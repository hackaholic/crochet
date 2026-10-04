# 08 — Resource limits and environment-aware logging

**Status:** Pending — depends on 01 discovery and 02 container isolation.

## Goal

Keep PREPROD resource consumption from starving PROD on the shared VPS and make logs identify their environment.

## Subtasks

- [ ] Inspect actual VPS CPU, RAM, disk, current load, and container runtime capabilities.
- [ ] Set reasoned CPU/memory/pids limits and reservations/priority for API, PostgreSQL, and proxy services.
- [ ] Prefer PROD under contention and keep limits within measured host capacity.
- [ ] Include environment identity in service names and structured logs.
- [ ] Validate limits and restart/log behavior without causing production downtime.

## Dependencies and acceptance

Depends on 01–02. Do not copy example limits blindly or apply limits to live services before local validation and owner review.
