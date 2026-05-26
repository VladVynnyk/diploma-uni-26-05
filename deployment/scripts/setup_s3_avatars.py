from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[2]
DEPLOYMENT_DIR = ROOT_DIR / "deployment"
INFRA_DIR = DEPLOYMENT_DIR / "infra" / "s3_avatars"
UPLOAD_SCRIPT = DEPLOYMENT_DIR / "scripts" / "upload_avatars_to_s3.py"
SYNC_SCRIPT = DEPLOYMENT_DIR / "scripts" / "sync_avatar_urls_to_db.py"
OUTPUT_PATH = DEPLOYMENT_DIR / "generated" / "avatar_urls.json"
DOTENV_PATH = DEPLOYMENT_DIR / ".env"


def ensure_command_exists(command_name: str) -> None:
    if shutil.which(command_name) is None:
        raise RuntimeError(
            f"`{command_name}` is not installed or is not available in PATH."
        )


def run_command(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=str(cwd),
        check=True,
        capture_output=True,
        text=True,
    )


def terraform_outputs() -> dict[str, str]:
    output = run_command(["terraform", "output", "-json"], INFRA_DIR)
    payload = json.loads(output.stdout)
    return {
        "bucket_name": payload["bucket_name"]["value"],
        "region": payload["region"]["value"],
        "base_url": payload["base_url"]["value"],
    }


def main() -> int:
    load_dotenv(DOTENV_PATH)

    try:
        ensure_command_exists("terraform")
    except RuntimeError as exc:
        print(exc, file=sys.stderr)
        return 1

    bucket_name = os.getenv("AVATARS_BUCKET_NAME") or os.getenv("TF_VAR_avatars_bucket_name")
    if not bucket_name:
        print(
            f"Set AVATARS_BUCKET_NAME or TF_VAR_avatars_bucket_name in {DOTENV_PATH} or your environment before running this script.",
            file=sys.stderr,
        )
        return 1

    aws_region = os.getenv("AWS_DEFAULT_REGION") or os.getenv("AWS_REGION")

    print(f"Running Terraform in {INFRA_DIR}")
    try:
        init_result = run_command(["terraform", "init"], INFRA_DIR)
        print(init_result.stdout)

        apply_command = [
            "terraform",
            "apply",
            "-auto-approve",
            f"-var=avatars_bucket_name={bucket_name}",
        ]
        if aws_region:
            apply_command.append(f"-var=aws_region={aws_region}")
        apply_result = run_command(apply_command, INFRA_DIR)
        print(apply_result.stdout)

        outputs = terraform_outputs()
    except subprocess.CalledProcessError as exc:
        print(f"Terraform command failed: {' '.join(exc.cmd)}", file=sys.stderr)
        if exc.stdout:
            print(exc.stdout, file=sys.stderr)
        if exc.stderr:
            print(exc.stderr, file=sys.stderr)
        return 1

    print(
        f"Terraform ready. Bucket: {outputs['bucket_name']} Region: {outputs['region']} Base URL: {outputs['base_url']}"
    )

    upload_command = [
        sys.executable,
        str(UPLOAD_SCRIPT),
        "--bucket-name",
        outputs["bucket_name"],
        "--aws-region",
        outputs["region"],
    ]
    print(f"Running upload script: {UPLOAD_SCRIPT}")
    try:
        upload_result = run_command(upload_command, ROOT_DIR)
        print(upload_result.stdout)
        if upload_result.stderr:
            print(upload_result.stderr, file=sys.stderr)
    except subprocess.CalledProcessError as exc:
        print("Avatar upload failed.", file=sys.stderr)
        if exc.stdout:
            print(exc.stdout, file=sys.stderr)
        if exc.stderr:
            print(exc.stderr, file=sys.stderr)
        return 1

    sync_command = [
        sys.executable,
        str(SYNC_SCRIPT),
    ]
    print(f"Running DB sync script: {SYNC_SCRIPT}")
    try:
        sync_result = run_command(sync_command, ROOT_DIR)
        print(sync_result.stdout)
        if sync_result.stderr:
            print(sync_result.stderr, file=sys.stderr)
    except subprocess.CalledProcessError as exc:
        print("Avatar URL database sync failed.", file=sys.stderr)
        if exc.stdout:
            print(exc.stdout, file=sys.stderr)
        if exc.stderr:
            print(exc.stderr, file=sys.stderr)
        return 1

    print(f"Avatar mapping saved to {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
