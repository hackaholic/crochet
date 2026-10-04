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

**Status:** Implemented and locally validated in Work 012 items 02–03; not deployed to the live VPS.

## DEC-012-006 — Require target-specific database secret paths and projects

**Decision:** Each deployment selects `sulocraft-${TARGET_ENV}` and a target-specific runtime secret directory. Compose requires explicit host-file paths for the database and database URL secrets; missing paths fail configuration. Bootstrap rejects missing PROD encrypted groups and validates that the API URL matches the selected database name and credentials.

**Reason:** Prevent two environments from mounting the same PostgreSQL credentials or sharing project-scoped persistent storage through defaults.

**Impact:** PREPROD and PROD volumes, networks, and secret sources remain separate. The current PREPROD encrypted groups cannot be used to start PROD. Production remains unavailable until its own config and encrypted groups are provisioned. Existing legacy PREPROD data still requires an item 11 backup/restore/cutover plan.

## DEC-012-007 — One deploy command with an explicit environment target

**Decision:** The final operator interface is `./deploy_vps.sh --env preprod` for the PREPROD environment serving `dev.sulocraft.com`, and `./deploy_vps.sh --env prod` for production. The environment argument is mandatory; the script must never guess or default the target. A separate config input may supply the target-specific host, release root, Compose inputs, and encrypted secret group path. The selected environment must always map to its own Compose project, database volume, networks, runtime secrets, and public hostname.

**Promotion rule:** `--env preprod` deploys the locally verified commit as a new immutable image. `--env prod` promotes only the exact image already deployed and accepted in preprod; it must not rebuild the image. Missing production configuration/secrets or a missing accepted preprod release fails closed.

**Status:** Required interface; remote deploy and promotion implementation is pending in Work 012 item 09.
