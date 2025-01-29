#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import functools
import json
import time
from typing import TYPE_CHECKING, Any, List, Optional, Sequence
from uuid import uuid4

import boto3
from airflow.models import BaseOperator
from airflow.providers.amazon.aws.hooks.base_aws import AwsBaseHook

if TYPE_CHECKING:
    from airflow.utils.context import Context


class AwsLambdaInvokeFunctionOperator(BaseOperator):
    """
    Invokes an AWS Lambda function.
    You can invoke a function synchronously (and wait for the response),
    or asynchronously.
    To invoke a function asynchronously,
    set `invocation_type` to `Event`. For more details,
    review the boto3 Lambda invoke docs.

    :param function_name: The name of the AWS Lambda function, version, or alias.
    :param payload: The JSON string that you want to provide to your Lambda function as input.
    :param log_type: Set to Tail to include the execution log in the response. Otherwise, set to "None".
    :param qualifier: Specify a version or alias to invoke a published version of the function.
    :param aws_conn_id: The AWS connection ID to use

    .. seealso::
        For more information on how to use this operator, take a look at the guide:
        :ref:`howto/operator:AwsLambdaInvokeFunctionOperator`

    """

    template_fields: Sequence[str] = (
        "function_name",
        "payload",
        "qualifier",
        "invocation_type",
    )

    ui_color = "#ff7300"

    def __init__(
        self,
        *,
        function_name: str,
        log_type: Optional[str] = None,
        qualifier: Optional[str] = None,
        invocation_type: Optional[str] = None,
        client_context: Optional[str] = None,
        payload: Optional[str] = None,
        aws_conn_id: str = "aws_default",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.function_name = function_name
        self.payload = payload
        self.log_type = log_type
        self.qualifier = qualifier
        self.invocation_type = invocation_type
        self.client_context = client_context
        self.aws_conn_id = aws_conn_id

    def execute(self, context: "Context"):
        """
        Invokes the target AWS Lambda function from Airflow.

        :return: The response payload from the function, or an error object.
        """
        hook = LambdaHook(aws_conn_id=self.aws_conn_id)
        success_status_codes = [200, 202, 204]
        self.log.info(
            "Invoking AWS Lambda function: %s with payload: %s",
            self.function_name,
            self.payload,
        )
        response = hook.invoke_lambda(
            function_name=self.function_name,
            invocation_type=self.invocation_type,
            log_type=self.log_type,
            client_context=self.client_context,
            payload=self.payload,
            qualifier=self.qualifier,
        )
        self.log.info("Lambda response metadata: %r", response.get("ResponseMetadata"))
        if response.get("StatusCode") not in success_status_codes:
            raise ValueError(
                "Lambda function did not execute",
                json.dumps(response.get("ResponseMetadata")),
            )
        payload_stream = response.get("Payload")
        payload = payload_stream.read().decode()
        if "FunctionError" in response:
            raise ValueError(
                "Lambda function execution resulted in error",
                {
                    "ResponseMetadata": response.get("ResponseMetadata"),
                    "Payload": payload,
                },
            )
        self.log.info(
            "Lambda function invocation succeeded: %r", response.get("ResponseMetadata")
        )
        return payload


class CustomLambdaFunctionOperator(AwsLambdaInvokeFunctionOperator):
    def __init__(
        self,
        *,
        function_name: str,
        log_type: Optional[str] = None,
        qualifier: Optional[str] = None,
        invocation_type: str = "Event",
        client_context: Optional[str] = None,
        payload: Optional[str] = None,
        aws_conn_id: str = "aws_default",
        correlation_id: str = str(uuid4()),
        **kwargs,
    ):
        super().__init__(
            function_name=function_name,
            log_type=log_type,
            qualifier=qualifier,
            invocation_type=invocation_type,
            client_context=client_context,
            payload=json.dumps(
                {**json.loads((payload or "{}")), **{"correlation_id": correlation_id}}
            ),
            aws_conn_id=aws_conn_id,
            **kwargs,
        )
        self.correlation_id = correlation_id

    def log_processor(func):
        @functools.wraps(func)
        def wrapper_decorator(self, *args, **kwargs):
            payload = func(self, *args, **kwargs)
            function_timeout = self.get_function_timeout()
            self.process_log_events(function_timeout)
            return payload

        return wrapper_decorator

    @log_processor
    def execute(self, context: "Context"):
        return super().execute(context)

    def get_function_timeout(self):
        resp = boto3.client("lambda").get_function_configuration(
            FunctionName=self.function_name
        )
        return resp["Timeout"]

    def process_log_events(self, function_timeout: int):
        start_time = 0
        for _ in range(function_timeout):
            response_iterator = self.get_response_iterator(
                self.function_name, self.correlation_id, start_time
            )
            for page in response_iterator:
                for event in page["events"]:
                    start_time = event["timestamp"]
                    message = json.loads(event["message"])
                    print(message)
                    if message["level"] == "ERROR":
                        raise RuntimeError("ERROR found in log")
                    if message["message"] == "Function ended":
                        return
            time.sleep(1)
        raise RuntimeError(
            "Lambda function end message not found after function timeout"
        )

    @staticmethod
    def get_response_iterator(function_name: str, correlation_id: str, start_time: int):
        paginator = boto3.client("logs").get_paginator("filter_log_events")
        return paginator.paginate(
            logGroupName=f"/aws/lambda/{function_name}",
            filterPattern=f'"{correlation_id}"',
            startTime=start_time + 1,
        )


class LambdaHook(AwsBaseHook):
    """
    Interact with AWS Lambda

    Additional arguments (such as ``aws_conn_id``) may be specified and
    are passed down to the underlying AwsBaseHook.

    .. seealso::
        :class:`~airflow.providers.amazon.aws.hooks.base_aws.AwsBaseHook`

    :param function_name: AWS Lambda Function Name
    :param log_type: Tail Invocation Request
    :param qualifier: AWS Lambda Function Version or Alias Name
    :param invocation_type: AWS Lambda Invocation Type (RequestResponse, Event etc)
    """

    def __init__(
        self,
        *args,
        **kwargs,
    ) -> None:
        kwargs["client_type"] = "lambda"
        super().__init__(*args, **kwargs)

    def invoke_lambda(
        self,
        *,
        function_name: str,
        invocation_type: Optional[str] = None,
        log_type: Optional[str] = None,
        client_context: Optional[str] = None,
        payload: Optional[str] = None,
        qualifier: Optional[str] = None,
    ):
        """Invoke Lambda Function. Refer to the boto3 documentation for more info."""
        invoke_args = {
            "FunctionName": function_name,
            "InvocationType": invocation_type,
            "LogType": log_type,
            "ClientContext": client_context,
            "Payload": payload,
            "Qualifier": qualifier,
        }
        return self.conn.invoke(
            **{k: v for k, v in invoke_args.items() if v is not None}
        )

    def create_lambda(
        self,
        *,
        function_name: str,
        runtime: str,
        role: str,
        handler: str,
        code: dict,
        description: Optional[str] = None,
        timeout: Optional[int] = None,
        memory_size: Optional[int] = None,
        publish: Optional[bool] = None,
        vpc_config: Optional[Any] = None,
        package_type: Optional[str] = None,
        dead_letter_config: Optional[Any] = None,
        environment: Optional[Any] = None,
        kms_key_arn: Optional[str] = None,
        tracing_config: Optional[Any] = None,
        tags: Optional[Any] = None,
        layers: Optional[list] = None,
        file_system_configs: Optional[List[Any]] = None,
        image_config: Optional[Any] = None,
        code_signing_config_arn: Optional[str] = None,
        architectures: Optional[List[str]] = None,
    ) -> dict:
        """Create a Lambda Function"""
        create_function_args = {
            "FunctionName": function_name,
            "Runtime": runtime,
            "Role": role,
            "Handler": handler,
            "Code": code,
            "Description": description,
            "Timeout": timeout,
            "MemorySize": memory_size,
            "Publish": publish,
            "VpcConfig": vpc_config,
            "PackageType": package_type,
            "DeadLetterConfig": dead_letter_config,
            "Environment": environment,
            "KMSKeyArn": kms_key_arn,
            "TracingConfig": tracing_config,
            "Tags": tags,
            "Layers": layers,
            "FileSystemConfigs": file_system_configs,
            "ImageConfig": image_config,
            "CodeSigningConfigArn": code_signing_config_arn,
            "Architectures": architectures,
        }
        return self.conn.create_function(
            **{k: v for k, v in create_function_args.items() if v is not None},
        )
