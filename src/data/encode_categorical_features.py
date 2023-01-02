#!/usr/bin/env python
# coding: utf-8

# In[13]:


import os
import sys
# directory_path = os.path.abspath('/Users/annukajla/Documents/sms_modelling/src/utils')
sys.path.insert(1, '/Users/annukajla/Documents/sms_modelling/src')
from utils.utils import init_logger
from sklearn.preprocessing import LabelEncoder
def encode_categorical_features(dataframe,model_type=None, encoder_type=None, version=None, target_encoder=None):
    """
    function to convert categorical into numerical feature
    Arguments: dataframe
    Return: dataframe with all numerical features
    """
    # logging
    logger = init_logger(__name__)
    logger.info('encoding categorical features using target encoder')
    categorical_columns = dataframe.select_dtypes('object').columns
    logger.info('categorical columns found: {}'.format(','.join(categorical_columns)))
#     encoding

    labelencoder = LabelEncoder()
    dataframe['target']=dataframe['target'].map({'paid':1,'not paid':0})
    return dataframe


# In[6]:



# In[ ]:




