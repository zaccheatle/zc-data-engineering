module "networking" {
  source = "../../modules/networking"

  project_name   = var.project_name
  env            = var.env
  aws_region     = var.aws_region
  vpc_cidr_block = var.vpc_cidr_block
}