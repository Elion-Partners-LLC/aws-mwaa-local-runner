module "mwaa_dags_trigger" {
  source                    = "./mwaa_dags_trigger"
  data_lake_s3_bucket_name  = var.data_lake_s3_bucket_name
  layers = [
    var.lambda_layers.requests_lambda_layer_19arn_python39
  ]
}
