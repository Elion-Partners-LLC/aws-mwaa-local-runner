output "mwaa_dags_trigger_lambda_arn" {
  value       = aws_lambda_function.trigger_event_mwaa_dags.arn
  description = "ARN for the trigger notification for the files to be processed by dags"
}
