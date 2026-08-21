output "repository_url" {
  value       = aws_ecr_repository.service_repository.repository_url
  description = "ECR Repository URL"
}

output "repository_arn" {
  value       = aws_ecr_repository.service_repository.arn
  description = "ECR Repository ARN"
}
