#!/usr/bin/env bash
set -euo pipefail

DEPLOY_HOST="${DEPLOY_HOST:-sulocraft-deploy@201.18.212.183}"
DEPLOY_ROOT="${DEPLOY_ROOT:-/opt/sulocraft}"
DEPLOY_ENV_FILE="${DEPLOY_ENV_FILE:-backend/.env.preprod}"
SSH_IDENTITY_FILE="${SSH_IDENTITY_FILE:-}"
SSH_KNOWN_HOSTS_FILE="${SSH_KNOWN_HOSTS_FILE:-}"
RELEASE_ID="${RELEASE_ID:-$(date -u +%Y%m%dT%H%M%SZ)}"
RELEASE_DIR="${DEPLOY_ROOT}/releases/${RELEASE_ID}"

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

if [[ ! -f "${DEPLOY_ENV_FILE}" ]]; then
  echo "Missing ${DEPLOY_ENV_FILE}. Copy backend/.env.preprod.example and fill it locally."
  exit 1
fi

for command in ssh scp rsync; do
  command -v "${command}" >/dev/null || { echo "Required command not found: ${command}"; exit 1; }
done

echo "Deploying Sulocraft release ${RELEASE_ID} to ${DEPLOY_HOST}:${RELEASE_DIR}"
ssh "${SSH_OPTIONS[@]}" "${DEPLOY_HOST}" "mkdir -p '${RELEASE_DIR}' '${DEPLOY_ROOT}/shared'"

rsync -az --delete -e "${RSYNC_SSH_COMMAND}" \
  --exclude '.git/' \
  --exclude '.env*' \
  --exclude 'node_modules/' \
  --exclude 'dist/' \
  --exclude 'backend/.venv/' \
  --exclude '**/__pycache__/' \
  ./ "${DEPLOY_HOST}:${RELEASE_DIR}/"

# Preserve a database snapshot from the currently running release before the
# new environment or migrations are applied. The first deployment has no DB yet.
ssh "${SSH_OPTIONS[@]}" "${DEPLOY_HOST}" "bash -s" -- "${DEPLOY_ROOT}" <<'REMOTE_BACKUP'
set -euo pipefail
deploy_root="$1"
current_release="$(readlink -f "${deploy_root}/current" 2>/dev/null || true)"
if [[ -n "${current_release}" && -f "${current_release}/backend/docker-compose.yml" ]]; then
  mkdir -p "${deploy_root}/backups"
  backup_file="${deploy_root}/backups/predeploy_$(date -u +%Y%m%dT%H%M%SZ).sql.gz"
  if docker compose -p sulocraft --env-file "${deploy_root}/shared/.env" -f "${current_release}/backend/docker-compose.yml" ps --status running postgres --quiet | grep -q .; then
    docker compose -p sulocraft --env-file "${deploy_root}/shared/.env" -f "${current_release}/backend/docker-compose.yml" \
      exec -T postgres sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' | gzip > "${backup_file}"
    chmod 600 "${backup_file}"
    echo "Database backup created: ${backup_file}"
  fi
fi
REMOTE_BACKUP

scp "${SSH_OPTIONS[@]}" "${DEPLOY_ENV_FILE}" "${DEPLOY_HOST}:${DEPLOY_ROOT}/shared/.env"
ssh "${SSH_OPTIONS[@]}" "${DEPLOY_HOST}" "chmod 600 '${DEPLOY_ROOT}/shared/.env'"

ssh "${SSH_OPTIONS[@]}" "${DEPLOY_HOST}" "bash -s" -- "${DEPLOY_ROOT}" "${RELEASE_DIR}" <<'REMOTE'
set -euo pipefail
deploy_root="$1"
release_dir="$2"
cd "${release_dir}"

if ! docker compose -p sulocraft \
  --env-file "${deploy_root}/shared/.env" \
  -f backend/docker-compose.yml \
  up -d --build --remove-orphans; then
  docker compose -p sulocraft --env-file "${deploy_root}/shared/.env" -f backend/docker-compose.yml ps
  docker compose -p sulocraft --env-file "${deploy_root}/shared/.env" -f backend/docker-compose.yml logs --tail=150 api postgres reverse-proxy
  echo "Deployment failed while starting the Compose stack; current symlink was not changed."
  exit 1
fi

for attempt in $(seq 1 30); do
  if curl --fail --silent http://127.0.0.1/health >/dev/null; then
    ln -sfn "${release_dir}" "${deploy_root}/current"
    printf '%s\n' "${release_dir}" > "${deploy_root}/shared/last-successful-release"
    docker compose -p sulocraft --env-file "${deploy_root}/shared/.env" -f backend/docker-compose.yml ps
    echo "Sulocraft API health check passed."
    exit 0
  fi
  sleep 2
done

docker compose -p sulocraft --env-file "${deploy_root}/shared/.env" -f backend/docker-compose.yml ps
docker compose -p sulocraft --env-file "${deploy_root}/shared/.env" -f backend/docker-compose.yml logs --tail=150 api reverse-proxy
echo "Deployment failed health validation; current symlink was not changed."
exit 1
REMOTE

echo "Deployment complete: ${RELEASE_ID}"
