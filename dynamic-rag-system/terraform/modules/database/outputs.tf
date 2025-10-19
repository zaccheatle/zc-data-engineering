output "cluster_endpoint" {
  description = "Aurora cluster write endpoint"
  value       = aws_rds_cluster.database.endpoint
}

output "cluster_reader_endpoint" {
  description = "Aurora cluster read endpoint"
  value       = aws_rds_cluster.database.reader_endpoint
}

output "database_name" {
  description = "Database name"
  value       = aws_rds_cluster.database.database_name
}

output "db_secret_arn" {
  description = "Database credentials secret ARN"
  value       = var.database_secret_arn
}

output "cluster_id" {
  description = "Cluster identifier"
  value       = aws_rds_cluster.database.id
}