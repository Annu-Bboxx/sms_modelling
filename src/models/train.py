import sys
sys.path.insert(1, '/Users/annukajla/Documents/sms_modelling/src')
from utils.utils import get_logger
from utils.utils import invoke_algorithm
import numpy


def train_model(model_type, features, target, hyperparameters_dict):
    """ function to load the giver data file, fit a model and return the model object

    Args:
        model_type (string) string containing the name of the model as they appear in yaml files
        features (pandas DataFrame) dataframe with the processed features for training
        target (numpy array) with target variable
        hyperparameters_dict(dictionary) dictionary with hyperparameters

    Return:
        dictionary: key is the model type and value is the model fitted object that will be used in prod

    """

    # logging
    logger = get_logger('model')
    logger.info('starting {} model training'.format(model_type))

    # invoke classifier
    binary_classifier = invoke_algorithm(model_type)

    # pass hyperparameters
    binary_classifier.set_params(**hyperparameters_dict)

    # train
    binary_classifier.fit(features, target)

    return binary_classifier