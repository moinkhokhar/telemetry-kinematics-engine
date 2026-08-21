output "ecr_repository_url" {
  value       = module.telemetry_ecr.repository_url
  description = "The URL of the created Amazon ECR repository"
}

output "ecr_repository_arn" {
  value       = module.telemetry_ecr.repository_arn
  description = "The ARN of the created Amazon ECR repository"
}
