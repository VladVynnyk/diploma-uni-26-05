from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import boto3
    from botocore.exceptions import BotoCoreError, NoCredentialsError
except ImportError as exc:  # pragma: no cover - environment dependent
    print("boto3 is required for production deploy automation.", file=sys.stderr)
    raise SystemExit(1) from exc


ROOT_DIR = Path(__file__).resolve().parents[2]
PROD_INFRA_DIR = ROOT_DIR / "deployment" / "infra" / "prod"
UPLOAD_SCRIPT = ROOT_DIR / "deployment" / "scripts" / "upload_avatars_to_s3.py"


def ensure_command_exists(command_name: str) -> None:
    if shutil.which(command_name) is None:
        raise RuntimeError(f"`{command_name}` is not installed or is not available in PATH.")


def ensure_aws_credentials() -> None:
    try:
        session = boto3.Session()
        credentials = session.get_credentials()
        if credentials is None:
            raise NoCredentialsError()
        sts = session.client("sts")
        sts.get_caller_identity()
    except (BotoCoreError, NoCredentialsError, Exception) as exc:  # pragma: no cover
        raise RuntimeError(
            "AWS credentials are not available. Configure the standard AWS credentials chain before deployment."
        ) from exc


def run_command(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=str(cwd),
        check=True,
        capture_output=True,
        text=True,
    )


def terraform_outputs() -> dict[str, str]:
    output = run_command(["terraform", "output", "-json"], PROD_INFRA_DIR)
    payload = json.loads(output.stdout)
    return {key: value["value"] for key, value in payload.items()}


def upload_avatars(bucket_name: str, aws_region: str) -> None:
    command = [
        sys.executable,
        str(UPLOAD_SCRIPT),
        "--bucket-name",
        bucket_name,
        "--aws-region",
        aws_region,
        "--prefix",
        "avatars",
    ]
    result = run_command(command, ROOT_DIR)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)


def main() -> int:
    try:
        ensure_command_exists("terraform")
        ensure_aws_credentials()
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"Running Terraform in {PROD_INFRA_DIR}")
    try:
        init_result = run_command(["terraform", "init"], PROD_INFRA_DIR)
        print(init_result.stdout)

        apply_result = run_command(["terraform", "apply", "-auto-approve"], PROD_INFRA_DIR)
        print(apply_result.stdout)
    except subprocess.CalledProcessError as exc:
        print(f"Terraform failed: {' '.join(exc.cmd)}", file=sys.stderr)
        if exc.stdout:
            print(exc.stdout, file=sys.stderr)
        if exc.stderr:
            print(exc.stderr, file=sys.stderr)
        return 1

    outputs = terraform_outputs()

    try:
        upload_avatars(
            bucket_name=outputs["avatars_bucket_name"],
            aws_region=outputs["aws_region"],
        )
    except subprocess.CalledProcessError as exc:
        print("Avatar upload failed.", file=sys.stderr)
        if exc.stdout:
            print(exc.stdout, file=sys.stderr)
        if exc.stderr:
            print(exc.stderr, file=sys.stderr)
        return 1

    app_url = outputs["app_url"]
    ec2_ip = outputs["ec2_public_ip"]
    bucket_name = outputs["avatars_bucket_name"]
    avatars_base_url = outputs["avatars_base_url"]
    aws_region = outputs["aws_region"]
    dns_managed = outputs.get("dns_managed_by_route53", False)

    print("Production deploy finished.")
    print(f"App URL: {app_url}")
    print(f"EC2 public IP: {ec2_ip}")
    print(f"S3 bucket: {bucket_name}")
    print(f"Avatars base URL: {avatars_base_url}")
    print(f"AWS region: {aws_region}")
    print(f"DNS status: {'Route53 managed' if dns_managed else 'Manual DNS required'}")
    print("SSH command:")
    print("  ssh -i /path/to/your-key.pem ubuntu@" + ec2_ip)
    print("Post-deploy checks:")
    print(f"  - open {app_url}")
    print(f"  - open {app_url}/api/docs")
    print("  - ssh into EC2 and run `docker ps`")
    print("  - inspect `docker logs <traefik-container>` if SSL is not issued")
    print("  - open several avatar URLs from deployment/generated/avatar_urls.json")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
