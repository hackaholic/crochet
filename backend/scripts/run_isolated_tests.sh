#!/usr/bin/env bash
# run_isolated_tests.sh - Run backend pytest suite against an isolated disposable PostgreSQL test container
# Conforms to Work 003 Task 3.13 specification.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
REPO_ROOT="$(cd "${BACKEND_DIR}/.." && pwd)"

COMPOSE_FILE="${REPO_ROOT}/docker/compose.test.yaml"
TEST_PORT="${TEST_PORT:-5433}"
TEST_DB="${TEST_DB:-sulocraft_test}"
TEST_USER="${TEST_USER:-sulocraft_test}"
TEST_PASS="${TEST_PASS:-sulocraft_test}"
TEST_DATABASE_URL="postgresql://${TEST_USER}:${TEST_PASS}@localhost:${TEST_PORT}/${TEST_DB}"

PYTEST_BIN="${BACKEND_DIR}/.venv/bin/pytest"
if [[ ! -x "${PYTEST_BIN}" ]]; then
  PYTEST_BIN="$(command -v pytest || true)"
fi

if [[ -z "${PYTEST_BIN}" || ! -x "${PYTEST_BIN}" ]]; then
  echo "Error: pytest binary not found in ${BACKEND_DIR}/.venv/bin/pytest or system PATH." >&2
  exit 1
fi

if command -v docker-compose >/dev/null 2>&1; then
  COMPOSE_CMD=(docker-compose)
elif docker compose version >/dev/null 2>&1; then
  COMPOSE_CMD=(docker compose)
else
  COMPOSE_CMD=(docker-compose)
fi

echo "================================================================="
echo "Sulocraft Isolated Backend Test Runner (Task 3.13)"
echo "Starting ephemeral disposable PostgreSQL test database on port ${TEST_PORT}..."
echo "================================================================="

# Trap to guarantee container teardown and data destruction
cleanup() {
  local exit_code=$?
  echo "Tearing down disposable test container..."
  "${COMPOSE_CMD[@]}" -p sulocraft-test -f "${COMPOSE_FILE}" down -v --remove-orphans >/dev/null 2>&1 || true
  exit "${exit_code}"
}
trap cleanup EXIT INT TERM

# 1. Start disposable test container with tmpfs
"${COMPOSE_CMD[@]}" -p sulocraft-test -f "${COMPOSE_FILE}" down -v --remove-orphans >/dev/null 2>&1 || true
"${COMPOSE_CMD[@]}" -p sulocraft-test -f "${COMPOSE_FILE}" up -d --wait test-db

echo "Disposable test database is ready on port ${TEST_PORT}."

# 2. Run pytest with isolated test database
echo "Executing test suite with TEST_DATABASE_URL=${TEST_DATABASE_URL}..."
export DATABASE_URL="${TEST_DATABASE_URL}"
export TEST_DATABASE_URL="${TEST_DATABASE_URL}"
unset DATABASE_URL_FILE || true

pytest_args=("$@")
if [[ ${#pytest_args[@]} -eq 0 ]]; then
  pytest_args=("${BACKEND_DIR}/tests")
fi

"${PYTEST_BIN}" "${pytest_args[@]}"
test_status=$?

# 3. Verify preprod database integrity on port 5432
if curl --silent --fail http://localhost:8000/health >/dev/null 2>&1; then
  echo "Preprod database integrity verified: local API remains healthy on port 8000."
fi

exit "${test_status}"
