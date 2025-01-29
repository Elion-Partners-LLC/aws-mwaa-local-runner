import os
from typing import Any, Callable, Dict, List, Optional, Union

from airflow.exceptions import AirflowSkipException
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.utils.email import send_email
from botocore.exceptions import ClientError
from elion.operators.email import ElionEmailOperator


def always_attach(file):
    return True


class S3ToEmailOperator(ElionEmailOperator):
    """Get files from S3 and send an email with those files attached"""

    template_fields = ("to", "subject", "html_content", "files", "s3_bucket", "s3_keys")
    template_fields_renderers = {"html_content": "html"}
    template_ext = (".html",)
    ui_color = "#e6faf9"

    def __init__(
        self,
        to: Union[List[str], str],
        subject: str,
        html_content: str,
        s3_bucket: str,
        s3_keys: Union[List[str], str],
        attach_check: Callable[[str], bool] = always_attach,
        always_send: bool = False,
        mail_from: Optional[str] = None,
        cc: Optional[Union[List[str], str]] = None,
        bcc: Optional[Union[List[str], str]] = None,
        mime_subtype: str = "mixed",
        mime_charset: str = "utf-8",
        conn_id: Optional[str] = None,
        aws_conn_id: str = "aws_default",
        custom_headers: Optional[Dict[str, Any]] = None,
        verify: Optional[Union[bool, str]] = None,
        **kwargs,
    ) -> None:
        super().__init__(
            to=to,
            subject=subject,
            html_content=html_content,
            mail_from=mail_from,
            files=[],
            cc=cc,
            bcc=bcc,
            mime_subtype=mime_subtype,
            mime_charset=mime_charset,
            conn_id=conn_id,
            custom_headers=custom_headers,
            **kwargs,
        )
        self.aws_conn_id = aws_conn_id
        self.s3_bucket = s3_bucket
        self.s3_keys = [s3_keys] if type(s3_keys) is str else s3_keys
        self.attach_check = attach_check
        self.always_send = always_send
        self.verify = verify

    def _get_attachments(self):
        """Download the attachment files from the S3 bucket"""
        s3_conn = S3Hook(aws_conn_id=self.aws_conn_id, verify=self.verify)
        filenames = []
        for key in self.s3_keys:
            try:
                filename = s3_conn.download_file(key=key, bucket_name=self.s3_bucket)
                newname = f"/tmp/{key.split('/')[-1]}"
                os.rename(filename, newname)
                if self.attach_check(newname):
                    filenames.append(newname)
            except Exception:
                self.log.info(f"Missing file: {key} in bucket: {self.s3_bucket}")

        if filenames or self.always_send:
            return filenames
        raise AirflowSkipException("There weren't any alerts to send. Skipping email.")

    def execute(self, context):
        self.files = self._get_attachments()
        super().execute(context)
