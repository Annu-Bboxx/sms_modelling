
import os
import sys
# sys.path.insert(1, '/Users/annukajla/Documents/sms_modelling/src/utils')
# sys.path.append(os.path.abspath(os.curdir))
from src.utils.utils import persist_meta_data
from src.utils.utils import persist_versions
from src.utils.persist_model import persist_model
from src.utils.persist_hyperparameters import persist_hyperparameter
from src.utils.utils import get_logger


def persist_training_components(model_type, version, final_classifier,
                                schema, train_date, raw_train_data,
                                train_data, hyperparameters_dictionary, meta_data):
    """ function to persist all the necessary training components
    Args:
        model_type (string): name of the type of model e.g. 'light_gbm'
        version (string): version of the model
        final_classifier (model object) trained classifier
        schema (string): name of DWH schema
        train_date (string) date of running train pipeline
        raw_train_data (dataframe): extract of raw data dump
        train_data (dataframe): extract of processed data used for modeling
        hyperparameters_dictionary (dictionary): dictionary with the tuned hp for the model
        meta_data (json): meta data training components
    """

    # logging
    logger = get_logger('model')
    logger.info('persisting training components')

    model_id = persist_versions([model_type, version])
    persist_model(model_id, final_classifier)
    versioning_data_name = persist_versions([model_id, schema, train_date, 'train_data.csv'])
    raw_train_data_path = os.path.join('data/raw', versioning_data_name)
    raw_train_data.to_csv(raw_train_data_path, index=False)

    train_data_path = os.path.join('data/processed', versioning_data_name)
    train_data.to_csv(train_data_path, index=True)

    train_data_path = os.path.join('data/train_aggregates', versioning_data_name)
    train_data_aggregate_stats = train_data.describe()
    train_data_aggregate_stats.to_csv(train_data_path)

    persist_hyperparameter(model_id, hyperparameters_dictionary)

    persist_meta_data(model_id, meta_data)