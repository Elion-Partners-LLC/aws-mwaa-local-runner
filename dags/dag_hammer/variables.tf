variable "data_lake_s3_bucket_name" {
  description = "Bucket name for the Data Lake S3 Bucket"
  type        = string
}

variable "ecr_repository_url" {
  description = "URL of the ECR Repository."
  type        = string
}

variable "temp_data_store_s3_bucket_name" {
  description = "Bucket name for the Temp Data Store"
  type        = string
}
