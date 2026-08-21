variable "repository_name" {
  type        = string
  description = "Name of the AWS ECR container repository"
}

variable "environment" {
  type        = string
  description = "Target deployment environment (staging/production)"
}
