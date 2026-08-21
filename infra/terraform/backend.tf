# Backend configuration template for state locking
# terraform {
#   backend "s3" {
#     bucket         = "telemetry-engine-tf-state"
#     key            = "production/state.tfstate"
#     region         = "us-east-1"
#     dynamodb_table = "telemetry-engine-tf-locks"
#     encrypt        = true
#   }
# }
