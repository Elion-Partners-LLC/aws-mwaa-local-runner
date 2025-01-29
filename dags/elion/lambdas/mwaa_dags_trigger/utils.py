import base64
import json
import urllib

import boto3
import requests
from constants import DAG_FILE_MAPPING, MWAA_CLI_COMMAND, MWAA_ENV_NAME


def run_dag(dag_name, params, logger):
    client = boto3.client("mwaa")
    mwaa_cli_token = client.create_cli_token(Name=MWAA_ENV_NAME)
    mwaa_auth_token = f"Bearer {mwaa_cli_token['CliToken']}"
    mwaa_webserver_hostname = (
        f"https://{mwaa_cli_token['WebServerHostname']}/aws_mwaa/cli"
    )

    conf = json.dumps(params)
    raw_data = f"{MWAA_CLI_COMMAND} {dag_name} --conf '{conf}'"
    mwaa_response = requests.post(
        mwaa_webserver_hostname,
        headers={
            "Authorization": mwaa_auth_token,
            "Content-Type": "application/json",
        },
        data=raw_data,
    )

    mwaa_std_err_message = base64.b64decode(mwaa_response.json()["stderr"]).decode(
        "utf8"
    )
    mwaa_std_out_message = base64.b64decode(mwaa_response.json()["stdout"]).decode(
        "utf8"
    )

    logger.info(mwaa_response.status_code)
    logger.info(mwaa_std_err_message)
    logger.info(mwaa_std_out_message)
    return mwaa_response


def get_file_key(event):
    try:
        key = urllib.parse.unquote_plus(
            event["Records"][0]["s3"]["object"]["key"], encoding="utf-8"
        )
        return key
    except (KeyError, IndexError):
        return None


def make_file_params(file_key):
    return {"prefix": file_key}


def get_dag_name(file_key):
    for dag_name, file_prefix, file_suffix in DAG_FILE_MAPPING:
        if file_key.startswith(file_prefix) and file_key.endswith(file_suffix):
            return dag_name
    return None
