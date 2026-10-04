# Work 012.09.1 — One-command immutable environment promotion

**Owner:** Codex
**Status:** Pending — starts after current-state discovery and the upstream safe-test gate
**Work item:** Work 012 / 09 Deployment workflow

## Objective

Provide a root-level command that promotes one immutable backend image through local verification, PREPROD, and PROD while selecting only environment-specific configuration and secrets at deployment time.

## Context and contract

- Follow `work/vps-environment-isolation/README.md`, `architecture.md`, `09-deployment-workflow/README.md`, and `01-current-state/README.md`.
- Work 003 owns SOPS/age secrets. Work 012 owns environment isolation and deployment. Work 006 owns CI triggers and calls this interface.
- Use the existing VPS and `/opt/sulocraft` layout unless Work 01 documents why a compatible adjustment is required. Do not introduce Kubernetes or a VPS-side Git clone.
- Deployment must use one immutable image ID/tag based on commit SHA in PREPROD and PROD; never rebuild from a different source revision for PROD.
- Keep the local → preprod → production gate: locally tested, preprod tested/stable, then explicit production promotion. Production changes config/secrets only.

## Scope

- In scope: root-level CLI, explicit target/config parsing, immutable image creation/promotion, per-environment Compose/config/secrets, preflight, DB backup/migrations, health validation, release state, rollback, operator docs, and fake-remote tests.
- Out of scope: actual production credentials, production DNS changes, changing SSH/firewall/users, or live production cutover.

## Dependencies and relevant files

- Depends on Work 01 discovery, Work 003 Task 3.13 safe tests and Task 3.14 config interface, plus approved designs from Work 02–08.
- Coordinate with Work 006 Task 6.3; it must call the shared command rather than duplicate release logic.
- Inspect/edit existing Compose, `backend/scripts/deploy_vps.sh`, bootstrap scripts, reverse proxy, workflows, and deployment docs only after discovery.

## Acceptance checks

- [ ] Root-level documented command selects `preprod` or `prod` through explicit config/arguments and fails closed on missing/unknown settings.
- [ ] Local gate blocks untested/dirty source; deployment records the exact commit and immutable image digest.
- [ ] PREPROD and PROD run separate API/DB containers, networks, volumes, and credentials; only proxy has public ports 80/443.
- [ ] PREPROD migration/runtime credentials cannot reach or modify PROD database/storage/secrets.
- [ ] PREPROD email recipient restrictions and environment-specific OAuth URLs are verified.
- [ ] Preprod receives a locally verified image; production promotes the exact same immutable image after stability/owner acceptance and changes only config/secrets.
- [ ] Backups, health checks, application rollback, and migration limitations are documented and tested without exposing secrets.
- [ ] Automated security tests prove isolation; local Docker/browser/API checks pass before any preprod deployment.
- [ ] No VPS/Cloudflare changes occur before owner-authorized cutover.

## Handoff back

- Update the Work 012 root status and relevant high-level item README after each completed item; update this contract and Work 09 task state.
- Keep detailed execution notes in the relevant numbered work item, not in one giant file.
- Never report unverified VPS, DNS, resource, or security state as fact.
