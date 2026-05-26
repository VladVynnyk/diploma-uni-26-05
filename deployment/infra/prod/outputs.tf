output "ec2_public_ip" {
  description = "Elastic IP attached to the production EC2 instance."
  value       = aws_eip.app.public_ip
}

output "app_url" {
  description = "Primary application URL."
  value       = "https://${var.app_domain}"
}

output "avatars_bucket_name" {
  description = "S3 bucket used for avatar uploads."
  value       = aws_s3_bucket.avatars.bucket
}

output "avatars_base_url" {
  description = "Base public URL of the S3 avatars bucket."
  value       = local.avatars_base_url
}

output "aws_region" {
  description = "AWS region used for the deployment."
  value       = var.aws_region
}

output "dns_managed_by_route53" {
  description = "Whether Route53 record management is enabled."
  value       = var.enable_route53
}
