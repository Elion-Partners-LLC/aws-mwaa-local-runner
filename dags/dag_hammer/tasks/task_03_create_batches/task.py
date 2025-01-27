from airflow.models import Variable
from airflow.operators.python import PythonOperator


def _create_batches(ti):
    batches_filenames = ti.xcom_pull(task_ids="list_batch_files")
    batches_filenames = [
        filename.split("/")[-1].replace(".csv", "") for filename in batches_filenames
    ]
    Variable.set(
        key="hammer_batches_filenames", value=batches_filenames, serialize_json=True
    )


def create_task():
    task = PythonOperator(task_id="create_batches", python_callable=_create_batches)
    return task
