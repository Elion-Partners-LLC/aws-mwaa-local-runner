from classes.store_manager import StoreManager


class SecretsManager(StoreManager):
    def __init__(self, client):
        self.client = client

    def get_secret_string(self, secret_id, region_name):
        secrets = self.client("secretsmanager", region_name=region_name)
        return secrets.get_secret_value(SecretId=secret_id)["SecretString"]
