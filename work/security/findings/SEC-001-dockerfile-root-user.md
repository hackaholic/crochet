# Finding SEC-001 — Dockerfiles Missing Explicit Non-Root USER Directive

- **Severity:** Medium
- **Category:** Container Security / Dockerfile Misconfiguration
- **Component:** `backend/Dockerfile`, `docker/api.Dockerfile`, `docker/frontend.Dockerfile`
- **Discovered Date:** 2026-10-02
- **Status:** Open (Tracked for remediation)

## Description

Semgrep rule `dockerfile.security.missing-user.missing-user` detected that the application Dockerfiles do not specify an explicit non-root `USER` directive before the `CMD` / `ENTRYPOINT`. By default, container processes run as `root` (UID 0) within the container namespace.

## Impact

If a remote code execution vulnerability were to occur within the container process, the attacker would have root privileges inside the container, increasing the potential risk of namespace escape or container breakout if paired with kernel vulnerabilities.

## Remediation

Add a non-root system user and group (e.g., `adduser -u 1001 -S appuser -G appgroup`) and specify `USER appuser` after building dependencies and setting ownership of runtime directories.
