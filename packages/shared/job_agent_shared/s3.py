from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import boto3
import os


@dataclass(frozen=True)
class S3Url:
    bucket: str
    key: str

    @staticmethod
    def parse(url: str) -> "S3Url":
        if not url.startswith("s3://"):
            raise ValueError("Invalid S3 URL: must start with s3://")
        path = url[len("s3://") :]
        parts = path.split("/", 1)
        if len(parts) != 2 or not parts[0] or not parts[1]:
            raise ValueError("Invalid S3 URL: expected s3://bucket/key")
        return S3Url(bucket=parts[0], key=parts[1])


def build_s3_client():
    endpoint_url = os.getenv("S3_ENDPOINT_URL")  # e.g., http://minio:9000
    access_key = os.getenv("S3_ACCESS_KEY", os.getenv("MINIO_ROOT_USER"))
    secret_key = os.getenv("S3_SECRET_KEY", os.getenv("MINIO_ROOT_PASSWORD"))
    kwargs: dict = {}
    if endpoint_url:
        kwargs["endpoint_url"] = endpoint_url
    if access_key and secret_key:
        kwargs["aws_access_key_id"] = access_key
        kwargs["aws_secret_access_key"] = secret_key
    # MinIO uses path-style by default; boto3 will handle both.
    return boto3.client("s3", **kwargs)


