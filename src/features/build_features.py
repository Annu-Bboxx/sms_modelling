#!/usr/bin/env python
# coding: utf-8

# In[2]:
import importlib

import pandas as pd
import sys
sys.path.insert(1, '/Users/annukajla/Documents/sms_modelling/src')
# from data.pull_payment_data import pull_payment_data
from utils.utils import get_logger
from utils.utils import read_yaml
def build_features(dataframe, features_list, training):
    """ Function to extract feature used in the model
    Args:
        dataframe (pandas DataFrame)
        features_list (list) list with features that will be used for training
        training (bool): boolean defining whether building features for training or prediction
    Returns:
        build_features: pandas DataFrame with the final set of model features"""
        
    logger = get_logger('model')
    logger.info('building features')
    
    # adding age feature     
    dataframe["customer_birth_date"] = pd.to_datetime(dataframe["customer_birth_date"], errors = 'coerce') #changing date of birth data type 
    today = pd.to_datetime('now')
    dataframe['age']=(today.year - dataframe["customer_birth_date"].dt.year) - ((today.month - dataframe["customer_birth_date"].dt.month) < 0)
    # adding how old customer is with bboxx feature
    if training :
        dataframe["customer_active_end_date"] = pd.to_datetime(dataframe["customer_active_end_date"], errors = 'coerce')
        dataframe["customer_active_start_date"] = pd.to_datetime(dataframe["customer_active_start_date"], errors = 'coerce')
        dataframe["msg_creation_date"]=pd.to_datetime(dataframe["msg_creation_date"], errors = 'coerce')
        dataframe.loc[(dataframe["customer_active_end_date"].notnull()) & (dataframe["customer_active_end_date"]>dataframe["msg_creation_date"]),"days_customer_in_bbox"]=(dataframe["msg_creation_date"]-dataframe["customer_active_start_date"]).dt.days
        dataframe.loc[(dataframe["customer_active_end_date"].notnull()) & (dataframe["customer_active_end_date"]<dataframe["msg_creation_date"]),"days_customer_in_bbox"]=(dataframe["customer_active_end_date"].dt.date-dataframe["customer_active_start_date"].dt.date).dt.days
        dataframe.loc[dataframe["customer_active_end_date"].isnull(),"days_customer_in_bbox"]=(dataframe["msg_creation_date"].dt.date - dataframe["customer_active_start_date"].dt.date).dt.days
#      add total no. of payments feature
#
#     config_path = './configs/train_model.yaml'
#     config_parameters = read_yaml(config_path)
#     total_payment_query = config_parameters['payment_query']
#     schema = config_parameters['schema']
#     module = importlib.import_module('Queries.{}'.format(total_payment_query))
#     df_payment= pull_payment_data(module.df_payment.format(schema))
#     pay_msg_df=dataframe.merge(df_payment,on='customer_id',how='inner')
#     new_pay_msg_df=pay_msg_df[pay_msg_df['msg_creation_date']>=pay_msg_df['pay_timestamp']]
#     Total_no_of_payments=new_pay_msg_df.groupby('customer_id')['pay_timestamp'].count().reset_index(name='Total_no_of_payments')
#     dataframe=dataframe.merge(Total_no_of_payments,how='left',on='customer_id')
#   Payment frequency
#     average_pay_df=new_pay_msg_df.groupby('customer_id')['paid_amount'].mean().reset_index(name='average_payment')
#     average_daily_rate=new_pay_msg_df.groupby('customer_id')['daily_rate'].mean().reset_index(name='mean_daily_rate')
#     df_pay_freq = average_pay_df.merge(average_daily_rate,on='customer_id', how='left')
#     df_pay_freq['payment_frequency']=df_pay_freq['average_payment']/df_pay_freq['mean_daily_rate']
#     payment_frequency_df=df_pay_freq[['customer_id','payment_frequency']].copy()
#     dataframe = pd.merge(dataframe,payment_frequency_df,on='customer_id', how='left')
#     previous status feature

    if training is False:
        # for prediction, creating past messages response feature
        midnight = (dataframe["msg_creation_date"] + pd.Timedelta(days=1)).dt.normalize()
        num_of_hours = (midnight - dataframe['msg_creation_date']) / pd.Timedelta(hours=1)
        dataframe.loc[(dataframe['pay_date'] <= (dataframe['msg_creation_date'] + pd.to_timedelta(num_of_hours, unit='h') + pd.Timedelta(days=3))), 'Previous_Pay_Status'] = 1
        dataframe.loc[(dataframe['pay_date'] > dataframe['msg_creation_date'] + pd.to_timedelta(num_of_hours,unit='h') + pd.Timedelta(days=3)), 'Previous_Pay_Status'] = 0
    #     how long customer has been in bboxx feature
        dataframe["customer_active_start_date"] = pd.to_datetime(dataframe["customer_active_start_date"],errors='coerce')
        dataframe["days_customer_in_bbox"] = (today - dataframe["customer_active_start_date"]).dt.days
    if training:
        df_previous_msg = dataframe[['customer_id', 'msg_creation_date', 'target']].copy()
        df_previous_msg = df_previous_msg.sort_values(by=['customer_id', 'msg_creation_date'], ascending=[True, True])
        df_previous_msg[['Previous_target', 'previous_msg_date']] = df_previous_msg.groupby(['customer_id'])[
            'target', 'msg_creation_date'].shift(1)
        df_previous_msg.loc[df_previous_msg['Previous_target'] == 'paid', 'Previous_Pay_Status'] = 1
        df_previous_msg.loc[df_previous_msg['Previous_target'] == 'not paid', 'Previous_Pay_Status'] = 0
        df_previous_status = df_previous_msg[['customer_id', 'Previous_Pay_Status', 'msg_creation_date']]
        dataframe = dataframe.merge(df_previous_status, on=["customer_id", "msg_creation_date"], how='left')
        logger.info('number of train features: {}'.format(len(features_list)))
        features_list = features_list.copy()  # avoid list mutability outside the function
        features_list.append('target')
        
    return dataframe[features_list]


# In[ ]:




