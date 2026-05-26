# Production Terraform

This folder provisions the minimal AWS infrastructure for the production deployment:
- EC2 instance
- Elastic IP
- Security Group
- S3 bucket for avatars
- IAM role / instance profile for S3 access
- Optional Route53 A record

Use `terraform.tfvars.example` as the starting point for your real `terraform.tfvars`.
