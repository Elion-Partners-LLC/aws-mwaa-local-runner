module "task-01-get-property-batches" {
  source                         = "./tasks/task_01_get_property_batches"
  ecr_repository_url             = var.ecr_repository_url
  temp_data_store_s3_bucket_name = var.temp_data_store_s3_bucket_name
}

module "task-04-download-hammer-data" {
  source                   = "./tasks/task_04_download_hammer_data"
  ecr_repository_url       = var.ecr_repository_url
  data_lake_s3_bucket_name = var.data_lake_s3_bucket_name
  temp_data_store_s3_bucket_name = var.temp_data_store_s3_bucket_name
}
