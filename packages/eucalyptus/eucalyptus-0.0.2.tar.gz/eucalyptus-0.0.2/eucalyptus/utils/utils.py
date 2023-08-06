import numpy as np
import pandas as pd
import requests
from eucalyptus.config import BASE_API_URL
from eucalyptus.config import get_api_headers
import pandera as pa
import re


def log_training_data_from_pandas_simpler(model_name, model_version, features, labels):
    if isinstance(features, pd.DataFrame) and (isinstance(labels, pd.Series) or isinstance(labels, pd.DataFrame)):
        training_data_distribution = []

        for column in features:
            column_name = column.lower()
            column_name = column_name.strip()
            column_name = re.sub(r'\W+', ' ', column_name)
            column_name = "_".join(column_name.split())
            num_unique_values = len(features[column].unique())
            if num_unique_values <= 10:
                value_counts = features[column].value_counts()
                training_bins = []
                training_hist = []

                for index, value in value_counts.items():
                    training_bins.append(index)
                    training_hist.append(value)

                histogram_info = {"training_hist": training_hist,
                                  "training_bins": training_bins}
                training_data_distribution.append({column_name: histogram_info, "feature_type": "categorical"})

            else:
                min_training = features[column].values.min()
                max_training = features[column].values.max()

                step = (max_training - min_training) / 10
                step = round(step, 2)

                training_hist, training_bins = np.histogram(features[column].values,
                                                            bins=np.arange(min_training,
                                                                           max_training + step,
                                                                           step))

                training_hist = np.around(training_hist, 2).tolist()
                training_bins = np.around(training_bins, 2).tolist()

                histogram_info = {"training_hist": training_hist,
                                  "training_bins": training_bins, "min_training": min_training,
                                  "max_training": max_training}

                training_data_distribution.append({column_name: histogram_info, "feature_type": "continuous"})

        payload = {"model_name": model_name,
                   "model_version": model_version,
                   "training_data_distribution": training_data_distribution,
                }

        print(payload)

        response = requests.post(f'{BASE_API_URL}/uploadTrainingDataFromSDK',
                                 json=payload, headers=get_api_headers())
        return response.json()
    else:
        raise ValueError("features and labels must be pandas dataframes")


def infer_schema(features, labels):
    features_schema = pa.infer_schema(features)
    if isinstance(features_schema, pa.schemas.DataFrameSchema):
        features_schema = features_schema.dtypes
    else:
        features_schema = features_schema.dtype
    f_schema = []
    for key, value in features_schema.items():
        column_name = key.lower()
        column_name = column_name.strip()
        column_name = re.sub(r'\W+', ' ', column_name)
        column_name = "_".join(column_name.split())

        f_schema.append({"col_name": column_name, "col_type": value.__str__()})

    l_schema = []
    labels_schema = pa.infer_schema(labels)
    if isinstance(labels_schema, pa.schemas.SeriesSchema):
        schema = labels_schema.dtype
        label_column_name = labels_schema.name
        label_column_name = label_column_name.lower()
        label_column_name = label_column_name.strip()
        label_column_name = re.sub(r'\W+', ' ', label_column_name)
        label_column_name = "_".join(label_column_name.split())
        l_schema.append({"col_name": label_column_name, "col_type": str(schema)})

    else:
        labels_schema = labels_schema.dtypes
        for key, value in labels_schema.items():
            label_column_name = key.lower()
            label_column_name = label_column_name.strip()
            label_column_name = re.sub(r'\W+', ' ', label_column_name)
            label_column_name = "_".join(label_column_name.split())

            l_schema.append({"col_name": label_column_name, "col_type": value.__str__()})

    return f_schema, l_schema


def validate_model_name(name):
    model_name = name.strip()
    pattern = '^[a-z][a-z_]+[a-z]$'
    model_name = re.sub(r"\__+", "_", model_name)
    result = re.match(pattern, model_name)
    if result:
        return True
    else:
        return False

