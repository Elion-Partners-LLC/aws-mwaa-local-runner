from airflow.providers.amazon.aws.operators.s3 import S3ListOperator


def create_task():
    task = S3ListOperator(
        task_id="list_batch_files",
        bucket="{{ var.value.temp_data_store_s3_bucket_name }}",
        prefix="hammer_batch/{{ ds }}/",
        delimiter="/",
        aws_conn_id="aws_default",
    )
    return task
