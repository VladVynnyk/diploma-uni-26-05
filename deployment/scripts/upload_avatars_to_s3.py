from __future__ import annotations

import argparse
import json
import mimetypes
import sys
from pathlib import Path

try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError
except ImportError as exc:  # pragma: no cover - environment dependent
    print(
        "boto3 is not installed. Install backend dependencies or run `pip install boto3` before uploading avatars.",
        file=sys.stderr,
    )
    raise SystemExit(1) from exc


SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
ROOT_DIR = Path(__file__).resolve().parents[2]
DEFAULT_PHOTOS_DIR = ROOT_DIR / "photos"
DEFAULT_MANIFEST_PATH = ROOT_DIR / "deployment" / "avatar_manifest.json"
DEFAULT_OUTPUT_PATH = ROOT_DIR / "deployment" / "generated" / "avatar_urls.json"


def load_manifest(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ValueError(f"Avatar manifest must be a JSON object: {path}")
    return {str(key): str(value) for key, value in data.items()}


def collect_avatar_files(photos_dir: Path) -> list[Path]:
    files = sorted(
        path for path in photos_dir.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )
    return files


def upload_file(s3_client, bucket_name: str, file_path: Path, object_key: str) -> None:
    content_type, _ = mimetypes.guess_type(file_path.name)
    extra_args = {"ContentType": content_type or "application/octet-stream"}
    s3_client.upload_file(str(file_path), bucket_name, object_key, ExtraArgs=extra_args)


def build_output(base_url: str, prefix: str, files: list[Path], manifest: dict[str, str]) -> dict[str, dict[str, str]]:
    normalized_prefix = prefix.strip("/")
    file_urls = {
        file_path.name: f"{base_url}/{normalized_prefix}/{file_path.name}"
        for file_path in files
    }
    consultant_email_urls = {
        email: file_urls[file_name]
        for email, file_name in manifest.items()
        if file_name in file_urls
    }
    return {
        "file_urls": file_urls,
        "consultant_email_urls": consultant_email_urls,
    }


def print_manifest_warnings(files: list[Path], manifest: dict[str, str]) -> None:
    available_names = {file_path.name for file_path in files}
    missing_files = sorted(
        f"{email} -> {file_name}"
        for email, file_name in manifest.items()
        if file_name not in available_names
    )
    for item in missing_files:
        print(f"Warning: manifest entry points to a missing local file: {item}", file=sys.stderr)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Upload consultant avatar images to S3.")
    parser.add_argument("--bucket-name", required=True, help="Target S3 bucket name.")
    parser.add_argument("--aws-region", required=True, help="AWS region of the bucket.")
    parser.add_argument("--photos-dir", default=str(DEFAULT_PHOTOS_DIR), help="Local directory with avatar images.")
    parser.add_argument("--manifest-path", default=str(DEFAULT_MANIFEST_PATH), help="Path to consultant email -> filename JSON manifest.")
    parser.add_argument("--output-path", default=str(DEFAULT_OUTPUT_PATH), help="Path where avatar URL mapping JSON will be written.")
    parser.add_argument("--prefix", default="avatars", help="S3 object key prefix for uploaded avatars.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    photos_dir = Path(args.photos_dir).resolve()
    manifest_path = Path(args.manifest_path).resolve()
    output_path = Path(args.output_path).resolve()
    prefix = args.prefix.strip("/")

    if not photos_dir.exists():
        print(f"Photos directory does not exist: {photos_dir}", file=sys.stderr)
        return 1

    manifest = load_manifest(manifest_path)
    files = collect_avatar_files(photos_dir)
    print(f"Found {len(files)} avatar file(s) in {photos_dir}")
    print_manifest_warnings(files, manifest)

    if not files:
        print("No supported avatar files found. Nothing to upload.", file=sys.stderr)
        return 1

    s3_client = boto3.client("s3", region_name=args.aws_region)
    base_url = f"https://{args.bucket_name}.s3.{args.aws_region}.amazonaws.com"

    uploaded_files: list[str] = []
    for file_path in files:
        object_key = f"{prefix}/{file_path.name}"
        try:
            upload_file(s3_client, args.bucket_name, file_path, object_key)
        except (ClientError, BotoCoreError) as exc:
            print(f"Failed to upload {file_path.name}: {exc}", file=sys.stderr)
            return 1
        uploaded_files.append(file_path.name)
        print(f"Uploaded {file_path.name} -> s3://{args.bucket_name}/{object_key}")

    output_payload = build_output(base_url, prefix, files, manifest)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(output_payload, file, ensure_ascii=False, indent=2)

    print(f"Uploaded {len(uploaded_files)} file(s).")
    print(f"Saved avatar URL mapping to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
