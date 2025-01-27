from elion.operators.ecs import ECSOperator


def create_task():
    task = ECSOperator(
        task_id="get_property_batches",
        task_definition="get_property_batches",
        cluster="data_engineering",
        overrides={
            "containerOverrides": [
                {
                    "name": "get_property_batches",
                    "environment": [
                        {
                            "name": "ALL_PROPERTIES",
                            "value": "{{ params.all_properties }}",
                        },
                        {
                            "name": "BATCH_SIZE",
                            "value": "{{ params.batch_size }}",
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
    )
    return task
