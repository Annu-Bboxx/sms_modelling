import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(1, '/Users/annukajla/Documents/sms_modelling/src')
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import make_scorer, fbeta_score
from sklearn.model_selection import RandomizedSearchCV
from utils.utils import read_yaml
from utils.utils import convert_numpy_to_native
from utils.utils import get_logger
from utils.utils import invoke_algorithm
import numpy


def tune_model(model_type, features, target, n_combinations, folds, beta, seed):
    """ function to load the given data file, and tune hyperparameters of a model type
    Args:
        model_type (string) string containing the name of the model as they appear in yaml files
        features (pandas DataFrame) dataframe with the processed features for training
        target (numpy array) with target variable
        n_combinations (integer) Number of random parameter combinations to be evaluated during RandomizedSearchCV
        folds (integer) Number of folds for cross validation
        beta (float) Harmoning mean between precision and recall
        seed (integer) set seed for reproducibility
    Return:
        dictionary: hyperparameter names(keys) and their tuned values(values)
    """
    # logging
    logger = get_logger('model')
    logger.info('starting {} model hyperparameter tuning'.format(model_type))

    # invoke classifier
    binary_classifier = invoke_algorithm(model_type)

    # load hyperparameter grid space
    hyperparameters_grid_space = eval(read_yaml('configs/random_search_parameters.yaml')[model_type])

    # setup CV parameters
    n_jobs = -1
    verbose = 1

    # metric for cv
    ftwo_scorer = make_scorer(fbeta_score, beta=beta)

    # invoke stratified k-folds for cv iterations
    stratified_kfolds = StratifiedKFold(n_splits=folds, random_state=seed, shuffle=True)

    # invoke random cv
    random_cv = RandomizedSearchCV(estimator=binary_classifier,
                                   n_iter=n_combinations,
                                   n_jobs=n_jobs,
                                   cv=stratified_kfolds,
                                   param_distributions=hyperparameters_grid_space,
                                   random_state=seed,
                                   scoring=ftwo_scorer,
                                   verbose=verbose)

    # iterate through k-folds in order to up-sample only train data during cv
    random_cv.fit(features, target)  # applying smote only on train
    best_params = random_cv.best_params_
    best_params = convert_numpy_to_native(best_params)

    return best_params