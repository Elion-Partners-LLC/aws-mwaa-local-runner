from typing import Sequence

from airflow.providers.amazon.aws.transfers.s3_to_sftp import S3ToSFTPOperator


class S3ToSFTPOperatorCustom(S3ToSFTPOperator):

    template_fields: Sequence[str] = ("s3_key", "sftp_path", "s3_bucket")
