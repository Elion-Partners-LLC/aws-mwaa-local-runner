import logging

from utils import get_dag_name, get_file_key, make_file_params, run_dag

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    file_key = get_file_key(event)

    if file_key is not None:
        dag_name = get_dag_name(file_key)
        params = make_file_params(file_key)
    else:
        dag_name = event.get("dag_name")
        params = event.get("params", {})

    if dag_name is not None:
        run_dag(dag_name, params, logger)
    else:
        logger.error("Dag name unresolved")
