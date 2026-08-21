output "ecr_repository_url" {
  value       = module.ecr_service.repository_url
  description = "The URL of the created Amazon ECR repository"
}

output "ecr_repository_arn" {
  value       = module.ecr_service.repository_arn
  description = "The ARN of the created Amazon ECR repository"
}
