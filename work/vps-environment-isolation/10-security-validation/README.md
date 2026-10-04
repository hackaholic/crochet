# 10 — Security and isolation validation

**Status:** Pending — depends on 02–09.

## Goal

Demonstrate that environment boundaries hold in Compose, runtime secrets, storage, and external integrations.

## Subtasks

- [ ] Prove PREPROD cannot connect to PROD PostgreSQL or access PROD credentials.
- [ ] Prove PREPROD cannot write/delete PROD R2 assets.
- [ ] Prove PREPROD email blocks recipients outside its allowlist.
- [ ] Confirm PostgreSQL 5432 and API 8000 are not publicly bound.
- [ ] Confirm only proxy ports 80/443 are public and hostnames reach their intended API.
- [ ] Scan images/logs/artifacts for secret leakage and add tests to existing security gates.
- [ ] Document shared-host risks: common VPS outage and potential impact from host compromise.

## Dependencies and acceptance

Depends on 02–09. Report evidence and limits; do not claim physical isolation.
