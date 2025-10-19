variable "account_id" {
  description = "Account ID of caller"
  type = string
}

variable "caller_arn" {
  description = "ARN of caller"
  type = string
}

variable "caller_user" {
  description = "User ID of caller"
  type = string
}

variable "aws_region" {
  description = "AWS Region"
  type        = string
  default     = "us-east-1"
}

variable "env" {
  description = "AWS Environment"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "omnirag"
}

variable "uploads_bucket_id" {
  description = "Uploads bucket id"
  type = string
}

variable "uploads_bucket_arn" {
  description = "Uploads bucket arn"
  type = string}

variable "processed_bucket_id" {
  description = "Processed bucket id"
  type = string
}

variable "processed_bucket_arn" {
  description = "Processed bucket arn"
  type = string
}

variable "reports_bucket_id" {
  description = "Reports bucket id"
  type = string
}

variable "reports_bucket_arn" {
  description = "Reports bucket arn"
  type = string
}

variable "website_bucket_id" {
  description = "Website bucket id"
  type = string
}

variable "website_bucket_arn" {
  description = "Website bucket arn"
  type = string
}