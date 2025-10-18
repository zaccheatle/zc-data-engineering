terraform {
  backend "s3" {
    bucket         = "omnirag-dev-terraform-state-us-east-1"
    key            = "omnirag/dev/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "omnirag-dev-terraform-state-lock-us-east-1"
    encrypt        = true
  }
}