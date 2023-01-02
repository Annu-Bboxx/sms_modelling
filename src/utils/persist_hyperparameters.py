import os
import sys
sys.path.insert(1, '/Users/annukajla/Documents/sms_modelling/src/utils')
from src.utils.utils import get_logger
from src.utils.utils import write_yaml


def persist_hyperparameter(versioning_name, hyperparameters_dictionary):
    """ function to persist model hyperparameters in yaml file

    Args:
        versioning_name (string): name of the type of model e.g. 'light_gbm'
        hyperparameters_dictionary (dictionary) dictionary with the tuned hyperparameters

    """

    # logging
    logger = get_logger('model')
    logger.info('persisting hyperparameters')

    # create complete file path to persist model
    full_file_path = os.path.join('models', versioning_name, 'hyperparameters')

    # persist
    write_yaml(hyperparameters_dictionary, full_file_path)
    logger.info('hyperparameters persisted to {}'.format(full_file_path))