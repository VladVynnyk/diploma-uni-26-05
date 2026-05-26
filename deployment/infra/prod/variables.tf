variable "project_name" {
  type        = string
  description = "Project name used in resource naming."
  default     = "consulting-app"
}

variable "aws_region" {
  type        = string
  description = "AWS region for production resources."
  default     = "eu-central-1"
}

variable "instance_type" {
  type        = string
  description = "EC2 instance type."
  default     = "t3.small"
}

variable "key_name" {
  type        = string
  description = "Existing EC2 key pair name for SSH access."
}

variable "ssh_allowed_cidr" {
  type        = string
  description = "CIDR block allowed to SSH into the instance."
  default     = "0.0.0.0/0"
}

variable "root_volume_size" {
  type        = number
  description = "Root EBS volume size in GB."
  default     = 25
}

variable "repo_url" {
  type        = string
  description = "Public HTTPS repository URL cloned by EC2 user_data."
}

variable "repo_branch" {
  type        = string
  description = "Git branch checked out on EC2."
  default     = "main"
}

variable "enable_route53" {
  type        = bool
  description = "Whether Terraform should manage the Route53 A record."
  default     = true
}

variable "root_domain" {
  type        = string
  description = "Hosted zone root domain, for example example.com."
  default     = ""
}

variable "app_domain" {
  type        = string
  description = "Application domain, for example consulting.example.com."
}

variable "letsencrypt_email" {
  type        = string
  description = "Email used by Let's Encrypt."
}

variable "avatars_bucket_name" {
  type        = string
  description = "Unique S3 bucket name used for consultant avatars."
}

variable "postgres_user" {
  type        = string
  description = "Postgres username."
}

variable "postgres_password" {
  type        = string
  description = "Postgres password."
  sensitive   = true
}

variable "postgres_db" {
  type        = string
  description = "Postgres database name."
}

variable "api_key" {
  type        = string
  description = "Optional payment API key for backend integrations."
  default     = ""
  sensitive   = true
}

variable "jwt_secret_key" {
  type        = string
  description = "JWT access token signing key."
  sensitive   = true
}

variable "jwt_refresh_secret_key" {
  type        = string
  description = "JWT refresh token signing key."
  sensitive   = true
}

variable "seed_demo_data" {
  type        = bool
  description = "Whether demo data seed should run on backend startup."
  default     = true
}

variable "use_s3_avatars" {
  type        = bool
  description = "Whether seed should assign S3 avatar URLs."
  default     = true
}

variable "tags" {
  type        = map(string)
  description = "Additional tags for AWS resources."
  default     = {}
}
