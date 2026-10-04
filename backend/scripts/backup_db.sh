#!/usr/bin/env bash
# =============================================================================
# Sulocraft Database Automated Backup to Cloudflare R2
# Dumps PostgreSQL -> compresses with gzip -> uploads to private R2 bucket
# =============================================================================

set -euo pipefail

TARGET_ENV="${TARGET_ENV:-${SULOCRAFT_ENV:-${APP_ENV:-preprod}}}"
TIMESTAMP=$(date -u +"%Y%m%d_%H%M%S")
BACKUP_DIR="${BACKUP_DIR:-/tmp/sulocraft_backups}"
BACKUP_FILE="${BACKUP_DIR}/sulocraft_db_${TIMESTAMP}.sql.gz"
mkdir -p "${BACKUP_DIR}"

# Helper to resolve secret from *_FILE, /run/secrets, or environment
read_secret() {
    local var_name="$1"
    local file_var_name="${var_name}_FILE"
    local file_path="${!file_var_name:-}"

    if [ -n "${file_path}" ]; then
        if [ -r "${file_path}" ]; then
            head -n 1 "${file_path}" | tr -d '\r\n'
            return 0
        else
            echo "Error: Configured secret file for ${var_name} could not be read" >&2
            return 1
        fi
    fi

    local var_lower
    var_lower="$(echo "${var_name}" | tr '[:upper:]' '[:lower:]')"
    for candidate_dir in "/run/secrets/backups" "/run/secrets"; do
        if [ -f "${candidate_dir}/${var_lower}" ]; then
            if [ -r "${candidate_dir}/${var_lower}" ]; then
                head -n 1 "${candidate_dir}/${var_lower}" | tr -d '\r\n'
                return 0
            else
                echo "Error: Secret file for ${var_name} could not be read" >&2
                return 1
            fi
        fi
    done

    local val="${!var_name:-}"
    if [ -n "${val}" ]; then
        printf '%s' "${val}"
        return 0
    fi

    return 2
}

DB_HOST="${DB_HOST:-postgres}"
DB_PORT="${DB_PORT:-5432}"

if DB_USER_VAL=$(read_secret "POSTGRES_USER"); then
    DB_USER="${DB_USER_VAL}"
else
    DB_USER="${POSTGRES_USER:-sulocraft}"
fi

if DB_NAME_VAL=$(read_secret "POSTGRES_DB"); then
    DB_NAME="${DB_NAME_VAL}"
else
    DB_NAME="${POSTGRES_DB:-sulocraft}"
fi

if PGPASSWORD=$(read_secret "POSTGRES_PASSWORD"); then
    export PGPASSWORD
else
    echo "Error: Database password must be supplied via POSTGRES_PASSWORD_FILE, secret mount, or POSTGRES_PASSWORD" >&2
    exit 1
fi

echo "==> [$(date -u)] Starting Sulocraft PostgreSQL database backup..."
pg_dump -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" | gzip > "${BACKUP_FILE}"
FILESIZE=$(ls -lh "${BACKUP_FILE}" | awk '{print $5}')
echo "==> [$(date -u)] Backup created successfully: ${BACKUP_FILE} (${FILESIZE})"

# Resolve Cloudflare R2 credentials (dedicated backup credentials take precedence)
R2_KEY=""
if val=$(read_secret "BACKUP_R2_ACCESS_KEY_ID"); then
    R2_KEY="${val}"
elif val=$(read_secret "R2_ACCESS_KEY_ID"); then
    R2_KEY="${val}"
fi

R2_SECRET=""
if val=$(read_secret "BACKUP_R2_SECRET_ACCESS_KEY"); then
    R2_SECRET="${val}"
elif val=$(read_secret "R2_SECRET_ACCESS_KEY"); then
    R2_SECRET="${val}"
fi

ENDPOINT="${BACKUP_R2_ENDPOINT:-${R2_ENDPOINT:-}}"
if [ "${TARGET_ENV}" = "production" ] || [ "${TARGET_ENV}" = "prod" ]; then
    DEFAULT_BACKUP_BUCKET="sulocraft-backups"
else
    DEFAULT_BACKUP_BUCKET="sulocraft-backups-${TARGET_ENV}"
fi
BUCKET="${BACKUP_R2_BUCKET:-${R2_PRIVATE_BACKUP_BUCKET:-${DEFAULT_BACKUP_BUCKET}}}"

if [ -n "${ENDPOINT}" ] && [ -n "${R2_KEY}" ] && [ -n "${R2_SECRET}" ]; then
    echo "==> [$(date -u)] Uploading backup archive to Cloudflare R2 bucket: ${BUCKET}..."
    BACKUP_R2_ENDPOINT="${ENDPOINT}" \
    BACKUP_R2_ACCESS_KEY_ID="${R2_KEY}" \
    BACKUP_R2_SECRET_ACCESS_KEY="${R2_SECRET}" \
    BACKUP_R2_BUCKET="${BUCKET}" \
    BACKUP_FILE_PATH="${BACKUP_FILE}" \
    BACKUP_OBJECT_NAME="database/${TARGET_ENV}/sulocraft_db_${TIMESTAMP}.sql.gz" \
    python3 - <<'PY'
import os
import boto3
from botocore.config import Config

endpoint = os.environ["BACKUP_R2_ENDPOINT"]
key_id = os.environ["BACKUP_R2_ACCESS_KEY_ID"]
secret = os.environ["BACKUP_R2_SECRET_ACCESS_KEY"]
bucket = os.environ["BACKUP_R2_BUCKET"]
file_path = os.environ["BACKUP_FILE_PATH"]
object_name = os.environ["BACKUP_OBJECT_NAME"]

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
