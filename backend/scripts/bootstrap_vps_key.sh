#!/usr/bin/env bash
# bootstrap_vps_key.sh - Safe VPS age-key bootstrap (Task 3.6)
# Provisions /etc/sulocraft/age/keys.txt with root:root 0600 permissions
# Never overwrites an existing key. Outputs only the public recipient.
set -euo pipefail

AGE_KEY_DIR="${AGE_KEY_DIR:-/etc/sulocraft/age}"
AGE_KEY_FILE="${AGE_KEY_FILE:-${AGE_KEY_DIR}/keys.txt}"

# 1. Check if key already exists - FAIL CLOSED without changing anything
if [[ -f "${AGE_KEY_FILE}" ]]; then
  echo "Error: Age key file already exists at '${AGE_KEY_FILE}'. Refusing to overwrite." >&2
  # If requested, display existing public recipient safely
  if grep -q "public key:" "${AGE_KEY_FILE}" 2>/dev/null; then
    existing_pub=$(grep -E "^[# ]*public key:" "${AGE_KEY_FILE}" | head -n 1 | awk '{print $NF}')
    if [[ "${existing_pub}" =~ ^age1 ]]; then
      echo "Existing public recipient: ${existing_pub}" >&2
    fi
  fi
  exit 1
fi

# 2. Enforce strict umask
umask 077

# 3. Create directory with mode 0700
mkdir -p "${AGE_KEY_DIR}"
chmod 700 "${AGE_KEY_DIR}"

if [[ "$(id -u)" -eq 0 ]]; then
  chown root:root "${AGE_KEY_DIR}" 2>/dev/null || true
fi

# 4. Generate age key
TEMP_KEY_FILE="${AGE_KEY_FILE}.tmp.$$"
trap 'rm -f "${TEMP_KEY_FILE}"' EXIT

if command -v age-keygen >/dev/null 2>&1; then
  age-keygen -o "${TEMP_KEY_FILE}" >/dev/null 2>&1
elif command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
  # Use ephemeral container without host package installation
  docker run --rm alpine sh -c "apk add --no-cache age >/dev/null 2>&1 && age-keygen" > "${TEMP_KEY_FILE}" 2>/dev/null
else
  # Minimal python fallback if neither binary nor docker is available in environment
  python3 -c "
import secrets

# Standard Bech32 / age key format generation fallback
# If age-keygen is not present, generate age-compatible key or raise
raise RuntimeError('age-keygen binary or Docker required to generate age key')
" 2>/dev/null || {
    echo "Error: age-keygen or Docker required to generate age key." >&2
    exit 1
  }
fi

if [[ ! -s "${TEMP_KEY_FILE}" ]]; then
  echo "Error: Generated key file is empty." >&2
  exit 1
fi

# 5. Restrict permissions to 0600
chmod 600 "${TEMP_KEY_FILE}"
if [[ "$(id -u)" -eq 0 ]]; then
  chown root:root "${TEMP_KEY_FILE}" 2>/dev/null || true
fi

mv "${TEMP_KEY_FILE}" "${AGE_KEY_FILE}"
trap - EXIT

# 6. Extract public recipient
PUBLIC_RECIPIENT=""
if grep -q "public key:" "${AGE_KEY_FILE}"; then
  PUBLIC_RECIPIENT=$(grep -E "^[# ]*public key:" "${AGE_KEY_FILE}" | head -n 1 | awk '{print $NF}')
elif command -v age-keygen >/dev/null 2>&1; then
  PUBLIC_RECIPIENT=$(age-keygen -y "${AGE_KEY_FILE}" 2>/dev/null || true)
fi

if [[ -z "${PUBLIC_RECIPIENT}" || ! "${PUBLIC_RECIPIENT}" =~ ^age1 ]]; then
  echo "Error: Failed to verify generated public recipient." >&2
  exit 1
fi

echo "VPS age key generated successfully."
echo "Public recipient: ${PUBLIC_RECIPIENT}"
exit 0
