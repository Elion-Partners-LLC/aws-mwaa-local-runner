output "mwaa_dags_trigger_lambda_arn" {
  value       = module.mwaa_dags_trigger.mwaa_dags_trigger_lambda_arn
  description = "ARN for the trigger notification for the files to be processed by dags"
}
