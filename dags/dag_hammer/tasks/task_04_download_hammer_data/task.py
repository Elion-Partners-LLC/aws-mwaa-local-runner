from airflow.utils.trigger_rule import TriggerRule
from elion.operators.ecs import ECSOperator


def create_task(batch_number):
    task = ECSOperator(
        task_id=f"download_hammer_data_{batch_number}",
        task_definition="download_hammer_data",
        cluster="data_engineering",
        overrides={
            "containerOverrides": [
                {
                    "name": "download_hammer_data",
                    "environment": [
                        {
                            "name": "BATCH_NUMBER",
                            "value": str(batch_number),
                        },
                        {
                            "name": "RUN_DATE",
                            "value": "{{ ds }}",
                        },
                    ],
                },
            ]
        },
        launch_type="FARGATE",
        network_configuration={
            "awsvpcConfiguration": {
                "securityGroups": ["{{ var.value.airflow_security_group }}"],
                "subnets": [
                    "{{ var.value.airflow_private_subnets.split(',')[0] }}",
                    "{{ var.value.airflow_private_subnets.split(',')[1] }}",
                ],
            },
        },
        trigger_rule=TriggerRule.ALL_DONE,
    )
    return task
