variable "data_lake_s3_bucket_name" {
  description = "Bucket name for the Data Lake S3 Bucket"
  type        = string
}

variable "layers" {
  description = "Layers to be used in the lambda function."
  type        = list(string)
}