#!/usr/bin/env python
# coding: utf-8

# In[3]:
import sys
import os

os.chdir( r'/Users/annukajla/Documents/sms_modelling' )
# sys.path.insert(1, '/Users/annukajla/Documents/sms_modelling/src/data')
print("current directory",os.getcwd())
sys.path.append(os.path.abspath(os.curdir))
print("current directory",os.getcwd())
import importlib
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import fbeta_score
from dotenv import find_dotenv, load_dotenv
from src.data.pull_raw_data import pull_raw_data
# from src.data.handle_outliers import handle_outliers
from src.data.handle_missing_values import handle_missing_values
from src.features.build_features import build_features
from src.data.create_target_variable import create_target_variable
from src.data.encode_categorical_features import encode_categorical_features
from src.models.train import train_model
from src.models.tune_model import tune_model
from src.utils.utils import persist_versions
from src.utils.persist_training_components import persist_training_components
from src.utils.utils import init_logger
from src.utils.utils import version_name_available
from src.utils.utils import optimal_threshold
from src.utils.utils import probabilities_to_binary
from src.utils.utils import read_yaml
from datetime import datetime
import pandas
import numpy
import warnings


def main():
    # invoke pipeline logger
    main_logger = init_logger('model')
     # set train date
    train_date = datetime.today().strftime('%Y-%m-%d')
    # load config parameters needed for training
    config_path = './configs/train_model.yaml'
    config_parameters = read_yaml(config_path)
    # check if model_id is available. The model_type + version combination should be unique
    
    version = config_parameters['version']
    mt = config_parameters['model_type']
    model_id = persist_versions([mt, version])
    # version_name_available(model_id)
    # create folder for storing model
    os.makedirs('models/' + model_id)

    # extract only features(keys) that their value is True in train_model yml config file
    # features_list=[]
    available_features_dict = config_parameters['model_features']
    features_list = list(filter(available_features_dict.get, available_features_dict))
    print("features_list :",features_list)
    # extract raw data for DWH
    train_query_file = config_parameters['train_query']
    schema = config_parameters['schema']
    # assign categorical encoder
    encoder_type = config_parameters['encoder_type']
    module = importlib.import_module('Queries.{}'.format(train_query_file))
    raw_train_data = pull_raw_data(module.msg_df.format(schema))
    # build train data with chain pipe
    train_data = raw_train_data \
        .pipe(create_target_variable)\
        .pipe(build_features, features_list=features_list, training=True)\
        .pipe(handle_missing_values, features_list=features_list) \
        .pipe(encode_categorical_features, model_type=mt, encoder_type=encoder_type, version=version)


    main_logger.info('final train size: {}'.format(train_data.shape[0]))
    # TODO explore adding data filters to avoid e.g. gender == 'Company'

    # load train/cv parameters
    seed = config_parameters['seed']
    beta = config_parameters['beta']
    cv_combinations = config_parameters['cv_parameters']['combinations']
    outer_folds = config_parameters['cv_parameters']['outer_folds']
    inner_folds = config_parameters['cv_parameters']['inner_folds']

    # invoke stratified k-folds for outer cv
    outer_stratified_kfolds = StratifiedKFold(n_splits=outer_folds, random_state=seed, shuffle=True)
    features = train_data.drop(['target'], axis=1)
    target = train_data['target']

    # store results from each fold
    outer_cv_scores = []
    outer_cv_ots = []
    # outer_good_prospects_frequency = []
    outer_cv_aggregate_results = {}

    # outer cv to evaluate the training method end-to-end. It's critical since single train/test split unstable
    main_logger.info('staring outer cv..')
    for train_idx, test_idx in outer_stratified_kfolds.split(features, target):
        X_train_cv = features.iloc[train_idx]
        X_test_cv = features.iloc[test_idx]
        y_train_cv = target.iloc[train_idx]
        y_test_cv = target.iloc[test_idx]
        # X_resampled, y_resampled = os.fit_resample(X_train_cv, y_train_cv)
        # ftwo_scorer = make_scorer(fbeta_score, beta=beta)
        # cv to tuning
        # tune hyperparameters
        tuned_hyperparameters = tune_model(mt, X_train_cv, y_train_cv,int(cv_combinations), inner_folds, beta,seed)

        classifier = train_model(mt, X_train_cv, y_train_cv, tuned_hyperparameters)

        # outer_cv_params.append(random_cv.best_params_)
        #     print(y_resampled.value_counts())
        # train model with best params
        # lgbm_binary_clf.set_params(**random_cv.best_params_)
        # lgbm_binary_clf.fit(X_resampled, y_resampled)

        # predict on testset
        y_hat = classifier.predict(X_test_cv)
        target_test_predicted_proba = classifier.predict_proba(X_test_cv)[:, 1]

        # tune threshold
        ot = optimal_threshold(y_test_cv, target_test_predicted_proba, beta=beta)
        outer_cv_ots.append(ot)

        # convert to probabilities and score
        y_test_pred = probabilities_to_binary(target_test_predicted_proba, ot)
        score = fbeta_score(y_test_cv, y_test_pred, beta=beta).round(2)
        outer_cv_scores.append(score)
        # F1_score = f1_score(y_test_cv,y_hat,average='weighted')
        # outer_cv_scores.append(F1_score)
        print(outer_cv_scores, ot)

        # aggregate outer cv results in order to assess variance of the training strategy
    outer_cv_aggregate_results['f-score_mean'] = round(numpy.mean(outer_cv_scores), 2)
    outer_cv_aggregate_results['f-score_stdev'] = round(numpy.std(outer_cv_scores), 2)
    outer_cv_aggregate_results['optimal_threshold_mean'] = round(numpy.mean(outer_cv_ots), 2)
    outer_cv_aggregate_results['optimal_threshold_stdev'] = round(numpy.std(outer_cv_ots), 2)
    # outer_cv_aggregate_results['good_prospect_frequency_mean'] = round(numpy.mean(outer_good_prospects_frequency),
    #                                                                    2)
    # outer_cv_aggregate_results['good_prospect_frequency_stdev'] = round(numpy.std(outer_good_prospects_frequency),
    #                                                                     2)
    # tune hyperparameters
    main_logger.info('starting final cv..')
    tuned_hyperparameters = tune_model(mt, features, target, int(cv_combinations), inner_folds, beta, seed)

    # train model using best hp on entire data
    final_classifier = train_model(mt, features, target, tuned_hyperparameters)

    # predict using testset
    predicted_probabilities = final_classifier.predict_proba(features)[:, 1]

    # find the optimal threshold using auc precision-recall curve (only on test set!)
    optimal_binary_threshold = round(optimal_threshold(target, predicted_probabilities, beta=beta), 3)
    main_logger.info('The optimal threshold is: {}'.format(optimal_binary_threshold))
    predicted_classes = probabilities_to_binary(predicted_probabilities, optimal_binary_threshold)
    # score
    total_score = round(fbeta_score(target, predicted_classes, beta=beta),3)
    main_logger.info('The final F-beta Score is: {}'.format(total_score))
    meta_data = {'model_version': model_id,
                 'description': config_parameters['description'],
                 'data': persist_versions([model_id, schema, train_date, 'train_data.csv']),
                 'beta': beta,
                 'production': bool(config_parameters['production']),
                 'date': train_date,
                 'schema': schema,
                 'outer_cv_agg_results': outer_cv_aggregate_results,
                 'optimal_threshold': optimal_binary_threshold,
                 'hyperparameters': tuned_hyperparameters,
                 'features': features_list,
                 'train_query': train_query_file,
                 # 'predict_query': config_parameters['predict_query']
                 }

    # persist all the components of the model: model object, raw data, processed data, meta data etc.
    persist_training_components(mt, version, final_classifier, schema,train_date, raw_train_data, train_data,tuned_hyperparameters, meta_data)


if __name__ == '__main__':

    warnings.filterwarnings("ignore")
    logger = init_logger(__name__)
    logger.info('starting train model pipeline..')
    load_dotenv(find_dotenv())
    main()


# In[ ]:




