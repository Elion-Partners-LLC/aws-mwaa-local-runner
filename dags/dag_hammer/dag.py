import elion.dag_tags as tags
from airflow.models import DAG, Variable
from airflow.utils.dates import days_ago
from airflow.utils.task_group import TaskGroup
from dag_hammer.tasks.task_01_get_property_batches.task import (
    create_task as task_01_get_property_batches,
)
from dag_hammer.tasks.task_02_list_batch_files.task import (
    create_task as task_02_list_batch_files,
)
from dag_hammer.tasks.task_03_create_batches.task import (
    create_task as task_03_create_batches,
)
from dag_hammer.tasks.task_04_download_hammer_data.task import (
    create_task as task_04_download_hammer_data,
)
from dag_hammer.tasks.task_05_s3_to_redshift.task import (
    create_task as task_05_s3_to_redshift,
)
from dag_hammer.tasks.task_06_create_dbt_snapshot.task import (
    create_task as task_06_create_dbt_snapshot,
)

default_args = {
    "owner": "Wilmer Montilla",
    "params": {
        "all_properties": False,
        "batch_size": 50,
    },
}

with DAG(
    dag_id="hammer_dag",
    description=(
        "Trigger and event once a year to get all the data for the hammer "
        "app and load raw tables to the data Warehouse"
    ),
    default_args=default_args,
    tags=[tags.EXTRACT_LOAD],
    start_date=days_ago(1),
    catchup=False,
    schedule_interval="@daily",
    max_active_tasks=5,
    max_active_runs=1,
) as dag:

    t1_get_property_batches = task_01_get_property_batches()
    t2_list_batch_files = task_02_list_batch_files()
    t3_create_batches = task_03_create_batches()
    t6_create_dbt_snapshot = task_06_create_dbt_snapshot()

    batches = Variable.get(
        "hammer_batches_filenames", default_var=["default_batch"], deserialize_json=True
    )

    # Create the dynamic tasks from that Variable
    with TaskGroup("batches", prefix_group_id=False) as batches_group:
        if batches:
            for i, batch in enumerate(batches):
                t4_download_hammer_data = task_04_download_hammer_data(batch)
                # Put the data in the DW as soon as it is downloaded
                if i > 0:
                    t5_s3_to_redshift >> t4_download_hammer_data
                t5_s3_to_redshift = task_05_s3_to_redshift(batch)
                t4_download_hammer_data >> t5_s3_to_redshift

    (
        t1_get_property_batches
        >> t2_list_batch_files
        >> t3_create_batches
        >> batches_group
        >> t6_create_dbt_snapshot
    )
