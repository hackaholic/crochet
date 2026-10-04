# 11 — Cutover and operational validation

**Status:** Pending — depends on 01–10.

## Goal

Safely activate the isolated PREPROD and PROD routes while preserving existing data and a known rollback path.

## Subtasks

- [ ] Prepare alongside the current stack where feasible; capture and verify backups before any data move.
- [ ] Validate DNS/Cloudflare proxy and TLS for `api.sulocraft.com` and the confirmed PREPROD API hostname.
- [ ] Verify frontend-to-correct-API mapping, health, R2, OAuth callbacks, and restricted/preprod email behavior.
- [ ] Verify data persistence across container recreation and VPS reboot plan.
- [ ] Exercise application rollback and document migration recovery limitations.
- [ ] Obtain owner acceptance before routing customer traffic to PROD.
- [ ] Record final containers, networks, volumes, domains, secret groups, deployment, rollback, validation, and remaining manual actions.

## Dependencies and acceptance

Depends on 01–10. Do not destroy the prior deployment until the replacement is verified and the owner accepts cutover.
