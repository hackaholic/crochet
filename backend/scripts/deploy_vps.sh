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
RUNTIME_SECRETS_ROOT="${RUNTIME_SECRETS_ROOT:-/run/sulocraft}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --env) TARGET_ENV="$2"; shift 2 ;;
    --env=*) TARGET_ENV="${1#*=}"; shift ;;
    --host) DEPLOY_HOST="$2"; shift 2 ;;
    --host=*) DEPLOY_HOST="${1#*=}"; shift ;;
    --root) DEPLOY_ROOT="$2"; shift 2 ;;
    --root=*) DEPLOY_ROOT="${1#*=}"; shift ;;
    --secrets-root) RUNTIME_SECRETS_ROOT="$2"; shift 2 ;;
    --secrets-root=*) RUNTIME_SECRETS_ROOT="${1#*=}"; shift ;;
    *) shift ;;
  esac
done

case "${TARGET_ENV}" in
  preprod|prod) ;;
  *) echo "Unsupported deployment target '${TARGET_ENV}'; expected preprod or prod." >&2; exit 2 ;;
esac

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
ssh "${SSH_OPTIONS[@]}" "${DEPLOY_HOST}" "bash -s" -- "${DEPLOY_ROOT}" "${TARGET_ENV}" "${RUNTIME_SECRETS_ROOT}" <<'REMOTE_BACKUP'
set -euo pipefail
umask 077
deploy_root="$1"
target_env="$2"
runtime_secrets_root="$3"
runtime_secrets_dir="${runtime_secrets_root%/}/${target_env}"
export TARGET_ENV="${target_env}" RUNTIME_SECRETS_DIR="${runtime_secrets_dir}"
export POSTGRES_DB_FILE="${runtime_secrets_dir}/postgres/postgres_db"
export POSTGRES_USER_FILE="${runtime_secrets_dir}/postgres/postgres_user"
export POSTGRES_PASSWORD_FILE="${runtime_secrets_dir}/postgres/postgres_password"
export DATABASE_URL_FILE="${runtime_secrets_dir}/backend/database_url"
current_release="$(readlink -f "${deploy_root}/current" 2>/dev/null || true)"
if [[ -n "${current_release}" && -f "${current_release}/backend/docker-compose.yml" ]]; then
  mkdir -p "${deploy_root}/backups"
  backup_file="${deploy_root}/backups/predeploy_${target_env}_$(date -u +%Y%m%dT%H%M%SZ).sql.gz"
  backup_tmp="${backup_file}.tmp.$$"
  compose_cmd=(docker compose -p "sulocraft-${target_env}" -f "${current_release}/backend/docker-compose.yml")
  if [[ -f "${deploy_root}/shared/.env" ]]; then
    compose_cmd+=(--env-file "${deploy_root}/shared/.env")
  fi
  if ! "${compose_cmd[@]}" ps --status running postgres --quiet | grep -q . && [[ "${target_env}" == "preprod" ]]; then
    # Before PREPROD's first isolated promotion, preserve its existing legacy project.
    export TARGET_ENV=preprod RUNTIME_SECRETS_DIR=/run/sulocraft
    export POSTGRES_DB_FILE=/run/sulocraft/postgres/postgres_db
    export POSTGRES_USER_FILE=/run/sulocraft/postgres/postgres_user
    export POSTGRES_PASSWORD_FILE=/run/sulocraft/postgres/postgres_password
    export DATABASE_URL_FILE=/run/sulocraft/backend/database_url
    legacy_compose_cmd=(docker compose -p sulocraft -f "${current_release}/backend/docker-compose.yml")
    if [[ -f "${deploy_root}/shared/.env" ]]; then
      legacy_compose_cmd+=(--env-file "${deploy_root}/shared/.env")
    fi
    if "${legacy_compose_cmd[@]}" ps --status running postgres --quiet | grep -q .; then
      compose_cmd=("${legacy_compose_cmd[@]}")
    fi
  fi
  if "${compose_cmd[@]}" ps --status running postgres --quiet | grep -q .; then
    if "${compose_cmd[@]}" exec -T postgres sh -ec 'pg_dump -U "$(cat /run/secrets/postgres_user)" "$(cat /run/secrets/postgres_db)"' | gzip > "${backup_tmp}"; then
      test -s "${backup_tmp}" || { echo "Pre-deploy database backup was empty; refusing to deploy." >&2; exit 1; }
      chmod 600 "${backup_tmp}"
      mv "${backup_tmp}" "${backup_file}"
      echo "Database backup created: ${backup_file}"
    else
      rm -f "${backup_tmp}"
      echo "Pre-deploy database backup failed; refusing to deploy." >&2
      exit 1
    fi
  fi
fi
REMOTE_BACKUP

# Remote Bootstrap and Compose Execution
ssh "${SSH_OPTIONS[@]}" "${DEPLOY_HOST}" "bash -s" -- "${DEPLOY_ROOT}" "${RELEASE_DIR}" "${TARGET_ENV}" "${RUNTIME_SECRETS_ROOT}" <<'REMOTE'
set -euo pipefail
deploy_root="$1"
release_dir="$2"
target_env="$3"
runtime_secrets_root="$4"
runtime_secrets_dir="${runtime_secrets_root%/}/${target_env}"
export TARGET_ENV="${target_env}" RUNTIME_SECRETS_DIR="${runtime_secrets_dir}"
export POSTGRES_DB_FILE="${runtime_secrets_dir}/postgres/postgres_db"
export POSTGRES_USER_FILE="${runtime_secrets_dir}/postgres/postgres_user"
export POSTGRES_PASSWORD_FILE="${runtime_secrets_dir}/postgres/postgres_password"
export DATABASE_URL_FILE="${runtime_secrets_dir}/backend/database_url"

# Default resource limits prioritize production and constrain preproduction
if [[ "${target_env}" == "prod" ]]; then
  export API_MEM_LIMIT="${API_MEM_LIMIT:-768M}"
  export API_CPUS_LIMIT="${API_CPUS_LIMIT:-0.75}"
  export POSTGRES_MEM_LIMIT="${POSTGRES_MEM_LIMIT:-1024M}"
  export POSTGRES_CPUS_LIMIT="${POSTGRES_CPUS_LIMIT:-0.75}"
else
  export API_MEM_LIMIT="${API_MEM_LIMIT:-512M}"
  export API_CPUS_LIMIT="${API_CPUS_LIMIT:-0.50}"
  export POSTGRES_MEM_LIMIT="${POSTGRES_MEM_LIMIT:-512M}"
  export POSTGRES_CPUS_LIMIT="${POSTGRES_CPUS_LIMIT:-0.50}"
fi

cd "${release_dir}"

# 1. Bootstrap secrets if encrypted groups exist
if [[ -f "${release_dir}/backend/scripts/bootstrap_secrets.sh" ]]; then
  echo "Bootstrapping encrypted secrets on host (environment: ${target_env})..."
  SOPS_AGE_KEY_FILE="/etc/sulocraft/age/keys.txt" \
  RUNTIME_SECRETS_DIR="${runtime_secrets_dir}" \
  bash "${release_dir}/backend/scripts/bootstrap_secrets.sh" --env "${target_env}"
fi

# 2. Build compose command
compose_cmd=(docker compose -p "sulocraft-${target_env}" -f backend/docker-compose.yml)
if [[ -f "${deploy_root}/shared/.env" ]]; then
  compose_cmd+=(--env-file "${deploy_root}/shared/.env")
fi

# 3. Start services
if ! "${compose_cmd[@]}" up -d --build --remove-orphans; then
  "${compose_cmd[@]}" ps
  "${compose_cmd[@]}" logs --tail=150 api postgres
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
"${compose_cmd[@]}" logs --tail=150 api
echo "Deployment failed health validation; current symlink was not changed."
exit 1
REMOTE

echo "Deployment complete: ${RELEASE_ID}"
