output "ecr_repository_url" {
  value       = aws_ecr_repository.telemetry_engine.repository_url
  description = "The URL of the created Amazon ECR repository"
}

output "ecr_repository_arn" {
  value       = aws_ecr_repository.telemetry_engine.arn
  description = "The ARN of the created Amazon ECR repository"
}
