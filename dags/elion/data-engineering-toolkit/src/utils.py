import logging
from io import StringIO

import boto3
import redshift_connector
from urllib3.util.url import parse_url

logger = logging.getLogger()


def _get_secret_string(secrets, secret_id: str):
    """Function to get a secret string given a secret ID"""
    return secrets.get_secret_value(SecretId=secret_id)["SecretString"]


def get_redshift_connection(s3_key):
    """Return the redshift connection"""

    secrets = boto3.client("secretsmanager")
    db_url = _get_secret_string(secrets, s3_key)
    url = parse_url(db_url)
    database = url.path.replace("/", "")
    user, password = url.auth.split(":")

    logger.info("Connecting to Redshift")
    conn = redshift_connector.connect(
        host=url.host, database=database, user=user, password=password
    )
    return conn


def upload_df_to_s3(df, bucket_name, key, header=False):
    logger.info(f"Uploading csv data to {key}")
    s3_client = boto3.client("s3")
    buffer = StringIO()
    df.to_csv(
        buffer,
        header=header,
        index=False,
        sep=",",
    )
    s3_client.put_object(Body=buffer.getvalue(), Bucket=bucket_name, Key=key)


def get_object_from_s3(bucket_name, key):
    s3_client = boto3.client("s3")
    s3_object = s3_client.get_object(Bucket=bucket_name, Key=key)
    return s3_object["Body"]
