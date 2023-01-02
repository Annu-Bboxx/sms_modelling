import os
import pandas
import psycopg2
import sys
print(os.getcwd())
sys.path.insert(0, '/Users/annukajla/Documents/sms_modelling/src')
from utils.utils import get_logger


def pull_payment_data(payment_query_string):
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
    # host_name = os.getenv('HOST_NAME')
    # port_ = os.getenv('PORT')
    # database_name = os.getenv('DATABASE_NAME')
    # username_ = os.getenv('USERNAME')
    # password_ = os.getenv('PASSWORD')
    # load_dotenv(find_dotenv())
    host_name = os.getenv('HOST_NAME')
    port_ = os.getenv('PORT')
    database_name = os.getenv('DATABASE_NAME')
    username_ = ''
    print(username_)
    username_ = os.getenv('DBUSER')
    print(os.getenv('DBUSER'))
    password_ = os.getenv('Password')

    # create connection string
    dwh_credentials_str = "host={} port={} dbname={} user={} password={}" \
        .format(host_name, port_, database_name, username_, password_)
    print(dwh_credentials_str)
    # invoke connection
    dwh_connection = psycopg2.connect(dwh_credentials_str, sslmode='prefer')
    # uri = "redshift://annu:AKIA654d894d14d5e$@redshift-prod.bboxx-dwh.co.uk:5439/bboxx"
    # create connection string

    # invoke connection
    logger.info('connecting to DWH')
    dwh_connection = psycopg2.connect(dwh_credentials_str)

    # query the dwh
    logger.info('extracting raw data from dwh')
    df_payment=pandas.read_sql_query(payment_query_string, dwh_connection)
    logger.info('data size: {}'.format(len(df_payment)))

    # close connection
    dwh_connection.close()

    return df_payment
