import os

BASE_URL = "https://hammerapp.com/api/v1/routes/find"
CONTAINER_DOWNLOAD_PATH = "/usr/src/data/"
HAMMER_DATA_S3_KEY = "processed/hammer_app/{today}/{batch_number}.csv"
BATCH_S3_KEY_TEMPLATE = "hammer_batch/{today}/{batch_number}.csv"

# Environment variables
ALL_PROPERTIES = os.environ.get("ALL_PROPERTIES") == "True"
BATCH_NUMBER = os.environ.get("BATCH_NUMBER")
RUN_DATE = os.environ.get("RUN_DATE")
DATA_LAKE_S3_BUCKET_NAME = os.environ.get("DATA_LAKE_S3_BUCKET_NAME")
TEMP_DATA_STORE_S3_BUCKET_NAME = os.environ.get("TEMP_DATA_STORE_S3_BUCKET_NAME")
