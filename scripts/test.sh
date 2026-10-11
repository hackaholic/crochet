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
  backend [pytest args...]    Run backend tests in container (passes all extra args to pytest)
  frontend [test args...]     Run frontend tests in container (passes all extra args to vitest/pnpm)
  all                         Run both backend and frontend test suites
  build                       Build test container images
  shell [backend|frontend]    Start interactive terminal session in test container
  down                        Stop and remove test containers and networks

Examples:
  ./scripts/test.sh backend
  ./scripts/test.sh backend tests/test_products.py -k test_list
  ./scripts/test.sh frontend
  ./scripts/test.sh shell backend
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
    echo "Building test containers..."
    "${DOCKER_COMPOSE[@]}" -f "${COMPOSE_FILE}" build
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
  all)
    echo "Running full test suite in containers..."
    build_service backend
    "${DOCKER_COMPOSE[@]}" -f "${COMPOSE_FILE}" run --rm backend
    build_service frontend
    "${DOCKER_COMPOSE[@]}" -f "${COMPOSE_FILE}" run --rm frontend
    ;;
  shell)
    SERVICE="${1:-backend}"
    echo "Starting interactive shell in test-${SERVICE} container..."
    build_service "${SERVICE}"
    if [[ "${SERVICE}" == "backend" ]]; then
      "${DOCKER_COMPOSE[@]}" -f "${COMPOSE_FILE}" run --rm backend /bin/bash
    else
      "${DOCKER_COMPOSE[@]}" -f "${COMPOSE_FILE}" run --rm frontend /bin/sh
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
