from typing import Any, Dict, List, Optional, Union

from airflow.models.baseoperator import BaseOperator
from airflow.utils.email import send_email


class ElionEmailOperator(BaseOperator):
    def __init__(
        self,
        to: Union[List[str], str],
        subject: str,
        html_content: str,
        mail_from: Optional[str] = None,
        files: Optional[List] = None,
        cc: Optional[Union[List[str], str]] = None,
        bcc: Optional[Union[List[str], str]] = None,
        mime_subtype: str = "mixed",
        mime_charset: str = "utf-8",
        conn_id: Optional[str] = None,
        custom_headers: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.to = to
        self.subject = subject
        self.html_content = html_content
        self.mail_from = mail_from
        self.files = files or []
        self.cc = cc
        self.bcc = bcc
        self.mime_subtype = mime_subtype
        self.mime_charset = mime_charset
        self.conn_id = conn_id
        self.custom_headers = custom_headers

    def execute(self, context):
        send_email(
            to=self.to,
            subject=self.subject,
            html_content=self.html_content,
            mail_from=self.mail_from,
            files=self.files,
            cc=self.cc,
            bcc=self.bcc,
            mime_subtype=self.mime_subtype,
            mime_charset=self.mime_charset,
            conn_id=self.conn_id,
            custom_headers=self.custom_headers,
        )
