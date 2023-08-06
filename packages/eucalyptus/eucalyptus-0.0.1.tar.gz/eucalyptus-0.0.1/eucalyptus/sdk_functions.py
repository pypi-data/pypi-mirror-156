from eucalyptus.utils.model_logger import log_model_prediction, log_model_actual, create_new_model_version
from eucalyptus.utils.utils import log_training_data_from_pandas_simpler
from eucalyptus.config import get_api_headers
from eucalyptus.config import set_api_token
from eucalyptus.config import BASE_API_URL
from eucalyptus.utils.utils import infer_schema, validate_model_name
import requests


class bcolors:
    OK = '\033[92m' #GREEN
    WARNING = '\033[93m' #YELLOW
    FAIL = '\033[91m' #RED
    RESET = '\033[0m' #RESET COLOR


def initialize(api_token: str):
    set_api_token(api_token)
    print("api token set")


def create_new_model(model_name, model_version, model_type, features, labels):
    if not validate_model_name(model_name):
        print(bcolors.FAIL + "Error: Invalid model name. The model name can only contain lowercase letters with underscores" + bcolors.RESET)
        return
    feature_schema, label_schema = infer_schema(features, labels)
    data = {"model_name": model_name, "model_version": str(model_version), "model_type": model_type,
            "feature_schema": feature_schema, "label_schema": label_schema}
    response = requests.post(f'{BASE_API_URL}/registerNewModelSDK', json=data, headers=get_api_headers())
    response = response.json()
    if response['status'] != 200:
        print(bcolors.FAIL + response['msg'] + bcolors.RESET)
    else:
        print(response['msg'])


def create_new_version(model_name, new_version_name):
    create_new_model_version(model_name, new_version_name)


def log_prediction(model_name, model_version, features, prediction):
    log_model_prediction(model_name=model_name, model_version=model_version, features=features, prediction=prediction)


def log_actual(model_name, request_ids, actual):
    log_model_actual(model_name=model_name, request_id=request_ids, actual=actual)


def log_training_data(model_name, model_version, features, labels):
    log_training_data_from_pandas_simpler(model_name, model_version, features, labels)
