from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING, Sequence

from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.amazon.aws.transfers.sftp_to_s3 import (
    SFTPToS3Operator as BaseSFTPToS3Operator,
)
from airflow.providers.ssh.hooks.ssh import SSHHook

if TYPE_CHECKING:
    from airflow.utils.context import Context


class SFTPToS3Operator(BaseSFTPToS3Operator):

    template_fields: Sequence[str] = ("s3_key", "sftp_path", "s3_bucket")

    def __init__(self, disabled_algorithms=None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.disabled_algorithms = disabled_algorithms

    def execute(self, context: "Context") -> None:
        self.s3_key = self.get_s3_key(self.s3_key)
        ssh_hook = SSHHook(
            ssh_conn_id=self.sftp_conn_id, disabled_algorithms=self.disabled_algorithms
        )
        s3_hook = S3Hook(self.s3_conn_id)

        sftp_client = ssh_hook.get_conn().open_sftp()

        if self.use_temp_file:
            with NamedTemporaryFile("w") as f:
                sftp_client.get(self.sftp_path, f.name)

                s3_hook.load_file(
                    filename=f.name,
                    key=self.s3_key,
                    bucket_name=self.s3_bucket,
                    replace=True,
                )
        else:
            with sftp_client.file(self.sftp_path, mode="rb") as data:
                s3_hook.get_conn().upload_fileobj(
                    data, self.s3_bucket, self.s3_key, Callback=self.log.info
                )
