#!/usr/bin/env bash
set -euo pipefail

DEPLOY_HOST="${DEPLOY_HOST:-root@201.18.212.183}"
DEPLOY_ROOT="${DEPLOY_ROOT:-/opt/sulocraft}"
TARGET_RELEASE="${1:-}"

if [[ -z "${TARGET_RELEASE}" ]]; then
  echo "Usage: $0 <release-id>"
  exit 1
fi

ssh "${DEPLOY_HOST}" "bash -s" -- "${DEPLOY_ROOT}" "${TARGET_RELEASE}" <<'REMOTE'
set -euo pipefail
deploy_root="$1"
target_release="$2"
release_dir="${deploy_root}/releases/${target_release}"
test -f "${release_dir}/backend/docker-compose.yml"
cd "${release_dir}"
docker compose -p sulocraft --env-file "${deploy_root}/shared/.env" -f backend/docker-compose.yml up -d --build --remove-orphans
curl --fail --retry 20 --retry-delay 2 http://127.0.0.1/health >/dev/null
ln -sfn "${release_dir}" "${deploy_root}/current"
printf '%s\n' "${release_dir}" > "${deploy_root}/shared/last-successful-release"
echo "Rolled back to ${target_release}"
REMOTE
