# 04 — Database and persistent-volume isolation

**Status:** Pending — depends on 02 container isolation.

## Goal

Guarantee PROD and PREPROD use distinct PostgreSQL databases, users, passwords, and persistent volumes.

## Subtasks

- [ ] Inventory current data/volume ownership and backups before planning any migration.
- [ ] Define separate DB names, users, credentials, and volumes from environment config.
- [ ] Ensure no PostgreSQL port is published on the host.
- [ ] Ensure each API receives only its environment's database URL/files.
- [ ] Run migrations independently and prove preprod cannot address PROD DB.
- [ ] Document backup/restore and migration compatibility.

## Dependencies and acceptance

Depends on 01–02 and Work 003 secret interfaces. No destructive data migration until a verified backup and owner-approved cutover plan exist.
