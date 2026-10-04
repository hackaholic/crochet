# Work 012 notes

- 2026-10-04: Created the canonical Work 012 folder at `work/vps-environment-isolation/` to follow the owner-provided specification. Consolidated its deployment-workflow contract here; `work/work-012-vps-deployment/` is a duplicate and must not remain an active work item.
- 2026-10-04: Completed repository and read-only VPS discovery. Findings and unresolved hostname choice are recorded in `01-current-state/README.md`. No live VPS, DNS, secret, database, or service state was changed.
- 2026-10-04: Owner confirmed `api-dev.sulocraft.com` is the PREPROD API hostname. Updated the architecture and cleared the owner-choice blocker. DNS/TLS verification remains in item 03.
- 2026-10-04: Started item 02 with the local design direction for distinct `sulocraft-preprod`/`sulocraft-prod` Compose projects and a separately managed shared proxy. No runtime files or live VPS state changed in this step.
