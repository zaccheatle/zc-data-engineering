output "uploads_bucket_id" {
  description = "Uploads bucket id"
  value = aws_s3_bucket.uploads.id
}

output "uploads_bucket_arn" {
  description = "Uploads bucket arn"
  value = aws_s3_bucket.uploads.arn
}

output "processed_bucket_id" {
  description = "Processed bucket id"
  value = aws_s3_bucket.processed.id
}

output "processed_bucket_arn" {
  description = "Processed bucket arn"
  value = aws_s3_bucket.processed.arn
}

output "reports_bucket_id" {
  description = "Reports bucket id"
  value = aws_s3_bucket.reports.id
}

output "reports_bucket_arn" {
  description = "Reports bucket arn"
  value = aws_s3_bucket.reports.arn
}

output "website_bucket_id" {
  description = "Website bucket id"
  value = aws_s3_bucket.website.id
}

output "website_bucket_arn" {
  description = "Website bucket arn"
  value = aws_s3_bucket.website.arn
}
