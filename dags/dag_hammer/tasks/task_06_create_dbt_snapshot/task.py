from airflow.providers.dbt.cloud.operators.dbt import DbtCloudRunJobOperator
from airflow.utils.trigger_rule import TriggerRule

SNAPSHOT_JOB_ID = 366364


def create_task():
    task = DbtCloudRunJobOperator(
        task_id="create_dbt_snapshot",
        job_id=SNAPSHOT_JOB_ID,
        check_interval=10,
        timeout=300,
        trigger_rule=TriggerRule.ALL_DONE,
    )

    return task
