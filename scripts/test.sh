#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="${ROOT_DIR}/docker/compose.test.yaml"

if docker compose version >/dev/null 2>&1; then
  DOCKER_COMPOSE=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
  DOCKER_COMPOSE=(docker-compose)
else
  echo "Error: neither 'docker compose' nor 'docker-compose' found." >&2
  exit 1
fi

usage() {
  cat << 'USAGE'
Sulocraft Containerized Test Runner
Usage:
  ./scripts/test.sh [target] [options...]

Targets:
  backend [pytest args...]       Run backend tests in container (passes all extra args to pytest)
  frontend [test args...]        Run frontend tests in container (passes all extra args to vitest/pnpm)
  security [check/script/args]   Run security scans and audits in container
  all                            Run backend, frontend, and security test suites
  build [service]                Build test container images
  shell [backend|frontend|sec]   Start interactive terminal session in test container
  down                           Stop and remove test containers, volumes, and networks

Security Shortcuts:
  ./scripts/test.sh security sast
  ./scripts/test.sh security secrets
  ./scripts/test.sh security config
  ./scripts/test.sh security deps
  ./scripts/test.sh security auth
  ./scripts/test.sh security audit   (runs the full security release gate)

Examples:
  ./scripts/test.sh backend
  ./scripts/test.sh backend tests/test_products.py -k test_list
  ./scripts/test.sh frontend
  ./scripts/test.sh security sast
  ./scripts/test.sh shell security
  ./scripts/test.sh all
USAGE
  exit 1
}

TARGET="${1:-all}"
shift || true

build_service() {
  local service="$1"
  "${DOCKER_COMPOSE[@]}" -f "${COMPOSE_FILE}" build "${service}"
}

case "${TARGET}" in
  build)
    SERVICE="${1:-}"
    if [[ -n "${SERVICE}" ]]; then
      build_service "${SERVICE}"
    else
      echo "Building all test containers..."
      "${DOCKER_COMPOSE[@]}" -f "${COMPOSE_FILE}" build
    fi
    ;;
  backend)
    echo "Running backend tests inside container..."
    build_service backend
    if [[ $# -gt 0 ]]; then
      "${DOCKER_COMPOSE[@]}" -f "${COMPOSE_FILE}" run --rm backend uv run pytest "$@"
    else
      "${DOCKER_COMPOSE[@]}" -f "${COMPOSE_FILE}" run --rm backend
    fi
    ;;
  frontend)
    echo "Running frontend tests inside container..."
    build_service frontend
    if [[ $# -gt 0 ]]; then
      "${DOCKER_COMPOSE[@]}" -f "${COMPOSE_FILE}" run --rm frontend "$@"
    else
      "${DOCKER_COMPOSE[@]}" -f "${COMPOSE_FILE}" run --rm frontend
    fi
    ;;
  security)
    SUB="${1:-audit}"
    shift || true
    build_service security
    case "${SUB}" in
      sast)
        echo "Running SAST Static Application Security Testing in container..."
        "${DOCKER_COMPOSE[@]}" -f "${COMPOSE_FILE}" run --rm -w /app security ./scripts/security/scan-sast.sh "$@"
        ;;
      secrets)
        echo "Running Secret Scanner in container..."
        "${DOCKER_COMPOSE[@]}" -f "${COMPOSE_FILE}" run --rm -w /app security ./scripts/security/scan-secrets.sh "$@"
        ;;
      config)
        echo "Running Configuration & Architecture Scan in container..."
        "${DOCKER_COMPOSE[@]}" -f "${COMPOSE_FILE}" run --rm -w /app security ./scripts/security/scan-config.sh "$@"
        ;;
      deps|dependencies)
        echo "Running Dependency Audit in container..."
        "${DOCKER_COMPOSE[@]}" -f "${COMPOSE_FILE}" run --rm -w /app security ./scripts/security/scan-dependencies.sh "$@"
        ;;
      auth|authorization)
        echo "Running Security Authorization & RBAC Tests in container..."
        "${DOCKER_COMPOSE[@]}" -f "${COMPOSE_FILE}" run --rm security uv run pytest tests/test_security_authorization.py tests/test_security_business_logic.py tests/test_config_secrets.py -v "$@"
        ;;
      audit|all)
        echo "Running Full Security Gate Suite in container..."
        "${DOCKER_COMPOSE[@]}" -f "${COMPOSE_FILE}" run --rm -w /app security ./scripts/security/scan-sast.sh
        "${DOCKER_COMPOSE[@]}" -f "${COMPOSE_FILE}" run --rm -w /app security ./scripts/security/scan-secrets.sh
        "${DOCKER_COMPOSE[@]}" -f "${COMPOSE_FILE}" run --rm -w /app security ./scripts/security/scan-config.sh
        "${DOCKER_COMPOSE[@]}" -f "${COMPOSE_FILE}" run --rm security uv run pytest tests/test_security_authorization.py tests/test_security_business_logic.py tests/test_config_secrets.py -q
        ;;
      *)
        "${DOCKER_COMPOSE[@]}" -f "${COMPOSE_FILE}" run --rm -w /app security "${SUB}" "$@"
        ;;
    esac
    ;;
  all)
    echo "Running complete test & security verification in containers..."
    build_service backend
    "${DOCKER_COMPOSE[@]}" -f "${COMPOSE_FILE}" run --rm backend
    build_service frontend
    "${DOCKER_COMPOSE[@]}" -f "${COMPOSE_FILE}" run --rm frontend
    build_service security
    "${DOCKER_COMPOSE[@]}" -f "${COMPOSE_FILE}" run --rm -w /app security ./scripts/security/scan-sast.sh
    "${DOCKER_COMPOSE[@]}" -f "${COMPOSE_FILE}" run --rm -w /app security ./scripts/security/scan-secrets.sh
    "${DOCKER_COMPOSE[@]}" -f "${COMPOSE_FILE}" run --rm security uv run pytest tests/test_security_authorization.py tests/test_security_business_logic.py tests/test_config_secrets.py -q
    ;;
  shell)
    SERVICE="${1:-backend}"
    if [[ "${SERVICE}" == "sec" || "${SERVICE}" == "security" ]]; then
      SERVICE="security"
    fi
    echo "Starting interactive shell in test-${SERVICE} container..."
    build_service "${SERVICE}"
    if [[ "${SERVICE}" == "frontend" ]]; then
      "${DOCKER_COMPOSE[@]}" -f "${COMPOSE_FILE}" run --rm frontend /bin/sh
    else
      "${DOCKER_COMPOSE[@]}" -f "${COMPOSE_FILE}" run --rm "${SERVICE}" /bin/bash
    fi
    ;;
  down)
    echo "Cleaning up test environment..."
    "${DOCKER_COMPOSE[@]}" -f "${COMPOSE_FILE}" down -v
    ;;
  help|--help|-h)
    usage
    ;;
  *)
    echo "Unknown target: ${TARGET}"
    usage
    ;;
esac
