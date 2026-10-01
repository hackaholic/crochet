#!/usr/bin/env bash
set -euo pipefail

DEPLOY_HOST="${DEPLOY_HOST:-root@201.18.212.183}"
DEPLOY_ROOT="${DEPLOY_ROOT:-/opt/sulocraft}"
DEPLOY_ENV_FILE="${DEPLOY_ENV_FILE:-backend/.env.preprod}"
RELEASE_ID="${RELEASE_ID:-$(date -u +%Y%m%dT%H%M%SZ)}"
RELEASE_DIR="${DEPLOY_ROOT}/releases/${RELEASE_ID}"

if [[ ! -f "${DEPLOY_ENV_FILE}" ]]; then
  echo "Missing ${DEPLOY_ENV_FILE}. Copy backend/.env.preprod.example and fill it locally."
  exit 1
fi

for command in ssh scp rsync; do
  command -v "${command}" >/dev/null || { echo "Required command not found: ${command}"; exit 1; }
done

echo "Deploying Sulocraft release ${RELEASE_ID} to ${DEPLOY_HOST}:${RELEASE_DIR}"
ssh "${DEPLOY_HOST}" "mkdir -p '${RELEASE_DIR}' '${DEPLOY_ROOT}/shared'"

rsync -az --delete \
  --exclude '.git/' \
  --exclude '.env*' \
  --exclude 'node_modules/' \
  --exclude 'dist/' \
  --exclude 'backend/.venv/' \
  --exclude '**/__pycache__/' \
  ./ "${DEPLOY_HOST}:${RELEASE_DIR}/"

scp "${DEPLOY_ENV_FILE}" "${DEPLOY_HOST}:${DEPLOY_ROOT}/shared/.env"
ssh "${DEPLOY_HOST}" "chmod 600 '${DEPLOY_ROOT}/shared/.env'"

ssh "${DEPLOY_HOST}" "bash -s" -- "${DEPLOY_ROOT}" "${RELEASE_DIR}" <<'REMOTE'
set -euo pipefail
deploy_root="$1"
release_dir="$2"
cd "${release_dir}"

docker compose -p sulocraft \
  --env-file "${deploy_root}/shared/.env" \
  -f backend/docker-compose.yml \
  up -d --build --remove-orphans

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
