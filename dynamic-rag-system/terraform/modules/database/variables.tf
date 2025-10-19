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

variable "vpc_id" {
  description = "ID for vpc used by database"
  type = string
}

variable "private_subnet_ids" {
  description = "IDs for private subnets used by database"
  type = list(string)
}

variable "database_security_group" {
  description = "ID for security group used by database"
  type = string
}

variable "database_kms_key" {
  description = "KMS key used by database"
  type = string
}

variable "database_secret_arn" {
  description = "ARN of secret used by database"
  type = string
}