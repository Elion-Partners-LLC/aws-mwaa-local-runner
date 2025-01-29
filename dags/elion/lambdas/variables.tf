variable "data_lake_s3_bucket_name" {
  description = "Bucket name for the Data Lake S3 Bucket"
  type        = string
}

variable "lambda_layers" {
  description = "Map all lambda layers available."
  type        = map(string)
}