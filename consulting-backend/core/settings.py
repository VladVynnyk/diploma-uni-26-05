import os
from functools import cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


load_dotenv(Path(__file__).resolve().parent.parent / ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        case_sensitive=False,
    )

    db_uri: str = "postgresql+psycopg2://postgres:1234@db:5432/consultingdb"
    api_key: str = ""
    url_to_local_api: str = ""
    url_to_local_api_in_docker: str = ""

    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = os.getenv("AWS_REGION", os.getenv("AWS_DEFAULT_REGION", "eu-central-1"))
    avatars_bucket_name: str = ""
    avatars_base_url: str = ""
    use_s3_avatars: bool = False

    redis_host: str = "redis"
    redis_port: str = "6379"


@cache
def get_settings() -> Settings:
    return Settings()
