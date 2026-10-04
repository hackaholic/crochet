#!/usr/bin/env bash
# Transfer and activate an already-built API image. The VPS never builds source.
set -euo pipefail

remote_mode=false
if [[ "${1:-}" == "--remote" ]]; then
  remote_mode=true
  shift
fi

TARGET_ENV=""
DEPLOY_HOST=""
DEPLOY_ROOT=""
RELEASE_ID=""
RUNTIME_SECRETS_ROOT="/run/sulocraft"
GATEWAY_NETWORK_NAME="sulocraft-gateway"
SSH_IDENTITY_FILE=""
SSH_KNOWN_HOSTS_FILE=""
IMAGE_REF=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --env) TARGET_ENV="$2"; shift 2 ;;
    --host) DEPLOY_HOST="$2"; shift 2 ;;
    --root) DEPLOY_ROOT="$2"; shift 2 ;;
    --release-id) RELEASE_ID="$2"; shift 2 ;;
    --runtime-secrets-root) RUNTIME_SECRETS_ROOT="$2"; shift 2 ;;
    --gateway-network) GATEWAY_NETWORK_NAME="$2"; shift 2 ;;
    --identity) SSH_IDENTITY_FILE="$2"; shift 2 ;;
    --known-hosts) SSH_KNOWN_HOSTS_FILE="$2"; shift 2 ;;
    --image-ref) IMAGE_REF="$2"; shift 2 ;;
    *) echo "Unknown deployment argument: $1" >&2; exit 2 ;;
  esac
done

case "${TARGET_ENV}" in preprod|prod) ;; *) echo "--env must be preprod or prod" >&2; exit 2 ;; esac
[[ -n "${DEPLOY_HOST}" && -n "${DEPLOY_ROOT}" && -n "${RELEASE_ID}" && -n "${IMAGE_REF}" && -n "${GATEWAY_NETWORK_NAME}" ]] || {
  echo "Host, root, release ID, gateway network, and image ref are required." >&2; exit 2;
}
[[ "${DEPLOY_ROOT}" == /* ]] || { echo "Deployment root must be absolute." >&2; exit 2; }
RELEASE_DIR="${DEPLOY_ROOT%/}/releases/${RELEASE_ID}"
RUNTIME_SECRETS_DIR="${RUNTIME_SECRETS_ROOT%/}/${TARGET_ENV}"

SSH_OPTIONS=(-o BatchMode=yes)
RSYNC_SSH="ssh -o BatchMode=yes"
if [[ -n "${SSH_IDENTITY_FILE}" ]]; then
  SSH_OPTIONS+=(-i "${SSH_IDENTITY_FILE}" -o IdentitiesOnly=yes)
  RSYNC_SSH+=" -i ${SSH_IDENTITY_FILE} -o IdentitiesOnly=yes"
fi
if [[ -n "${SSH_KNOWN_HOSTS_FILE}" ]]; then
  SSH_OPTIONS+=(-o "UserKnownHostsFile=${SSH_KNOWN_HOSTS_FILE}" -o StrictHostKeyChecking=yes)
  RSYNC_SSH+=" -o UserKnownHostsFile=${SSH_KNOWN_HOSTS_FILE} -o StrictHostKeyChecking=yes"
fi

if [[ "${remote_mode}" == false ]]; then
  repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
  artifact_dir="${repo_root}/.deploy/releases/${RELEASE_ID}"
  runtime_env="${repo_root}/.deploy/runtime-${TARGET_ENV}.env"
  [[ -s "${artifact_dir}/api-image.tar" && -s "${artifact_dir}/manifest.json" && -s "${runtime_env}" ]] || {
    echo "Release archive, manifest, or rendered runtime config is missing." >&2; exit 1;
  }
  command -v ssh >/dev/null && command -v rsync >/dev/null || { echo "ssh and rsync are required." >&2; exit 1; }
  ssh "${SSH_OPTIONS[@]}" "${DEPLOY_HOST}" "mkdir -p '${RELEASE_DIR}' '${DEPLOY_ROOT}/backups' '${DEPLOY_ROOT}/shared'"
  rsync -az --delete -e "${RSYNC_SSH}" \
    --exclude '.git/' --exclude '.env*' --exclude 'node_modules/' --exclude 'dist/' \
    --exclude 'backend/.venv/' --exclude '**/__pycache__/' --exclude '.deploy/' \
    --exclude '/work/' --exclude '/docs/' \
    "${repo_root}/" "${DEPLOY_HOST}:${RELEASE_DIR}/"
  rsync -az -e "${RSYNC_SSH}" "${artifact_dir}/api-image.tar" "${artifact_dir}/manifest.json" "${DEPLOY_HOST}:${RELEASE_DIR}/"
  rsync -az -e "${RSYNC_SSH}" "${runtime_env}" "${DEPLOY_HOST}:${RELEASE_DIR}/deploy.env"
  ssh "${SSH_OPTIONS[@]}" "${DEPLOY_HOST}" "chmod 600 '${RELEASE_DIR}/deploy.env' && bash -s -- --remote --env '${TARGET_ENV}' --host '${DEPLOY_HOST}' --root '${DEPLOY_ROOT}' --release-id '${RELEASE_ID}' --runtime-secrets-root '${RUNTIME_SECRETS_ROOT}' --gateway-network '${GATEWAY_NETWORK_NAME}' --image-ref '${IMAGE_REF}'" < "${BASH_SOURCE[0]}"
  exit $?
fi

# From here onward this script is executing on the VPS as the deployment owner.
release_dir="${RELEASE_DIR}"
deploy_root="${DEPLOY_ROOT%/}"
runtime_secrets_dir="${RUNTIME_SECRETS_DIR}"
test -s "${release_dir}/api-image.tar" && test -s "${release_dir}/manifest.json" && test -s "${release_dir}/deploy.env"
archive_sha="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["artifact_sha256"])' "${release_dir}/manifest.json")"
printf '%s  %s\n' "${archive_sha}" "${release_dir}/api-image.tar" | sha256sum --check --status || {
  echo "Release image checksum verification failed." >&2; exit 1;
}
manifest_ref="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["image_ref"])' "${release_dir}/manifest.json")"
[[ "${manifest_ref}" == "${IMAGE_REF}" ]] || { echo "Image reference does not match release manifest." >&2; exit 1; }

# Prefer an existing isolated target stack. On the first PREPROD rollout only,
# fall back to the current legacy `sulocraft` stack for the one-time DB cutover.
backup_file="${deploy_root}/backups/predeploy_${TARGET_ENV}_${RELEASE_ID}.sql.gz"
current_release="$(readlink -f "${deploy_root}/current" 2>/dev/null || true)"
previous_compose=()
previous_kind="none"
if [[ -n "${current_release}" && -f "${current_release}/backend/docker-compose.yml" ]]; then
  isolated_compose=(docker compose -p "sulocraft-${TARGET_ENV}" -f "${current_release}/backend/docker-compose.yml")
  if [[ -s "${current_release}/deploy.env" ]]; then isolated_compose+=(--env-file "${current_release}/deploy.env"); fi
  if "${isolated_compose[@]}" ps --status running postgres --quiet | grep -q .; then
    previous_compose=("${isolated_compose[@]}")
    previous_kind="isolated"
  elif [[ "${TARGET_ENV}" == preprod ]]; then
    legacy_compose=(docker compose -p sulocraft -f "${current_release}/backend/docker-compose.yml")
    if [[ -f "${deploy_root}/shared/.env" ]]; then legacy_compose+=(--env-file "${deploy_root}/shared/.env"); fi
    if "${legacy_compose[@]}" ps --status running postgres --quiet | grep -q .; then
      previous_compose=("${legacy_compose[@]}")
      previous_kind="legacy"
    fi
  fi
fi

if [[ "${previous_kind}" != none ]]; then
  umask 077
  backup_tmp="${backup_file}.tmp.$$"
  if "${previous_compose[@]}" exec -T postgres sh -ec 'pg_dump -U "$(cat /run/secrets/postgres_user)" "$(cat /run/secrets/postgres_db)"' </dev/null | gzip > "${backup_tmp}" && test -s "${backup_tmp}"; then
    chmod 600 "${backup_tmp}"
    mv "${backup_tmp}" "${backup_file}"
    echo "Pre-deploy database backup verified: ${backup_file}"
  else
    rm -f "${backup_tmp}"
    echo "Database backup failed; deployment stopped before service changes." >&2
    exit 1
  fi
fi

export TARGET_ENV="${TARGET_ENV}" RUNTIME_SECRETS_DIR="${runtime_secrets_dir}"
export POSTGRES_DB_FILE="${runtime_secrets_dir}/postgres/postgres_db"
export POSTGRES_USER_FILE="${runtime_secrets_dir}/postgres/postgres_user"
export POSTGRES_PASSWORD_FILE="${runtime_secrets_dir}/postgres/postgres_password"
export DATABASE_URL_FILE="${runtime_secrets_dir}/backend/database_url"
SOPS_AGE_KEY_FILE="/etc/sulocraft/age/keys.txt" \
  bash "${release_dir}/backend/scripts/bootstrap_secrets.sh" --env "${TARGET_ENV}" --secrets-dir "${release_dir}/secrets/encrypted" --runtime-dir "${runtime_secrets_dir}"

if ! docker network inspect "${GATEWAY_NETWORK_NAME}" >/dev/null 2>&1; then docker network create "${GATEWAY_NETWORK_NAME}" >/dev/null; fi
if [[ "${TARGET_ENV}" == preprod ]]; then
  while IFS= read -r proxy_id; do
    [[ -n "${proxy_id}" ]] || continue
    if ! docker inspect --format '{{json .NetworkSettings.Networks}}' "${proxy_id}" | grep -Fq "${GATEWAY_NETWORK_NAME}"; then
      docker network connect "${GATEWAY_NETWORK_NAME}" "${proxy_id}"
    fi
  done < <(docker ps -q --filter label=com.docker.compose.service=reverse-proxy --filter status=running)
fi

if [[ "${previous_kind}" != none ]]; then
  "${previous_compose[@]}" stop api postgres
  "${previous_compose[@]}" rm -f api postgres
fi

compose=(docker compose -p "sulocraft-${TARGET_ENV}" -f "${release_dir}/backend/docker-compose.yml" --env-file "${release_dir}/deploy.env")
rollback_legacy() {
  "${compose[@]}" down || true
  if [[ "${previous_kind}" != none ]]; then "${previous_compose[@]}" up -d postgres api || true; fi
}

if ! docker load --input "${release_dir}/api-image.tar"; then
  echo "Could not load release image." >&2
  rollback_legacy
  exit 1
fi
if ! "${compose[@]}" up -d postgres; then
  echo "Isolated database failed to start." >&2
  rollback_legacy
  exit 1
fi
for attempt in $(seq 1 45); do
  if "${compose[@]}" exec -T postgres sh -ec 'pg_isready -U "$(cat /run/secrets/postgres_user)" -d "$(cat /run/secrets/postgres_db)"' </dev/null >/dev/null 2>&1; then break; fi
  if [[ "${attempt}" == 45 ]]; then echo "Isolated database did not become ready." >&2; rollback_legacy; exit 1; fi
  sleep 2
done
if [[ "${previous_kind}" == legacy && "${TARGET_ENV}" == preprod && -s "${backup_file}" ]]; then
  if ! gzip -dc "${backup_file}" | "${compose[@]}" exec -T postgres sh -ec 'PGPASSWORD="$(cat /run/secrets/postgres_password)" psql -v ON_ERROR_STOP=1 -U "$(cat /run/secrets/postgres_user)" -d "$(cat /run/secrets/postgres_db)"' >/dev/null; then
    echo "PREPROD database restore failed; old database volume is preserved." >&2
    rollback_legacy
    exit 1
  fi
  echo "PREPROD database restored from the verified pre-deploy backup."
fi

if ! "${compose[@]}" up -d --no-build api; then
  "${compose[@]}" logs --tail=120 api postgres || true
  echo "Isolated API failed to start." >&2
  rollback_legacy
  exit 1
fi
healthy=false
for attempt in $(seq 1 45); do
  if "${compose[@]}" exec -T api curl --fail --silent http://127.0.0.1:8000/health </dev/null >/dev/null; then healthy=true; break; fi
  sleep 2
done
if [[ "${healthy}" != true ]]; then
  "${compose[@]}" logs --tail=120 api postgres || true
  echo "New API failed its health check; restoring the previous preprod service." >&2
  rollback_legacy
  exit 1
fi

if [[ "${TARGET_ENV}" == preprod ]]; then
  if ! curl --fail --silent --max-time 12 http://127.0.0.1/health >/dev/null; then
    echo "Preprod API is healthy but the existing proxy route failed; rolling back." >&2
    rollback_legacy
    exit 1
  fi
fi
ln -sfn "${release_dir}" "${deploy_root}/current"
printf '%s\n' "${RELEASE_ID}" > "${deploy_root}/shared/last-successful-${TARGET_ENV}-release"
"${compose[@]}" ps
echo "Sulocraft ${TARGET_ENV} image ${IMAGE_REF} is healthy and active."
