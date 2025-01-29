from airflow.providers.amazon.aws.operators.ecs import (
    EcsRunTaskOperator as BaseECSOperator,
)


class ECSOperator(BaseECSOperator):

    template_fields = ("overrides", "network_configuration")
