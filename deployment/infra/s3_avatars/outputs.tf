output "bucket_name" {
  description = "Created S3 bucket name."
  value       = aws_s3_bucket.avatars.bucket
}

output "region" {
  description = "AWS region of the bucket."
  value       = var.aws_region
}

output "base_url" {
  description = "Base public URL for files in the bucket."
  value       = "https://${aws_s3_bucket.avatars.bucket}.s3.${var.aws_region}.amazonaws.com"
}
