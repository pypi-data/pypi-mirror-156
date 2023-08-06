from eucalyptus.config import BASE_API_URL
from eucalyptus.config import get_api_headers
import json
import pandas as pd
import sys
import requests


def log_model_prediction(model_name, model_version, features, prediction):
    features = {k.lower(): v for k, v in features.items()}
    data = {"model_name": model_name, "model_version": str(model_version), "features": features, "prediction": prediction}
    response = requests.post(f'{BASE_API_URL}/logPrediction', json=data, headers=get_api_headers())


def log_model_actual(model_name, request_id, actual):
    if isinstance(request_id, pd.Series) and isinstance(actual, pd.Series):
        zipped_data = dict(zip(request_id, actual))
        # Check if the data is larger than 1 MB in size because that is the default limit
        if sys.getsizeof(zipped_data) >= pow(2, 20):
            raise Exception("The size of the data is too large, please send the data in smaller chunks")

        data = {"model_name": model_name, "data": zipped_data}
        response = requests.post(f'{BASE_API_URL}/logActual', json=data, headers=get_api_headers())

    elif isinstance(request_id, list) and isinstance(actual, list):
        zipped_data = dict(zip(request_id, actual))
        # Check if the data is larger than 1 MB in size because that is the default limit
        if sys.getsizeof(zipped_data) >= pow(2, 20):
            raise Exception("The size of the data is too large, please send the data in smaller chunks")

        data = {"model_name": model_name, "data": zipped_data}
        response = requests.post(f'{BASE_API_URL}/logActual', json=data, headers=get_api_headers())
    else:
        print("The arguments request_id and actual can ONLY accept a list or a pandas series object")


def create_new_model_version(model_name, new_version_name):
    data = {"model_name": model_name, "version": new_version_name}
    response = requests.post(f'{BASE_API_URL}/createNewModelVersion', json=data, headers=get_api_headers())

