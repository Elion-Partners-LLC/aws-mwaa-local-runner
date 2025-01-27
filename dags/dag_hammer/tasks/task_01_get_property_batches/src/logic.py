import logging
import os

from functions import (
    get_properties_from_redshift,
    get_redshift_connection,
    split_properties,
    upload_to_s3,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
logger.addHandler(stream_handler)


def main():
    red_conn = get_redshift_connection()
    properties = get_properties_from_redshift(red_conn)
    split_properties(properties)
    upload_to_s3()


if __name__ == "__main__":
    main()
