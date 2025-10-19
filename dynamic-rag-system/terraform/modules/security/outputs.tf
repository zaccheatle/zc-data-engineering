output "application_kms_key_id" {
  description = "Application KMS key ID"
  value       = aws_kms_key.application.id
}

output "database_kms_key_id" {
  description = "Database KMS key ID"
  value       = aws_kms_key.db_key.id
}

output "db_secret_arn" {
  description = "Database credentials secret ARN"
  value       = aws_secretsmanager_secret.database_secret.arn
}

output "api_secret_arn" {
  description = "API keys secret ARN"
  value       = aws_secretsmanager_secret.api_keys.arn
}