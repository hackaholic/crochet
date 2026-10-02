# Task 9.4 — Container and infrastructure security scanning

**Owner:** Gemini
**Status:** Pending

## Objective

Implement `scripts/security/scan-container.sh` using Trivy to audit repository filesystems, Dockerfiles, Compose files, and production container images for known vulnerabilities, misconfigurations, and embedded secrets.

## Context and contract

Audit criteria: non-root users, non-privileged containers, no Docker socket mounts, no sensitive capabilities, no exposed internal ports (Postgres 5432), and no secrets in image layers.

## Scope

- In scope:
  - `scripts/security/scan-container.sh` with Trivy scanners (`vuln,secret,misconfig`).
  - Auditing `backend/Dockerfile`, `docker/frontend.Dockerfile`, `docker/compose.yaml`, `backend/docker-compose.yml`.
  - Machine-readable JSON/SARIF output saved to `work/security/reports/`.
- Out of scope:
  - Running host root commands.

## Dependencies and relevant files

- Depends on: Docker setup.
- Inspect/edit:
  - `scripts/security/scan-container.sh`
  - `backend/docker-compose.yml`

## Acceptance checks

- [ ] `scan-container.sh` scans Dockerfiles and Compose configurations.
- [ ] Confirms Postgres port 5432 is not exposed to public host interface.

## Handoff back

- Update `work/security/tasks.md` and `notes.md`.
