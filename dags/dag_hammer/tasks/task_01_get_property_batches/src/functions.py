import logging
import os
from datetime import date
from itertools import zip_longest

import boto3
import redshift_connector
from constants import (
    BATCH_S3_KEY_TEMPLATE,
    BATCH_SIZE,
    CONTAINER_DOWNLOAD_PATH,
    PROPERTY_QUERY,
    RUN_DATE,
    TEMP_DATA_STORE_S3_BUCKET_NAME,
)
from urllib3.util.url import parse_url

logger = logging.getLogger()


def _get_secret_string(secrets, secret_id: str):
    """Function to get a secret string given a secret ID"""
    return secrets.get_secret_value(SecretId=secret_id)["SecretString"]


def get_redshift_connection():
    """Return the redshift connection"""

    secrets = boto3.client("secretsmanager")
    db_url = _get_secret_string(
        secrets, "airflow/connections/data-warehouse-airflow-user-prod"
    )
    url = parse_url(db_url)
    database = url.path.replace("/", "")
    user, password = url.auth.split(":")

    logger.info("Connecting to Redshift")
    conn = redshift_connector.connect(
        host=url.host, database=database, user=user, password=password
    )
    return conn


def get_properties_from_redshift(conn):
    """Retrieve the list of properties to be used in the hammer query"""

    logger.info("Retrieving the properties")
    cursor = conn.cursor()
    cursor.execute(PROPERTY_QUERY)

    return cursor.fetch_dataframe()


def split_properties(properties):
    """Split the properties dataframe into batches according to BATCH_SIZE"""

    logger.info("Splitting the properties into batches")
    property_ids = properties.property_id.unique().tolist()
    batches = zip_longest(*(iter(property_ids),) * BATCH_SIZE)

    for i, batch in enumerate(batches):
        logger.info(f"Saving batch {i} into temp storage")
        df = properties.loc[properties["property_id"].isin(batch)]
        df.to_csv(os.path.join(CONTAINER_DOWNLOAD_PATH, f"{i}.csv"), index=False)


# TODO: This could change to another point of view, trying to create a custom function to allow upload multiple files into specific path
def upload_to_s3():
    client = boto3.client("s3")

    for filename in os.listdir(CONTAINER_DOWNLOAD_PATH):
        key = BATCH_S3_KEY_TEMPLATE.format(today=RUN_DATE, filename=filename)

        try:
            logger.info(f"Loading {filename} into {key}")
            client = boto3.client("s3")
            client.upload_file(
                os.path.join(CONTAINER_DOWNLOAD_PATH, filename),
                TEMP_DATA_STORE_S3_BUCKET_NAME,
                key,
            )
        except Exception as e:
            logger.error(e)
