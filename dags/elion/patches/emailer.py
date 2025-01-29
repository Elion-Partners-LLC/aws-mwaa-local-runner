from typing import List, Optional, Union

from airflow.configuration import conf
from airflow.exceptions import AirflowConfigException
from airflow.providers.amazon.aws.hooks.ses import SesHook


def send_email(
    to: Union[List[str], str],
    subject: str,
    html_content: str,
    mail_from: Optional[str] = None,
    files: Optional[List] = None,
    cc: Optional[Union[List[str], str]] = None,
    bcc: Optional[Union[List[str], str]] = None,
    mime_subtype: str = "mixed",
    mime_charset: str = "utf-8",
    conn_id: str = "aws_default",
    **kwargs,
) -> None:
    """Email backend for SES."""
    if mail_from is not None:
        send_mail_from = mail_from
    else:
        send_mail_from = conf.get("smtp", "SMTP_MAIL_FROM")

    hook = SesHook(aws_conn_id=conn_id)
    hook.send_email(
        mail_from=send_mail_from,
        to=to,
        subject=subject,
        html_content=html_content,
        files=files,
        cc=cc,
        bcc=bcc,
        mime_subtype=mime_subtype,
        mime_charset=mime_charset,
    )
