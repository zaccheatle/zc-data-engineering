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

variable "vpc_cidr_block" {
  description = "VPC cidr block"
  type        = string
  default     = "10.0.0.0/16"
}

