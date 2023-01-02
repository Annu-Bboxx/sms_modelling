#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# -*- coding: utf-8 -*-
import os
import pandas
import psycopg2
from src.utils.utils import get_logger


def pull_raw_data(data_query_string):
    """ Function that queries the dhw to extract raw training data
    Args:
        data_query_string (string) string containing the sql query that will be parsed
        version_name (string) version name to persist the data in csv format

    Returns:
        pull_raw_training_data: pandas DataFrame containing raw training data

     """
    # logging
    logger = get_logger('model')

    # get env variables
    logger.info('retrieving DWH credentials')
    host_name = os.getenv('HOST_NAME')
    port_ = os.getenv('PORT')
    database_name = os.getenv('DATABASE_NAME')
    username_ = os.getenv('USERNAME')
    password_ = os.getenv('PASSWORD')
    uri = "redshift://annu:AKIA654d894d14d5e$@redshift-prod.bboxx-dwh.co.uk:5439/bboxx"
    # create connection string
    dwh_credentials_str = "host={} port={} dbname={} user={} password={}"         .format(host_name, port_, database_name, username_, password_)

    # invoke connection
    logger.info('connecting to DWH')
    dwh_connection = psycopg2.connect(dwh_credentials_str)

    # query the dwh
    logger.info('extracting raw data from dwh')
    raw_df = pandas.read_sql_query(uri, dwh_connection)
    logger.info('data size: {}'.format(len(raw_df)))

    # close connection
    dwh_connection.close()

    return raw_df

