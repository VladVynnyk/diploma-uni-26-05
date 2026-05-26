# S3 Avatars Setup

This automation creates a simple S3 bucket for consultant avatar images and uploads local files from `./photos/`.

## What each part does

### Terraform

Path: `deployment/infra/s3_avatars`

Terraform creates:

- one S3 bucket
- public read access for objects
- CORS for browser `GET` and `HEAD` requests
- outputs:
  - `bucket_name`
  - `region`
  - `base_url`

It does not create CloudFront, IAM users, ECS, RDS, or upload image objects.

### boto3 upload script

Path: `deployment/scripts/upload_avatars_to_s3.py`

This script:

- reads avatar files from `./photos/`
- uploads `.png`, `.jpg`, `.jpeg`, `.webp` files to `avatars/` in S3
- sets the correct `ContentType`
- writes `deployment/generated/avatar_urls.json`

The generated JSON contains:

- `file_urls`: `filename -> public URL`
- `consultant_email_urls`: `consultant email -> public URL`

### Master setup script

Path: `deployment/scripts/setup_s3_avatars.py`

This script:

1. runs `terraform init`
2. runs `terraform apply -auto-approve`
3. reads `terraform output -json`
4. runs the boto3 upload script with the resolved bucket settings
5. runs a DB sync script that updates `users.photo` from the generated avatar mapping

## Required environment

You need:

- `terraform` in `PATH`
- AWS credentials available through the standard AWS credential chain

Supported credential sources:

- environment variables
- `deployment/.env` loaded by `python-dotenv` in the master script
- `aws configure`
- IAM role

Example environment variables:

```bash
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
export AWS_DEFAULT_REGION=eu-central-1
export AVATARS_BUCKET_NAME=your-unique-avatars-bucket-name
```

You can also put these values into:

`deployment/.env`

Example:

```env
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_DEFAULT_REGION=eu-central-1
AVATARS_BUCKET_NAME=your-unique-avatars-bucket-name
```

Or configure locally with:

```bash
aws configure
```

## How to run the full process

From the repository root:

```bash
python deployment/scripts/setup_s3_avatars.py
```

The master script reads:

- `deployment/.env` via `python-dotenv`
- `AVATARS_BUCKET_NAME` or `TF_VAR_avatars_bucket_name`
- optional `AWS_DEFAULT_REGION` or `AWS_REGION`

## How to run Terraform separately

```bash
cd deployment/infra/s3_avatars
terraform init
terraform apply -auto-approve -var="avatars_bucket_name=your-avatars-bucket-name"
terraform output -json
```

You must provide `avatars_bucket_name`. Optional variables:

- `aws_region`
- `allowed_origins`
- `project_name`

## How to run avatar upload separately

```bash
python deployment/scripts/upload_avatars_to_s3.py --bucket-name your-avatars-bucket-name --aws-region eu-central-1
```

Optional arguments:

- `--photos-dir`
- `--manifest-path`
- `--output-path`

## Avatar mapping file

Generated file:

`deployment/generated/avatar_urls.json`

This file is used by:

- the DB sync script, which updates existing `users.photo` values directly
- the demo seed logic, which uses these URLs for seeded consultants

If it does not exist, seed falls back to `https://via.placeholder.com/150`.

## How seed data uses S3 URLs

The seed checks `deployment/generated/avatar_urls.json` and reads:

- `consultant_email_urls[email]` first
- fallback placeholder image if no mapping exists

This means:

- seed works even before S3 is configured
- after S3 setup, rerunning seed updates consultant `photo` fields to real S3 URLs

## How to sync avatar URLs into the database manually

```bash
python deployment/scripts/sync_avatar_urls_to_db.py
```

This script:

- loads `deployment/.env`
- reads `DB_URI`
- reads `deployment/generated/avatar_urls.json`
- updates `users.photo` for matching consultant emails

## What the main setup script does now

Running:

```bash
python deployment/scripts/setup_s3_avatars.py
```

now performs the full flow:

1. Terraform bucket setup
2. S3 avatar upload
3. `avatar_urls.json` generation
4. direct database update of `users.photo`

## How to verify avatars are public

1. Open `deployment/generated/avatar_urls.json`
2. Copy any generated URL
3. Open it in a browser
4. The image should load directly without authentication
