terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

data "aws_route53_zone" "root" {
  count        = var.enable_route53 ? 1 : 0
  name         = var.root_domain
  private_zone = false
}

locals {
  common_tags = merge(
    {
      Project     = var.project_name
      Environment = "prod"
    },
    var.tags
  )

  avatars_base_url = "https://${aws_s3_bucket.avatars.bucket}.s3.${var.aws_region}.amazonaws.com"
  user_data = templatefile("${path.module}/user_data.sh.tpl", {
    repo_url               = var.repo_url
    repo_branch            = var.repo_branch
    app_domain             = var.app_domain
    letsencrypt_email      = var.letsencrypt_email
    aws_region             = var.aws_region
    avatars_bucket_name    = aws_s3_bucket.avatars.bucket
    avatars_base_url       = local.avatars_base_url
    postgres_user          = var.postgres_user
    postgres_password      = var.postgres_password
    postgres_db            = var.postgres_db
    api_key                = var.api_key
    jwt_secret_key         = var.jwt_secret_key
    jwt_refresh_secret_key = var.jwt_refresh_secret_key
    seed_demo_data         = tostring(var.seed_demo_data)
    use_s3_avatars         = tostring(var.use_s3_avatars)
  })
}

resource "aws_security_group" "app" {
  name        = "${var.project_name}-prod-sg"
  description = "Security group for production consulting app"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.ssh_allowed_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = local.common_tags
}

resource "aws_s3_bucket" "avatars" {
  bucket = var.avatars_bucket_name
  tags   = local.common_tags
}

resource "aws_s3_bucket_ownership_controls" "avatars" {
  bucket = aws_s3_bucket.avatars.id

  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_public_access_block" "avatars" {
  bucket = aws_s3_bucket.avatars.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_cors_configuration" "avatars" {
  bucket = aws_s3_bucket.avatars.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "HEAD"]
    allowed_origins = ["*"]
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}

resource "aws_s3_bucket_policy" "avatars_public_read" {
  bucket = aws_s3_bucket.avatars.id

  depends_on = [
    aws_s3_bucket_public_access_block.avatars
  ]

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadAvatarsOnly"
        Effect    = "Allow"
        Principal = "*"
        Action    = ["s3:GetObject"]
        Resource  = "${aws_s3_bucket.avatars.arn}/avatars/*"
      }
    ]
  })
}

resource "aws_iam_role" "ec2_app" {
  name = "${var.project_name}-prod-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = local.common_tags
}

resource "aws_iam_role_policy" "ec2_s3_access" {
  name = "${var.project_name}-prod-s3-policy"
  role = aws_iam_role.ec2_app.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket"
        ]
        Resource = aws_s3_bucket.avatars.arn
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = "${aws_s3_bucket.avatars.arn}/avatars/*"
      }
    ]
  })
}

resource "aws_iam_instance_profile" "ec2_app" {
  name = "${var.project_name}-prod-instance-profile"
  role = aws_iam_role.ec2_app.name
}

resource "aws_instance" "app" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_type
  key_name                    = var.key_name
  subnet_id                   = data.aws_subnets.default.ids[0]
  vpc_security_group_ids      = [aws_security_group.app.id]
  associate_public_ip_address = true
  iam_instance_profile        = aws_iam_instance_profile.ec2_app.name
  user_data                   = local.user_data

  root_block_device {
    volume_size = var.root_volume_size
    volume_type = "gp3"
  }

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-prod"
  })
}

resource "aws_eip" "app" {
  domain   = "vpc"
  instance = aws_instance.app.id

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-prod-eip"
  })
}

resource "aws_route53_record" "app" {
  count   = var.enable_route53 ? 1 : 0
  zone_id = data.aws_route53_zone.root[0].zone_id
  name    = var.app_domain
  type    = "A"
  ttl     = 300
  records = [aws_eip.app.public_ip]
}
