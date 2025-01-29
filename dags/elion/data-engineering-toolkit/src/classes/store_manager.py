from abc import ABC, abstractmethod


class StoreManager(ABC):
    @abstractmethod
    def __init__(self, client):
        self.client = client

    @abstractmethod
    def upload_file(self, source, key, bucket):
        pass
