#!/usr/bin/env bash
set -euo pipefail

ENDPOINT="${S3_ENDPOINT_URL:-http://localhost:9000}"
ACCESS="${S3_ACCESS_KEY:-minio}"
SECRET="${S3_SECRET_KEY:-minio12345}"

mc alias set local "$ENDPOINT" "$ACCESS" "$SECRET" --api S3v4 || true
mc mb -p local/resumes || true
touch /tmp/backend.pdf /tmp/fullstack.pdf /tmp/data.pdf
mc cp /tmp/backend.pdf local/resumes/backend.pdf
mc cp /tmp/fullstack.pdf local/resumes/fullstack.pdf
mc cp /tmp/data.pdf local/resumes/data.pdf
echo "Seeded MinIO with sample resumes."


