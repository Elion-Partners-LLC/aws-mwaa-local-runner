import logging
from io import BytesIO, StringIO

import pandas as pd
from python_calamine.pandas import pandas_monkeypatch

from .store_manager import StoreManager

logger = logging.getLogger()


class S3Manager(StoreManager):
    def __init__(self, client, bucket):
        self.client = client
        self.bucket = bucket

    def upload_file(self, source, key):
        """
        Uploads a file to an Amazon S3 bucket.

        Parameters:

        source (str): The path to the file to upload. This can be the name of the file if the file is in the same directory as the script, or a full path to the file.

        key (str): The name that the file will have once it is uploaded to the S3 bucket. This includes any directories that the file should be put in. For example, to upload a file to the root of the bucket, just use the filename as the key. To put the file in a directory, prepend the directory name to the filename (e.g., 'my_directory/my_file.txt').

        Returns:
        None

        """
        try:
            logger.info(f"Uploading {source} to {key} in {self.bucket}")
            self.client.upload_file(source, self.bucket, key)
        except Exception as e:
            logger.error(
                f"Failed to upload {source} to {key} in {self.bucket} with error: {e.message}"
            )

    def get_json_object_from_s3(self, key):
        """
        Retrieves a JSON object from an Amazon S3 bucket.

        Parameters:
        key (str): The key (i.e., the name) of the JSON object in the S3 bucket.

        Returns:
        The JSON object if it is successfully retrieved. If an error occurs during retrieval, an error message is logged and the method returns None.

        Raises:
        Exception: An error occurred when trying to retrieve the JSON object from the S3 bucket.
        """
        try:
            logger.info(
                f"Retrieving JSON object from s3 bucket {self.bucket} with key {key}"
            )
            s3_object = self.client.get_object(Bucket=self.bucket, Key=key)

            return BytesIO(s3_object["Body"].read())
        except Exception as e:
            logger.error(
                f"Failed to retrieve json from s3 bucket {self.bucket} witht he key {key} and exception {e.message}"
            )

    def upload_df(self, df, key, headers=True, separator=","):
        """
        Uploads a pandas DataFrame to an Amazon S3 bucket as a CSV file.

        Parameters:
        df (pd.DataFrame): The DataFrame to upload.

        key (str): The key (i.e., the name) that the CSV file will have in the S3 bucket.

        headers (bool, optional): If True, the CSV file will include the column headers from the DataFrame. Defaults to True.

        separator (str, optional): The character used to separate values in the CSV file. Defaults to ",".

        Returns:
        None

        Raises:
        Exception: An error occurred when trying to upload the DataFrame to the S3 bucket.
        """
        try:
            buffer = StringIO()
            df.to_csv(
                buffer,
                header=headers,
                index=False,
                sep=separator,
            )

            logger.info(
                f"Uploading DataFrame to S3 bucket {self.bucket} with key {key}"
            )
            self.client.put_object(Body=buffer.getvalue(), Bucket=self.bucket, Key=key)
        except Exception as e:
            logger.error(
                f"Failed to upload dataframe from s3 bucket {self.bucket} witht he key {key} and exception {e.message}"
            )

    def get_file_as_df(self, key, ext=".csv") -> pd.DataFrame:
        """
        Retrieves a file from an Amazon S3 bucket and loads it into a pandas DataFrame.

        Parameters:
        key (str): The key (i.e., the name) of the file in the S3 bucket.
        ext (str): The file extension indicating the format of the file. Available options are:
               - '.csv': for CSV files
               - '.xlsx': for Excel files
               - '.xls': for older Excel files (using the 'calamine' engine)

        Returns:
        pd.DataFrame: The DataFrame if the file is successfully retrieved and loaded. If an error occurs during retrieval or loading, an error message is logged and the method returns None.

        Raises:
        Exception: An error occurred when trying to retrieve the file from the S3 bucket or load it into a DataFrame.
        """
        try:
            logger.info(
                f"Retrieving file from s3 bucker: {self.bucket} with the key {key}"
            )
            s3_object = self.get_json_object_from_s3(key)

            # Mapping file extensions to pandas read functions
            read_functions = {
                ".csv": pd.read_csv,
                ".xlsx": pd.read_excel,
                ".xls": lambda obj: pd.read_excel(obj, engine="calamine"),
            }

            if ext in read_functions:
                if ext == ".xls":
                    pandas_monkeypatch()
                return read_functions[ext](s3_object)
            else:
                raise ValueError(f"Unsupported file extension: {ext}")

        except Exception as e:
            logger.error(
                f"Failed to retrieve dataframe from s3 key: {key} in the bucket {self.bucket} and error: {str(e)}"
            )
