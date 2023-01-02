import sys
import os
import pandas
from sqlalchemy import create_engine
import boto3
import importlib
from datetime import datetime
import click
os.chdir( r'/Users/annukajla/Documents/sms_modelling')
print("current directory",os.getcwd())
sys.path.append(os.path.abspath(os.curdir))
from dotenv import find_dotenv, load_dotenv
from src.data.pull_raw_data import pull_raw_data
from src.utils.predict import predict
from src.utils.utils import load_pickled_model
from src.utils.utils import find_production_version
from src.utils.utils import init_logger
from src.utils.utils import get_model_version_metadata
from src.utils.utils import persist_versions

from src.data.handle_missing_values import handle_missing_values
# from src.data.handle_outliers import handle_outliers
from src.features.build_features import build_features
import psycopg2

@click.command()
@click.option('-ngu', required=True, help='ngu to extract raw data from')
@click.option('-target', required=True, help='ngu to extract raw data from')
@click.option('-amv', '--alternative_model_version', required=False, help='use alternative to production model version')
def main(ngu,target, alternative_model_version=None):
    # invoke pipeline logger
    main_logger = init_logger('model')

    # set prediction date
    prediction_date = datetime.today().strftime('%Y-%m-%d')

    # load model metadata needed for predictions
    if not alternative_model_version:
        model_meta_data_dict = find_production_version()
    else:
        model_meta_data_dict = get_model_version_metadata(alternative_model_version)

    # fetch model version
    model_version = model_meta_data_dict['model_version']
    main_logger.info('production model found: {}'.format(model_version))

    # fetch prediction query
    predict_query_file = model_meta_data_dict['predict_query']
    print(predict_query_file)
    prediction_query_module = importlib.import_module('src.Queries.{}'.format(predict_query_file))
    print(prediction_query_module)
    # extract raw data from prediction
    raw_prediction_data = pull_raw_data(prediction_query_module.pred_query.format(ngu))

    # add date-of-execution as column
    raw_prediction_data['prediction_date'] = prediction_date

    # set list of features used in training
    features_list = model_meta_data_dict['features']
    print(features_list)
    # process raw data
    processed_prediction_data = raw_prediction_data \
        .pipe(build_features, features_list=features_list, training=False)\
        .pipe(handle_missing_values, features_list=features_list)


    # load pre-trained model
    classifier_file_path = os.path.join('models/{}'.format(model_version), 'trained_model')
    classifier = load_pickled_model(classifier_file_path)

    # get optimal threshold for classification
    optimal_threshold = model_meta_data_dict['optimal_threshold']

    # run predictions
    predicted_probabilities, predicted_classes = predict(classifier, processed_prediction_data, optimal_threshold)
    print(predicted_probabilities, predicted_classes)
    # link predictions back to features data
    processed_prediction_data['predicted_probability'] = predicted_probabilities.round(3)
    processed_prediction_data['predicted_class'] = predicted_classes
    class_one_predicted_pct = round(processed_prediction_data['predicted_class'].value_counts(normalize=True)[1], 2)
    class_zero_predicted_pct = round(processed_prediction_data['predicted_class'].value_counts(normalize=True)[0], 2)
    main_logger.info('predicted class one distribution: {}%'.format(class_one_predicted_pct * 100))
    main_logger.info('predicted class zero distribution: {}%'.format(class_zero_predicted_pct * 100))
    # create predictions final output with id and predictions data
    predictions_output = pandas.merge(raw_prediction_data.loc[:, ['customer_id', 'prediction_date']],
                                      processed_prediction_data.loc[:, ['predicted_probability', 'predicted_class']],
                                      left_index=True,
                                      right_index=True)


    # store predictions
    versioning_name = persist_versions([model_version, ngu, prediction_date])
    filename = str(model_version) + "" + str(ngu) + "" + str(prediction_date) + ".csv"

    # if target == 's3':
    #     print("in s3")
        # Save_data_to_S3(predictions_output, filename)
    # if target == 'dwh':
    #     Save_data_to_DWH_E(predictions_output_eligibile)
    #     Save_data_to_DWH_NE(predictions_output_not_eligibile)
    # if target == 'both':
    #     Save_data_to_DWH_E(predictions_output_eligibile)
    #     Save_data_to_DWH_NE(predictions_output_not_eligibile)
    #     #Save_data_to_S3(predictions_output, filename)
    # if target == 'none':
    #     print('Not pushing data to any source')
    if target == 'local':
         predictions_output.to_csv('data/predictions/{}'.format(filename))
    #


if __name__ == '__main__':
    load_dotenv(find_dotenv())
    main()