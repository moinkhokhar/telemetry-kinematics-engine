resource "aws_ecr_repository" "service_repository" {
  name                 = var.repository_name
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "KMS"
  }

  tags = {
    Environment = var.environment
    Service     = "telemetry-kinematics-engine"
    ManagedBy   = "Terraform"
  }
}
