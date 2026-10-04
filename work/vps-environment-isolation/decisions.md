# Work 012 decisions

## DEC-012-001 — Separate VPS environment work from the secret vault

**Decision:** Work 012 owns PROD/PREPROD environment isolation and deployment mechanics. Work 003 owns SOPS/age secret encryption, decryption, key safety, and rotation. Work 006 owns CI/CD triggers and calls the shared deployment interface.

**Reason:** Keep ownership clear and avoid duplicating vault implementation or CI deployment behavior.

## DEC-012-002 — Preserve the three-stage release gate

**Decision:** Verify locally first, deploy and validate in preprod next, and promote the same tested artifact to production only after preprod is stable and accepted. Differences between environments should be configuration/secrets only.

## DEC-012-003 — Use logical isolation on the existing VPS

**Decision:** Use the current VPS and Docker Compose approach; do not add Kubernetes or unrelated infrastructure. Treat one VPS as a shared physical failure/compromise domain.

## DEC-012-004 — Discovery precedes implementation

**Decision:** Item 01 must be documented and reviewed before item 02. The owner reviewed it on 2026-10-04 and confirmed `api-dev.sulocraft.com` as the PREPROD API hostname, superseding the example `api-preprod.sulocraft.com` in the supplied target. Validate live DNS/TLS in item 03; do not change DNS based on this decision alone.

## DEC-012-005 — Use one parameterized Compose definition with separate project identities

**Decision:** Item 02 will evaluate a shared parameterized Compose definition launched as distinct `sulocraft-preprod` and `sulocraft-prod` projects, without fixed `container_name` values. Project-scoped services and named volumes must not collide. The shared public proxy must be separated from the per-environment API/database stack so the two environments cannot claim the same host ports.

**Reason:** Keep definitions maintainable while allowing both environments to coexist on one host. Compose project scoping gives distinct runtime identities; the proxy split avoids port conflicts.

**Status:** Design direction for local validation in item 02; not yet implemented or deployed.
