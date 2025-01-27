import logging
import os
from io import StringIO

import boto3
import pandas as pd
import redshift_connector
from constants import (
    ALL_PROPERTIES,
    BATCH_NUMBER,
    BATCH_S3_KEY_TEMPLATE,
    CONTAINER_DOWNLOAD_PATH,
    DATA_LAKE_S3_BUCKET_NAME,
    HAMMER_DATA_S3_KEY,
    RUN_DATE,
    TEMP_DATA_STORE_S3_BUCKET_NAME,
)
from urllib3.util.url import parse_url

logger = logging.getLogger()


def get_properties_from_s3():
    object_name = BATCH_S3_KEY_TEMPLATE.format(
        today=RUN_DATE, batch_number=BATCH_NUMBER
    )
    file_name = os.path.join(CONTAINER_DOWNLOAD_PATH, "batch_info.csv")

    s3 = boto3.client("s3")
    s3.download_file(TEMP_DATA_STORE_S3_BUCKET_NAME, object_name, file_name)

    df = pd.read_csv(file_name)
    return df


def get_secret_string(secrets, secret_id: str):
    """Function to get a secret string given a secret ID"""
    return secrets.get_secret_value(SecretId=secret_id)["SecretString"]


def upload_to_s3():
    client = boto3.client("s3")
    buffer = StringIO()
    key = HAMMER_DATA_S3_KEY.format(today=RUN_DATE, batch_number=BATCH_NUMBER)

    try:
        logger.info("Uploading data to S3")
        client.upload_file(
            os.path.join(CONTAINER_DOWNLOAD_PATH, "data.csv"),
            DATA_LAKE_S3_BUCKET_NAME,
            key,
        )
    except Exception as e:
        logger.error(e)
