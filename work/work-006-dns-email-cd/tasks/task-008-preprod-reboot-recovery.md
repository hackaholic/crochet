# Task 6.8 — Restore preprod API after reboot

**Owner:** Codex
**Status:** Completed
**Work item:** Work 006

## Objective / scope
Restore the existing verified preprod deployment without deploying the uncommitted local tree or changing production. Diagnose outage, regenerate runtime secret files using the existing on-server encrypted vault/key/bootstrap, restart existing containers, verify public health/catalogue/browser. Preserve database volume and all secret values.

## Dependencies and relevant files
- Depends on: None
- Dependency context: Existing VPS root access, installed release and encrypted vault; no new credentials or assets required.
- Blocked by: None
- Blocker reason: None
- Next action: Inspect release/bootstrap inputs, materialize missing preprod runtime files, start database then API.
- Inspect: deployed backend/scripts/bootstrap_secrets.sh; existing container mount/state metadata; proxy health.

## Diagnosis
2026-10-19: Public health/home return502. Both preprod containers exited127 after host restart; OCI bind mounts fail because `/run/sulocraft/preprod/backend/database_url` and `/run/sulocraft/preprod/postgres/postgres_db` no longer exist. Reverse proxy is running. No Sulocraft systemd boot unit installed. Runtime `/run` is ephemeral. No evidence of disk/memory pressure.

## Tests / acceptance
- [x] Capture public502 and exact container mount failure without secret values.
- [x] Existing vault bootstrap succeeds; secret files remain restricted, no plaintext logged/copied locally.
- [x] Same containers/images/DB volume restored and healthy; no migrations or code rollout requested.
- [x] Public health and storefront API return200; actual dev browser renders catalogue.
- [x] Record durable reboot-recovery follow-up separately; no claim of automatic recovery until implemented/tested.

## Security / review
Only restore preprod secret files from existing authorized vault using existing age identity. Never print secret contents, inspect full container environment, reset DB or use production fallback. Self-review: Pass for operational recovery. Existing encrypted vault/bootstrap and exact existing containers reused; permissions0700/0600 verified. No new application code or database reset.

## Handoff back
Update work-local tasks/notes/coordination with health evidence, root cause and next recovery task. No push or unverified local release.

## Return — 2026-10-19
Restored runtime secret files with installed release bootstrap `--env preprod --runtime-dir /run/sulocraft/preprod`; started existing PostgreSQL then API containers. Existing release810301bcd8a1 retained; no images rebuilt, no files rsynced and no local code deployed. Both containers healthy. Public `/health`200withstatusok; `/api/v1/storefront/home`200withbrand/hero/sections. Actual `https://dev.sulocraft.com/` retry cleared unavailable state; real product links and9loadedmainimages observed. [Browser proof](../reports/task-008-recovered-preprod.jpg).

Root cause: host restart cleared volatile `/run` secret mounts; Docker containers exited127 because source files were absent. No boot-time secret rehydration service exists. Durable prevention retained as pending6.9; immediate recovery does not fix reboot recurrence. No secrets printed or transferred to local machine.
