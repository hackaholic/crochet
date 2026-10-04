# 06 — R2/storage isolation

**Status:** Pending — depends on 01 discovery and 05 secrets/config.

## Goal

Ensure PREPROD tests cannot modify production product images or backups.

## Subtasks

- [ ] Inventory current product-image and backup buckets, public hostnames, DB URLs, and credential scope.
- [ ] Decide whether PREPROD needs a separate bucket/public hostname or read-only access to approved production media.
- [ ] Separate upload/write/delete credentials by environment; ensure backup buckets remain private.
- [ ] Update environment config and API asset URL behavior without hardcoding storage paths.
- [ ] Test that PREPROD credentials cannot write/delete production assets.

## Dependencies and acceptance

Depends on 01 and 05. No asset copy, bucket creation, deletion, or credential change during discovery; changes require a reviewed migration plan.
