from pickle import dump
import os
import sys
# sys.path.insert(5, '/Users/annukajla/Documents/sms_modelling/src')
from src.utils.utils import get_logger


def persist_model(versioning_name, model_object):
    """ function to persist model using pickle dump

    Args:
        versioning_name (string): name of the type of model e.g. 'light_gbm'
        model_object (sklearn object) fitted sklearn model object

    """

    # logging
    logger = get_logger('model')
    logger.info('persisting model object')

    # create complete file path to persist model
    full_file_path = os.path.join('models', versioning_name, 'trained_model') + '.pkl'

    # persist
    dump(model_object, open(full_file_path, 'wb'))
    logger.info('model persisted to {}'.format(full_file_path))