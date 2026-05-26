variable "aws_region" {
  description = "AWS region where the avatars bucket will be created."
  type        = string
  default     = "eu-central-1"
}

variable "avatars_bucket_name" {
  description = "Name of the S3 bucket used for consultant avatars."
  type        = string
}

variable "project_name" {
  description = "Project tag value for the S3 bucket."
  type        = string
  default     = "bachelors-consulting"
}

variable "allowed_origins" {
  description = "Origins allowed to fetch avatar images via browser requests."
  type        = list(string)
  default = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1:3000"
  ]
}
