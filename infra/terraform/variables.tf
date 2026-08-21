variable "aws_region" {
  type        = string
  default     = "us-east-1"
  description = "Target deployment AWS region"
}

variable "environment" {
  type        = string
  default     = "production"
  description = "Operating deployment tier (staging/production)"
}

variable "repository_name" {
  type        = string
  default     = "telemetry-kinematics-engine"
  description = "Name of the AWS ECR container registry repository"
}
