#!/usr/bin/env bash
set -euo pipefail

TARGET_ENV="${TARGET_ENV:-${SULOCRAFT_ENV:-${APP_ENV:-preprod}}}"
DEPLOY_HOST="${DEPLOY_HOST:-root@201.18.212.183}"
DEPLOY_ROOT="${DEPLOY_ROOT:-/opt/sulocraft}"
DEPLOY_ENV_FILE="${DEPLOY_ENV_FILE:-backend/.env.${TARGET_ENV}}"
SSH_IDENTITY_FILE="${SSH_IDENTITY_FILE:-}"
SSH_KNOWN_HOSTS_FILE="${SSH_KNOWN_HOSTS_FILE:-}"
RELEASE_ID="${RELEASE_ID:-$(date -u +%Y%m%dT%H%M%SZ)}"
RELEASE_DIR="${DEPLOY_ROOT}/releases/${RELEASE_ID}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --env) TARGET_ENV="$2"; shift 2 ;;
    --env=*) TARGET_ENV="${1#*=}"; shift ;;
    --host) DEPLOY_HOST="$2"; shift 2 ;;
    --host=*) DEPLOY_HOST="${1#*=}"; shift ;;
    --root) DEPLOY_ROOT="$2"; shift 2 ;;
    --root=*) DEPLOY_ROOT="${1#*=}"; shift ;;
    *) shift ;;
  esac
done

SSH_OPTIONS=(-o BatchMode=yes)
RSYNC_SSH_COMMAND="ssh -o BatchMode=yes"
if [[ -n "${SSH_IDENTITY_FILE}" ]]; then
  SSH_OPTIONS+=(-i "${SSH_IDENTITY_FILE}" -o IdentitiesOnly=yes)
  RSYNC_SSH_COMMAND+=" -i ${SSH_IDENTITY_FILE} -o IdentitiesOnly=yes"
fi
if [[ -n "${SSH_KNOWN_HOSTS_FILE}" ]]; then
  SSH_OPTIONS+=(-o "UserKnownHostsFile=${SSH_KNOWN_HOSTS_FILE}" -o StrictHostKeyChecking=yes)
  RSYNC_SSH_COMMAND+=" -o UserKnownHostsFile=${SSH_KNOWN_HOSTS_FILE} -o StrictHostKeyChecking=yes"
fi

SECRETS_DIR="${SECRETS_DIR:-secrets/encrypted}"

for command in ssh rsync; do
  command -v "${command}" >/dev/null || { echo "Required command not found: ${command}"; exit 1; }
done

echo "Deploying Sulocraft release ${RELEASE_ID} to ${DEPLOY_HOST}:${RELEASE_DIR}"
ssh "${SSH_OPTIONS[@]}" "${DEPLOY_HOST}" "mkdir -p '${RELEASE_DIR}' '${DEPLOY_ROOT}/shared'"

# Transfer release files excluding git, plaintext env files, build artifacts, and virtual environments
rsync -az --delete -e "${RSYNC_SSH_COMMAND}" \
  --exclude '.git/' \
  --exclude '.env*' \
  --exclude 'node_modules/' \
  --exclude 'dist/' \
  --exclude 'backend/.venv/' \
  --exclude '**/__pycache__/' \
  ./ "${DEPLOY_HOST}:${RELEASE_DIR}/"

# Preserve a database snapshot from the currently running release before the
# new release or migrations are applied. The first deployment has no DB yet.
ssh "${SSH_OPTIONS[@]}" "${DEPLOY_HOST}" "bash -s" -- "${DEPLOY_ROOT}" <<'REMOTE_BACKUP'
set -euo pipefail
deploy_root="$1"
current_release="$(readlink -f "${deploy_root}/current" 2>/dev/null || true)"
if [[ -n "${current_release}" && -f "${current_release}/backend/docker-compose.yml" ]]; then
  mkdir -p "${deploy_root}/backups"
  backup_file="${deploy_root}/backups/predeploy_$(date -u +%Y%m%dT%H%M%SZ).sql.gz"
  compose_cmd=(docker compose -p sulocraft -f "${current_release}/backend/docker-compose.yml")
  if [[ -f "${deploy_root}/shared/.env" ]]; then
    compose_cmd+=(--env-file "${deploy_root}/shared/.env")
  fi
  if "${compose_cmd[@]}" ps --status running postgres --quiet | grep -q .; then
    "${compose_cmd[@]}" exec -T postgres sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' | gzip > "${backup_file}"
    chmod 600 "${backup_file}"
    echo "Database backup created: ${backup_file}"
  fi
fi
REMOTE_BACKUP

# Remote Bootstrap and Compose Execution
ssh "${SSH_OPTIONS[@]}" "${DEPLOY_HOST}" "bash -s" -- "${DEPLOY_ROOT}" "${RELEASE_DIR}" "${TARGET_ENV}" <<'REMOTE'
set -euo pipefail
deploy_root="$1"
release_dir="$2"
target_env="$3"
cd "${release_dir}"

# 1. Bootstrap secrets if encrypted groups exist
if [[ -f "${release_dir}/backend/scripts/bootstrap_secrets.sh" ]]; then
  echo "Bootstrapping encrypted secrets on host (environment: ${target_env})..."
  SOPS_AGE_KEY_FILE="/etc/sulocraft/age/keys.txt" \
  RUNTIME_SECRETS_DIR="/run/sulocraft" \
  bash "${release_dir}/backend/scripts/bootstrap_secrets.sh" --env "${target_env}"
fi

# 2. Build compose command
compose_cmd=(docker compose -p sulocraft -f backend/docker-compose.yml)
if [[ -f "${deploy_root}/shared/.env" ]]; then
  compose_cmd+=(--env-file "${deploy_root}/shared/.env")
fi

# 3. Start services
if ! "${compose_cmd[@]}" up -d --build --remove-orphans; then
  "${compose_cmd[@]}" ps
  "${compose_cmd[@]}" logs --tail=150 api postgres reverse-proxy
  echo "Deployment failed while starting the Compose stack; current symlink was not changed."
  exit 1
fi

# 4. Validate health
for attempt in $(seq 1 30); do
  if curl --fail --silent http://127.0.0.1/health >/dev/null; then
    ln -sfn "${release_dir}" "${deploy_root}/current"
    printf '%s\n' "${release_dir}" > "${deploy_root}/shared/last-successful-release"
    "${compose_cmd[@]}" ps
    echo "Sulocraft API health check passed."
    exit 0
  fi
  sleep 2
done

"${compose_cmd[@]}" ps
"${compose_cmd[@]}" logs --tail=150 api reverse-proxy
echo "Deployment failed health validation; current symlink was not changed."
exit 1
REMOTE

echo "Deployment complete: ${RELEASE_ID}"
