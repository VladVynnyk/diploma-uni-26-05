from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker


ROOT_DIR = Path(__file__).resolve().parents[2]
DEPLOYMENT_DIR = ROOT_DIR / "deployment"
DOTENV_PATH = DEPLOYMENT_DIR / ".env"
AVATAR_URLS_PATH = DEPLOYMENT_DIR / "generated" / "avatar_urls.json"
BACKEND_CORE_DIR = ROOT_DIR / "consulting-backend" / "core"

if str(BACKEND_CORE_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_CORE_DIR))

from database.models import User  # noqa: E402


def load_avatar_mapping(path: Path) -> dict[str, str]:
    if not path.exists():
        raise FileNotFoundError(f"Avatar mapping file was not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    consultant_email_urls = payload.get("consultant_email_urls")
    if not isinstance(consultant_email_urls, dict):
        raise ValueError(
            f"`consultant_email_urls` is missing or invalid in mapping file: {path}"
        )

    return {
        str(email): str(url)
        for email, url in consultant_email_urls.items()
        if email and url
    }


def main() -> int:
    load_dotenv(DOTENV_PATH)

    db_uri = os.getenv("DB_URI")
    if not db_uri:
        print(
            f"DB_URI is missing. Set it in {DOTENV_PATH} or your environment.",
            file=sys.stderr,
        )
        return 1

    try:
        consultant_email_urls = load_avatar_mapping(AVATAR_URLS_PATH)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"Using avatar mapping file: {AVATAR_URLS_PATH}")
    print(f"Found {len(consultant_email_urls)} consultant avatar URL mapping(s).")

    engine = create_engine(db_uri)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

    updated_emails: list[str] = []
    unchanged_emails: list[str] = []
    skipped_emails: list[str] = []

    with SessionLocal() as session:
        for email, url in consultant_email_urls.items():
            user = (
                session.execute(select(User).where(User.email == email))
                .unique()
                .scalar_one_or_none()
            )
            if user is None:
                skipped_emails.append(email)
                print(f"Skipped {email}: user not found in database.")
                continue

            if user.photo == url:
                unchanged_emails.append(email)
                print(f"Unchanged {email}: photo URL already up to date.")
                continue

            user.photo = url
            updated_emails.append(email)
            print(f"Updated {email}: photo URL synced from avatar mapping.")

        session.commit()

    print(f"Updated users: {len(updated_emails)}")
    print(f"Unchanged users: {len(unchanged_emails)}")
    print(f"Skipped users: {len(skipped_emails)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
