#!/usr/bin/env bash
# =============================================================================
# Sulocraft Database Automated Backup to Cloudflare R2
# Dumps PostgreSQL -> compresses with gzip -> uploads to private R2 bucket
# =============================================================================

set -euo pipefail

TIMESTAMP=$(date -u +"%Y%m%d_%H%M%S")
BACKUP_DIR="${BACKUP_DIR:-/tmp/sulocraft_backups}"
BACKUP_FILE="${BACKUP_DIR}/sulocraft_db_${TIMESTAMP}.sql.gz"
mkdir -p "${BACKUP_DIR}"

DB_HOST="${DB_HOST:-postgres}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${POSTGRES_DB:-sulocraft}"
DB_USER="${POSTGRES_USER:-sulocraft}"
PGPASSWORD="${POSTGRES_PASSWORD:-sulocraft_secure_pw}"
export PGPASSWORD

echo "==> [$(date -u)] Starting Sulocraft PostgreSQL database backup..."
pg_dump -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" | gzip > "${BACKUP_FILE}"
FILESIZE=$(ls -lh "${BACKUP_FILE}" | awk '{print $5}')
echo "==> [$(date -u)] Backup created successfully: ${BACKUP_FILE} (${FILESIZE})"

# Upload to Cloudflare R2 if credentials provided
if [ -n "${R2_ENDPOINT:-}" ] && [ -n "${R2_ACCESS_KEY_ID:-}" ] && [ -n "${R2_SECRET_ACCESS_KEY:-}" ]; then
    R2_BUCKET="${R2_PRIVATE_BACKUP_BUCKET:-sulocraft-backups}"
    echo "==> [$(date -u)] Uploading backup archive to Cloudflare R2 bucket: ${R2_BUCKET}..."
    python3 - <<PY
import os
import boto3
from botocore.config import Config

endpoint = os.environ["R2_ENDPOINT"]
key_id = os.environ["R2_ACCESS_KEY_ID"]
secret = os.environ["R2_SECRET_ACCESS_KEY"]
bucket = os.environ.get("R2_PRIVATE_BACKUP_BUCKET", "sulocraft-backups")
file_path = "${BACKUP_FILE}"
object_name = f"database/sulocraft_db_${TIMESTAMP}.sql.gz"

s3 = boto3.client(
    "s3",
    endpoint_url=endpoint,
    aws_access_key_id=key_id,
    aws_secret_access_key=secret,
    config=Config(signature_version="s3v4"),
    region_name="auto",
)
s3.upload_file(file_path, bucket, object_name)
print(f"Uploaded {file_path} to R2: {bucket}/{object_name}")
PY
    echo "==> [$(date -u)] Cloudflare R2 upload complete."
else
    echo "==> [$(date -u)] Cloudflare R2 credentials not configured. Preserving local backup at ${BACKUP_FILE}."
fi
