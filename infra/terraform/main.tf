terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  type        = string
  default     = "us-east-1"
  description = "Target deployment AWS region"
}

variable "environment" {
  type        = string
  default     = "production"
  description = "Target operating environment"
}

resource "aws_ecr_repository" "telemetry_engine" {
  name                 = "telemetry-kinematics-engine"
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Environment = var.environment
    Service     = "telemetry-engine"
  }
}
