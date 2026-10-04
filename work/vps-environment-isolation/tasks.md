# Work 012 — PROD/PREPROD isolation task status

## Completed

- [x] 01 — Current-state discovery; documented repo and read-only VPS baseline, owner confirmed `api-dev.sulocraft.com` for PREPROD.

## In Progress

- [ ] 02 — Container isolation; validate separate Compose project identities locally.

## Pending

- [ ] 03 — Networking and reverse-proxy routing
- [ ] 04 — Database and persistent-volume isolation
- [ ] 05 — Secret and non-secret configuration isolation
- [ ] 06 — R2/storage isolation
- [ ] 07 — Email and OAuth isolation
- [ ] 08 — Resource limits and environment-aware logging
- [ ] 09 — Deployment workflow and same-artifact promotion
- [ ] 10 — Security/isolation validation
- [ ] 11 — Cutover and operational validation

## Blocked

- None. Live DNS/TLS validation remains in item 03; it does not block local item 02 work.
