#!/usr/bin/env python
# coding: utf-8

# In[ ]:
import sys
sys.path.insert(0, '/Users/annukajla/Documents/sms_modelling/src')
from utils.utils import get_logger
import numpy


def handle_missing_values(dataframe,features_list):
    """
    This Function handles the missing values
    Arguments: Dataframe and list of features
    Returns:dataframe with no missing value in it
    """
    
#     logging
    logger = get_logger('model')
    logger.info('handling missing values')
#     handling missing values
    dataframe['daily_rate'].fillna(dataframe['daily_rate'].mean(), inplace=True)
    dataframe['utilisation_rate'].fillna(dataframe['utilisation_rate'].mean(), inplace=True)
    dataframe['balance_left'].fillna(dataframe['balance_left'].mean(), inplace=True)
    dataframe['age'].fillna(dataframe['age'].mean(), inplace=True)
    dataframe['days_customer_in_bbox'].fillna(dataframe['days_customer_in_bbox'].mean(), inplace=True)
    dataframe['payment_frequency'].fillna(dataframe['payment_frequency'].mean(), inplace=True)
    dataframe['enable_ontime_used'].fillna(dataframe['enable_ontime_used'].mean(), inplace=True)
    dataframe['bonus_no_cash_ontime_used'].fillna(dataframe['bonus_no_cash_ontime_used'].mean(), inplace=True)
    dataframe['Previous_Pay_Status'] = dataframe['Previous_Pay_Status'].fillna(-1)
    dataframe['bundle_ontime_used'].fillna(dataframe['bundle_ontime_used'].mean(), inplace=True)

#     raise missing value error
    if dataframe.isnull().values.any():
        columns_with_missing_values = list(dataframe.columns[dataframe.isnull().any()])

        # find the intersection between features of interest and features with missing values and flag them
        missing_values_from_selected_features = list(set(features_list).intersection(set(columns_with_missing_values)))
        if len(missing_values_from_selected_features) > 0:
            print(dataframe[missing_values_from_selected_features])
            missing_values_error_msg = 'missing values detected in columns: {}'\
                .format(','.join(missing_values_from_selected_features))
            logger.error(missing_values_error_msg)
            raise ValueError(missing_values_error_msg)
            
    return dataframe

