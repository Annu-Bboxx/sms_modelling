#!/usr/bin/env python
# coding: utf-8

# In[ ]:
import io
import os
import sys
# sys.path.append(os.path.abspath(os.curdir))
from ruamel import yaml
from attrdict import AttrDict
import logging
import numpy
import random
import lightgbm
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_recall_curve
import json
from pickle import load


def get_logger(logger_name):
    return logging.getLogger(logger_name)


def invoke_algorithm(model_type):
    model_parameters_dict = read_yaml('configs/model_parameters.yaml')[model_type]
    if model_type == 'light_gbm':
        return lightgbm.LGBMClassifier(**model_parameters_dict)
    elif model_type == 'random_forest':
        return RandomForestClassifier(**model_parameters_dict)


def init_logger(name):
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)
    logger = logging.getLogger(name)

    # console handler for validation info
    ch_va = logging.StreamHandler(sys.stdout)
    ch_va.setLevel(logging.INFO)
    ch_va.setFormatter(fmt=logging.Formatter(fmt=log_fmt))

    # add the handlers to the logger
    logger.propagate = False
    logger.addHandler(ch_va)
    return logger


def load_pickled_model(full_file_path):
    if 'pkl' not in full_file_path:
        full_file_path = full_file_path + '.pkl'
    return load(open(full_file_path, 'rb'))


def read_json(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)


def write_json(dictionary_data, filepath):
    if '.json' not in filepath:
        filepath = filepath + '.json'
    with open(filepath, 'w') as f:
        json.dump(dictionary_data, f, indent=4)


def read_yaml(filepath):
    with open(filepath) as f:
        config = yaml.safe_load(f)
    return AttrDict(config)


def write_yaml(data, filepath):
    if '.yaml' not in filepath:
        filepath = filepath + '.yaml'
    with open(filepath, 'w') as outfile:
        yaml.dump(data, outfile, default_flow_style=False)


def persist_meta_data(model_version, meta_data):
    fixed_file_path = 'metadata/model_meta_data.json'

    if not (os.path.isfile(fixed_file_path)):
        print("Either file is missing or is not readable, creating file...")

        with io.open(os.path.join(fixed_file_path[:8], 'model_meta_data.json'), 'w') as db_file:
            print("directory name",fixed_file_path[:8])
            db_file.write(json.dumps(meta_data))

    else:
        print("else")
        meta_data_dict = read_json(fixed_file_path)
        print(meta_data_dict)
        if version_name_available(model_version):
            meta_data_dict['meta_data'][model_version] = meta_data
            write_json(meta_data_dict, fixed_file_path)


def persist_versions(versioning_name_lst):
    return '_'.join(versioning_name_lst)


def convert_bytes_to_gigabyte(size_in_bytes):
    return round(size_in_bytes/float(1 << 30), 2)


def get_model_version_metadata(model_version):
    return read_json('metadata/model_meta_data.json')['meta_data'][model_version]


def find_production_version():
    production_model = None
    meta_data_dictionary = read_json('metadata/model_meta_data.json')['meta_data']
    for model_meta_data in meta_data_dictionary:
        if meta_data_dictionary[model_meta_data]['production']:
            production_model = model_meta_data

    assert production_model, 'no record for production found. Change production in  model_meta_data or train new model'

    return meta_data_dictionary[production_model]


def optimal_threshold(y, y_hat, beta):
    precision, recall, thresholds = precision_recall_curve(y, y_hat)
    nonzero_idx = numpy.where((recall != 0) & (precision != 0))
    x = (beta * beta * precision[nonzero_idx] + recall[nonzero_idx])
    fscore = (beta * beta + 1) * precision[nonzero_idx] * recall[nonzero_idx] / x
    optimal_idx = numpy.argmax(fscore)
    return thresholds[optimal_idx]


def probabilities_to_binary(probabilities, threshold):
    return numpy.where(probabilities >= threshold, 1, 0)


def version_name_available(model_version):
    fixed_file_path = 'metadata/model_meta_data.json'
    meta_data_dict = read_json(fixed_file_path)
    if model_version in meta_data_dict['meta_data']:
        raise ValueError('{} already exists as key in meta_data dict.Choose different suffix'.format(model_version))
    else:
        return True

def convert_numpy_to_native(dictionary):
    for key_, value_ in dictionary.items():
        if type(value_).__module__ == numpy.__name__:
            dictionary[key_] = value_.item()
    return dictionary

