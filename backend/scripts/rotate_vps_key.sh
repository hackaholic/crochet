#!/usr/bin/env bash
# rotate_vps_key.sh - Guarded age-key rotation automation (Task 3.7)
# Generates candidate keys without overwriting active keys.
# Validates candidate decryption, supports atomic promotion and rollback.
set -euo pipefail

AGE_KEY_DIR="${AGE_KEY_DIR:-/etc/sulocraft/age}"
ACTIVE_KEY_FILE="${ACTIVE_KEY_FILE:-${AGE_KEY_DIR}/keys.txt}"
CANDIDATE_KEY_FILE="${CANDIDATE_KEY_FILE:-${AGE_KEY_DIR}/keys.txt.candidate}"
SECRETS_DIR="${SECRETS_DIR:-secrets/encrypted}"

umask 077

action="${1:---generate}"

case "${action}" in
  --generate)
    echo "Staging candidate age key for rotation..."
    if [[ -f "${CANDIDATE_KEY_FILE}" ]]; then
      echo "Error: Candidate key already exists at '${CANDIDATE_KEY_FILE}'." >&2
      echo "Verify and promote or remove it before generating a new one." >&2
      exit 1
    fi

    mkdir -p "${AGE_KEY_DIR}"
    chmod 700 "${AGE_KEY_DIR}"

    TEMP_KEY="${CANDIDATE_KEY_FILE}.tmp.$$"
    trap 'rm -f "${TEMP_KEY}"' EXIT

    if command -v age-keygen >/dev/null 2>&1; then
      age-keygen -o "${TEMP_KEY}" >/dev/null 2>&1
    elif command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
      docker run --rm alpine sh -c "apk add --no-cache age >/dev/null 2>&1 && age-keygen" > "${TEMP_KEY}" 2>/dev/null
    else
      echo "Error: age-keygen or Docker required to generate candidate key." >&2
      exit 1
    fi

    chmod 600 "${TEMP_KEY}"
    if [[ "$(id -u)" -eq 0 ]]; then
      chown root:root "${TEMP_KEY}" 2>/dev/null || true
    fi
    mv "${TEMP_KEY}" "${CANDIDATE_KEY_FILE}"
    trap - EXIT

    CANDIDATE_PUB=$(grep -E "^[# ]*public key:" "${CANDIDATE_KEY_FILE}" | head -n 1 | awk '{print $NF}')
    echo "Candidate key staged at '${CANDIDATE_KEY_FILE}'."
    echo "Candidate public recipient: ${CANDIDATE_PUB}"
    echo "Next steps:"
    echo "  1. Add ${CANDIDATE_PUB} to .sops.yaml"
    echo "  2. Re-encrypt all groups with sops updatekeys"
    echo "  3. Run '$0 --verify' to verify decryption"
    echo "  4. Run '$0 --promote' after successful verification"
    ;;

  --verify)
    echo "Verifying encrypted secret groups can be decrypted by candidate key..."
    if [[ ! -f "${CANDIDATE_KEY_FILE}" ]]; then
      echo "Error: Candidate key '${CANDIDATE_KEY_FILE}' not found. Generate one with --generate." >&2
      exit 1
    fi

    if [[ ! -d "${SECRETS_DIR}" ]]; then
      echo "Warning: Secrets directory '${SECRETS_DIR}' does not exist. Nothing to verify."
      exit 0
    fi

    shopt -s nullglob
    enc_files=("${SECRETS_DIR}"/*.enc.*)
    shopt -u nullglob

    if [[ ${#enc_files[@]} -eq 0 ]]; then
      echo "Warning: No encrypted files matching '*.enc.*' in '${SECRETS_DIR}'."
      exit 0
    fi

    for file in "${enc_files[@]}"; do
      echo "Testing decryption of $(basename "${file}")..."
      if command -v sops >/dev/null 2>&1; then
        SOPS_AGE_KEY_FILE="${CANDIDATE_KEY_FILE}" sops --input-type dotenv --output-type dotenv -d "${file}" >/dev/null
      elif command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
        enc_dir=$(cd "$(dirname "${file}")" && pwd)
        enc_name=$(basename "${file}")
        cand_dir=$(cd "$(dirname "${CANDIDATE_KEY_FILE}")" && pwd)
        cand_name=$(basename "${CANDIDATE_KEY_FILE}")
        docker run --rm \
          -v "${enc_dir}:/secrets:ro" \
          -v "${cand_dir}:/keys:ro" \
          -e "SOPS_AGE_KEY_FILE=/keys/${cand_name}" \
          ghcr.io/getsops/sops:v3.9.4-alpine --input-type dotenv --output-type dotenv -d "/secrets/${enc_name}" >/dev/null
      else
        echo "Error: No sops tool available." >&2
        exit 1
      fi
    done
    echo "All encrypted groups successfully decrypted with candidate key."
    ;;

  --promote)
    echo "Promoting candidate age key to active..."
    if [[ ! -f "${CANDIDATE_KEY_FILE}" ]]; then
      echo "Error: Candidate key '${CANDIDATE_KEY_FILE}' does not exist." >&2
      exit 1
    fi

    if [[ -f "${ACTIVE_KEY_FILE}" ]]; then
      backup_file="${ACTIVE_KEY_FILE}.backup.$(date -u +%Y%m%dT%H%M%SZ)"
      cp -p "${ACTIVE_KEY_FILE}" "${backup_file}"
      chmod 600 "${backup_file}"
      echo "Archived active key to '${backup_file}'."
    fi

    mv "${CANDIDATE_KEY_FILE}" "${ACTIVE_KEY_FILE}"
    chmod 600 "${ACTIVE_KEY_FILE}"
    echo "Candidate key promoted to active: '${ACTIVE_KEY_FILE}'."
    ;;

  --rollback)
    echo "Rolling back to most recent backup key..."
    shopt -s nullglob
    backups=("${ACTIVE_KEY_FILE}".backup.*)
    shopt -u nullglob

    if [[ ${#backups[@]} -eq 0 ]]; then
      echo "Error: No backup key files found matching '${ACTIVE_KEY_FILE}.backup.*'." >&2
      exit 1
    fi

    # Pick the most recent backup
    latest_backup=$(printf '%s\n' "${backups[@]}" | sort | tail -n 1)
    echo "Restoring from '${latest_backup}'..."
    cp -p "${latest_backup}" "${ACTIVE_KEY_FILE}"
    chmod 600 "${ACTIVE_KEY_FILE}"
    echo "Active key restored from backup: '${ACTIVE_KEY_FILE}'."
    ;;

  *)
    echo "Usage: $0 [--generate | --verify | --promote | --rollback]"
    exit 1
    ;;
esac

exit 0
