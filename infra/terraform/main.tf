provider "aws" {
  region = var.aws_region
}

module "ecr_service" {
  source          = "./modules/ecr"
  repository_name = var.repository_name
  environment     = var.environment
}
