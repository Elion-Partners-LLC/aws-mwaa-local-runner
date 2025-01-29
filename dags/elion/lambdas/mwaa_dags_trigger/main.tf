data "aws_iam_role" "lambda_role" {
  name = "DataEngineeringLambdaRole"
}

data "archive_file" "zip_lambda_function" {
  type        = "zip"
  source_dir  = "${path.module}"
  output_path = "${path.module}/lambda_function.zip"
}

resource "aws_lambda_function" "trigger_event_mwaa_dags" {
  function_name    = "trigger_event_mwaa_dags"
  role             = data.aws_iam_role.lambda_role.arn
  filename         = data.archive_file.zip_lambda_function.output_path
  source_code_hash = data.archive_file.zip_lambda_function.output_base64sha256
  layers           = var.layers
  runtime          = "python3.9"
  handler          = "logic.lambda_handler"
  timeout          = 30

  tags = {
    Name         = "Trigger-ingestion_MWAA_Dags"
    BusinessUnit = "Company"
    ServiceName  = "Company"
    Owner        = "Emilio Silveira"
  }
}

# Adding S3 bucket as trigger to my lambda and giving the permissions
resource "aws_lambda_permission" "s3_trigger_mwaa_dags" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.trigger_event_mwaa_dags.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = "arn:aws:s3:::${var.data_lake_s3_bucket_name}"
}

resource "aws_lambda_permission" "ei_staging_trigger_mwaa_dags" {
  statement_id  = "AllowInvestmentManagementRoleInvokeStaging"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.trigger_event_mwaa_dags.function_name
  principal     = "arn:aws:iam::760057578774:role/InvestmentManagementBackendTaskRole"
}

resource "aws_lambda_permission" "ei_production_trigger_mwaa_dags" {
  statement_id  = "AllowInvestmentManagementRoleInvokeProduction"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.trigger_event_mwaa_dags.function_name
  principal     = "arn:aws:iam::635445179061:role/InvestmentManagementBackendTaskRole"
}
