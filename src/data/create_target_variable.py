#!/usr/bin/env python
# coding: utf-8

# In[17]:


import pandas as pd
import numpy
import sys
sys.path.insert(0, '/Users/annukajla/Documents/sms_modelling/src')
from utils.utils import get_logger
def create_target_variable(dataframe):
    """ Function to create target variable which model will predict
        Arguments: Dataframe
        Returns: Return dataframe with target column
    """
#     logging
    logger = get_logger('model')
    logger.info('creating target variable')
#  condition for paid and not paid customer
    midnight = (dataframe["msg_creation_date"]+pd.Timedelta(days=1)).dt.normalize()
    num_of_hours=(midnight-dataframe['msg_creation_date'])/pd.Timedelta(hours=1)
#   creating target column and assigning paid/not paid values  
    dataframe.loc[((dataframe['after_msg_pay_date']<=(dataframe['msg_creation_date'] +pd.to_timedelta(num_of_hours, unit='h')+pd.Timedelta(days=3)))), 'target']='paid'
    dataframe.loc[(dataframe['after_msg_pay_date']>dataframe['msg_creation_date'] +pd.to_timedelta(num_of_hours, unit='h')+pd.Timedelta(days=3)), 'target']='not paid'
    
    class_1=round(dataframe['target'].value_counts(normalize=True)[0]*100,2)
    class_0=round(dataframe['target'].value_counts(normalize=True)[1]*100,2)
    logger.info('class 1: {}%, class 0: {}%'.format(class_1, class_0))
    
    return dataframe


# In[ ]:





# In[ ]:




