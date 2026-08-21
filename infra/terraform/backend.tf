# Production state configuration with encryption and DynamoDB locking
terraform {
  backend "s3" {
    bucket         = "telemetry-engine-tfstate-production"
    key            = "telemetry-engine/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "telemetry-engine-tf-locks"
  }
}
