from airflow.providers.amazon.aws.transfers.s3_to_redshift import S3ToRedshiftOperator
from airflow.utils.trigger_rule import TriggerRule


def create_task(batch_number: int):
    task = S3ToRedshiftOperator(
        task_id=f"s3_to_redshift_hammer_data_{batch_number}",
        redshift_conn_id="data-warehouse-airflow-user-prod",
        schema="hammer",
        table="logistics_routes_latest",
        s3_bucket="{{ var.value.data_lake_s3_bucket_name }}",
        s3_key=f"processed/hammer_app/{{{{ ds }}}}/{batch_number}.csv",
        method="UPSERT",
        upsert_keys=["property_id", "market_name", "poi_name"],
        copy_options=[
            "FORMAT AS CSV",
            "DELIMITER ','",
            "DATEFORMAT 'yyyy-mm-dd'",
            "IGNOREHEADER 1",
        ],
        trigger_rule=TriggerRule.ALL_DONE,
    )
    return task
