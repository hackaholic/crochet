#!/usr/bin/env bash
# bootstrap_secrets.sh - VPS service-scoped secret materialization (Task 3.3)
# Decrypts encrypted SOPS groups and materializes runtime secret files under /run/sulocraft/
# Enforces strict 0700/0600 permissions. Never logs secret values.
set -euo pipefail

TARGET_ENV="${TARGET_ENV:-${SULOCRAFT_ENV:-${APP_ENV:-preprod}}}"
SECRETS_DIR="${SECRETS_DIR:-}"
RUNTIME_SECRETS_ROOT="${RUNTIME_SECRETS_ROOT:-/run/sulocraft}"
RUNTIME_SECRETS_DIR="${RUNTIME_SECRETS_DIR:-}"
SOPS_AGE_KEY_FILE="${SOPS_AGE_KEY_FILE:-/etc/sulocraft/age/keys.txt}"
CLEANUP_ON_FAILURE="${CLEANUP_ON_FAILURE:-true}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --env) TARGET_ENV="$2"; shift 2 ;;
    --env=*) TARGET_ENV="${1#*=}"; shift ;;
    --secrets-dir) SECRETS_DIR="$2"; shift 2 ;;
    --secrets-dir=*) SECRETS_DIR="${1#*=}"; shift ;;
    --runtime-dir) RUNTIME_SECRETS_DIR="$2"; shift 2 ;;
    --runtime-dir=*) RUNTIME_SECRETS_DIR="${1#*=}"; shift ;;
    --key) SOPS_AGE_KEY_FILE="$2"; shift 2 ;;
    --key=*) SOPS_AGE_KEY_FILE="${1#*=}"; shift ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

case "${TARGET_ENV}" in
  preprod|prod|dev) ;;
  *) echo "Error: Unsupported target environment '${TARGET_ENV}'." >&2; exit 2 ;;
esac
RUNTIME_SECRETS_DIR="${RUNTIME_SECRETS_DIR:-${RUNTIME_SECRETS_ROOT%/}/${TARGET_ENV}}"

if [[ -z "${SECRETS_DIR}" ]]; then
  if [[ -d "secrets/encrypted/${TARGET_ENV}" ]]; then
    SECRETS_DIR="secrets/encrypted/${TARGET_ENV}"
  elif [[ -d "secrets/${TARGET_ENV}/encrypted" ]]; then
    SECRETS_DIR="secrets/${TARGET_ENV}/encrypted"
  elif [[ "${TARGET_ENV}" == "preprod" && -d "secrets/encrypted" ]]; then
    SECRETS_DIR="secrets/encrypted"
  else
    echo "Error: Encrypted secrets directory for environment '${TARGET_ENV}' not found; cannot fall back across environments." >&2
    exit 1
  fi
fi

echo "Initializing Sulocraft secret bootstrap (environment: ${TARGET_ENV})..."

# 1. Enforce strict umask
umask 077

# 2. Validate Age private key presence and permissions
if [[ ! -f "${SOPS_AGE_KEY_FILE}" ]]; then
  echo "Error: Required age private key file '${SOPS_AGE_KEY_FILE}' not found." >&2
  echo "Run bootstrap_vps_key.sh first or verify the key path." >&2
  exit 1
fi

key_perms=$(stat -c "%a" "${SOPS_AGE_KEY_FILE}" 2>/dev/null || stat -f "%Lp" "${SOPS_AGE_KEY_FILE}" 2>/dev/null || echo "600")
if [[ "${key_perms: -1}" != "0" || "${key_perms: -2:1}" != "0" ]]; then
  echo "Warning: Insecure permissions on age key file '${SOPS_AGE_KEY_FILE}' (${key_perms}). Tightening to 0600..." >&2
  chmod 600 "${SOPS_AGE_KEY_FILE}" 2>/dev/null || true
fi

# 3. Setup temporary working directory for decrypted buffers
TEMP_DEC_DIR=$(mktemp -d)
cleanup() {
  local exit_code=$?
  if [[ -d "${TEMP_DEC_DIR}" ]]; then
    rm -rf "${TEMP_DEC_DIR}"
  fi
  if [[ ${exit_code} -ne 0 && "${CLEANUP_ON_FAILURE}" == "true" ]]; then
    echo "Bootstrap failed (exit code ${exit_code}). Plaintext buffers purged." >&2
  fi
  exit "${exit_code}"
}
trap cleanup EXIT ERR INT TERM

# 4. Helper to decrypt a SOPS file into a destination buffer
decrypt_sops_group() {
  local enc_file="$1"
  local dest_file="$2"

  if [[ ! -f "${enc_file}" ]]; then
    echo "Error: Encrypted secrets file not found: '${enc_file}'" >&2
    return 1
  fi

  if command -v sops >/dev/null 2>&1; then
    SOPS_AGE_KEY_FILE="${SOPS_AGE_KEY_FILE}" sops --input-type dotenv --output-type dotenv -d "${enc_file}" > "${dest_file}"
  elif command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
    local enc_dir
    local enc_filename
    local key_dir
    local key_filename
    enc_dir=$(cd "$(dirname "${enc_file}")" && pwd)
    enc_filename=$(basename "${enc_file}")
    key_dir=$(cd "$(dirname "${SOPS_AGE_KEY_FILE}")" && pwd)
    key_filename=$(basename "${SOPS_AGE_KEY_FILE}")

    docker run --rm \
      -v "${enc_dir}:/secrets:ro" \
      -v "${key_dir}:/keys:ro" \
      -e "SOPS_AGE_KEY_FILE=/keys/${key_filename}" \
      ghcr.io/getsops/sops:v3.9.4-alpine --input-type dotenv --output-type dotenv -d "/secrets/${enc_filename}" > "${dest_file}"
  else
    echo "Error: Neither 'sops' CLI nor Docker is available to decrypt secrets." >&2
    return 1
  fi

  chmod 600 "${dest_file}"
  return 0
}

# 5. Helper to materialize key-value pairs into individual secret files
materialize_env_file() {
  local src_env="$1"
  local target_service_dir="$2"

  mkdir -p "${target_service_dir}"
  chmod 700 "${target_service_dir}"
  if [[ "$(id -u)" -eq 0 ]]; then
    chown root:root "${target_service_dir}" 2>/dev/null || true
  fi

  while IFS= read -r line || [[ -n "${line}" ]]; do
    # Skip comments and empty lines
    [[ "${line}" =~ ^[[:space:]]*# ]] && continue
    [[ -z "${line// }" ]] && continue

    # Parse KEY=VALUE
    if [[ "${line}" =~ ^[[:space:]]*([A-Za-z0-9_]+)[[:space:]]*=[[:space:]]*(.*)$ ]]; then
      local key="${BASH_REMATCH[1]}"
      local raw_val="${BASH_REMATCH[2]}"

      # Strip surrounding quotes if present
      if [[ "${raw_val}" =~ ^\"(.*)\"$ ]] || [[ "${raw_val}" =~ ^\'(.*)\'$ ]]; then
        raw_val="${BASH_REMATCH[1]}"
      fi

      local filename
      filename=$(echo "${key}" | tr '[:upper:]' '[:lower:]')
      local out_file="${target_service_dir}/${filename}"

      printf '%s' "${raw_val}" > "${out_file}"
      chmod 600 "${out_file}"
      if [[ "$(id -u)" -eq 0 ]]; then
        chown root:root "${out_file}" 2>/dev/null || true
      fi
    fi
  done < "${src_env}"
}

# 6. Create main runtime root
mkdir -p "${RUNTIME_SECRETS_DIR}"
chmod 700 "${RUNTIME_SECRETS_DIR}"
if [[ "$(id -u)" -eq 0 ]]; then
  chown root:root "${RUNTIME_SECRETS_DIR}" 2>/dev/null || true
fi

# 7. Process Service Groups
# A. PostgreSQL Group
PG_ENC=""
for candidate in "${SECRETS_DIR}/postgres.enc.env" "${SECRETS_DIR}/postgres.env" "${SECRETS_DIR}/postgres.enc.yaml"; do
  if [[ -f "${candidate}" ]]; then
    PG_ENC="${candidate}"
    break
  fi
done

if [[ -n "${PG_ENC}" ]]; then
  echo "Decrypting PostgreSQL secrets group from '${PG_ENC}'..."
  decrypt_sops_group "${PG_ENC}" "${TEMP_DEC_DIR}/postgres.env"
  materialize_env_file "${TEMP_DEC_DIR}/postgres.env" "${RUNTIME_SECRETS_DIR}/postgres"
else
  echo "Error: Missing PostgreSQL encrypted secrets file in '${SECRETS_DIR}'." >&2
  exit 1
fi

# B. Backend API Group
BACKEND_ENC=""
for candidate in "${SECRETS_DIR}/backend.enc.env" "${SECRETS_DIR}/backend.env" "${SECRETS_DIR}/backend.enc.yaml"; do
  if [[ -f "${candidate}" ]]; then
    BACKEND_ENC="${candidate}"
    break
  fi
done

if [[ -n "${BACKEND_ENC}" ]]; then
  echo "Decrypting Backend secrets group from '${BACKEND_ENC}'..."
  decrypt_sops_group "${BACKEND_ENC}" "${TEMP_DEC_DIR}/backend.env"
  materialize_env_file "${TEMP_DEC_DIR}/backend.env" "${RUNTIME_SECRETS_DIR}/backend"
else
  echo "Error: Missing Backend encrypted secrets file in '${SECRETS_DIR}'." >&2
  exit 1
fi

# C. Backup Group (Optional)
BACKUP_ENC=""
for candidate in "${SECRETS_DIR}/backup.enc.env" "${SECRETS_DIR}/backup.env" "${SECRETS_DIR}/backup.enc.yaml"; do
  if [[ -f "${candidate}" ]]; then
    BACKUP_ENC="${candidate}"
    break
  fi
done

if [[ -n "${BACKUP_ENC}" ]]; then
  echo "Decrypting Backup secrets group from '${BACKUP_ENC}'..."
  decrypt_sops_group "${BACKUP_ENC}" "${TEMP_DEC_DIR}/backup.env"
  materialize_env_file "${TEMP_DEC_DIR}/backup.env" "${RUNTIME_SECRETS_DIR}/backup"
fi

# 8. Validate Required Service Secrets
REQUIRED_SECRETS=(
  "${RUNTIME_SECRETS_DIR}/postgres/postgres_db"
  "${RUNTIME_SECRETS_DIR}/postgres/postgres_user"
  "${RUNTIME_SECRETS_DIR}/postgres/postgres_password"
  "${RUNTIME_SECRETS_DIR}/backend/database_url"
)

for req in "${REQUIRED_SECRETS[@]}"; do
  if [[ ! -s "${req}" ]]; then
    echo "Error: Required secret file '$(basename "${req}")' was not materialized or is empty in '$(dirname "${req}")'." >&2
    exit 1
  fi
done

python3 "$(dirname "$0")/validate_database_target.py" \
  "${RUNTIME_SECRETS_DIR}/postgres/postgres_db" \
  "${RUNTIME_SECRETS_DIR}/postgres/postgres_user" \
  "${RUNTIME_SECRETS_DIR}/postgres/postgres_password" \
  "${RUNTIME_SECRETS_DIR}/backend/database_url"

echo "Secret bootstrap completed successfully. Runtime secrets materialized under '${RUNTIME_SECRETS_DIR}'."
exit 0
