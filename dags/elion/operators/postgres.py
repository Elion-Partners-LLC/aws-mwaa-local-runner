from airflow.models import BaseOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook


class PostgresOperator(BaseOperator):
    def __init__(
        self,
        postgres_conn_id_location,
        query,
        *args,
        **kwargs,
    ):
        """
        Operator class to execute a query in a PostgreSQL database.

        :param postgres_conn_id_location: The ID of the PostgreSQL connection to be used for establishing the connection with the database this connection is the connection store in the secret without the prefix of airflow/connections/.
        :type postgres_conn_id_location: str
        :param query: The SQL query to be executed in the database.
        :type query: str
        """
        super().__init__(*args, **kwargs)
        self.query = query
        self.postgres_conn_id_location = postgres_conn_id_location

    def execute(self, context):
        # Connect with PostgreSQL database
        postgres_conn_id = self.postgres_conn_id_location
        postgres_hook = PostgresHook(postgres_conn_id=postgres_conn_id)

        # Execute the query
        postgres_hook.run(self.query)
