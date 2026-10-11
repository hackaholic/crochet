# Task 19.3 — Verify new and existing product information end to end

**Owner:** Codex
**Status:** Completed
**Work item:** Work 019

## Objective and context
Rebuild affected local Docker services and verify localhost:8080/admin product creation/edit and public product page through actual API/PostgreSQL. Use disposable test records, preserve existing products, no real charges/emails. Confirm default changes affect new products only; six overrides roundtrip and storefront accordions reflect exact values after reload. Review default copy with owner, especially materials/dimensions/processing/shipping promises. Record Chrome/Firefox availability and mobile wrapping/keyboard checks. No push until user review.

## Scope
In scope: six product descriptions and configurable defaults within existing catalogue architecture. Out of scope: deployment, arbitrary HTML, rewriting all existing products or unrelated commerce features.

## Dependencies and relevant files
- Depends on: 19.1, 19.2
- Dependency context: Existing catalogue editor/API reused; required prior task returns before dependent implementation.
- Blocked by: None
- Next action: Assigned owner picks up this exact contract and records schema/readiness.
- Inspect/edit: docker/compose.yaml; frontend/backend tests; work-local contracts/notes

## Test cases
- 19.3-TC01 acceptance/regression: all six descriptions roundtrip; changed defaults vs existing overrides; missing values honest; customer cannot mutate; desktop/mobile and keyboard; existing catalogue/variants/tags/images regression; owner default-copy review recorded.
- 19.3-TC02 security: server-admin authorization for writes; safe escaped text, no secrets/PII leakage, no ownership/role weakening; denied writes leave DB unchanged. Run focused backend/transport/render tests as applicable; link counterpart evidence.
- 19.3-TC03 failure/boundary: controlled field limits and null/blank policy; no silent default overwrite after errors/retry; meaningful validation and accessible feedback.
Record concrete fixtures, test files/commands/results before completion. Runtime changes require local Docker/browser verification before push.

## Security validation
Pending: admin write trust boundary, validated bounded plain text, parameterized persistence, mass-assignment protection and safe storefront rendering. No raw HTML. Record findings and self-review; no fabricated factual assurances.

## Acceptance checks
- [x] Scope/API semantics documented and compatible with existing products.
- [x] Focused tests and security negatives pass; counterpart contract evidence linked.
- [x] Local integration evidence and limitations recorded.
- [x] Work-local return handoff updated, no unauthorized push/deploy.

## Handoff back
Update this exact contract, tasks.md, notes.md and coordination.md with fields/payload examples, migration/default behavior, tests/counts, security disposition and next dependency. Gemini first reads work/GEMINI_WORKFLOW_PROMPT.md. Do not duplicate live contract in global docs.

## Return handoff — Codex, 2026-10-11
Completed local acceptance. All six temporary multiline descriptions saved through the actual admin form, reopened unchanged, and individually displayed through keyboard-operated public accordions. Restored the product's original descriptions. Desktop/mobile viewport verified; product image loaded, no page overflow. Original creation/default prefill verified in19.2; isolated PostgreSQL acceptance creates products with all six fields and future defaults, verifies overrides/default changes leave existing product text intact, and preserves catalogue fields. User selected removal of unconfirmed timing/delivery promises; applied neutral defaults through exact-match defaults-only migration and verified actual admin fields. Custom defaults and existing products are not rewritten.

Found and fixed existing gallery recreation on unchanged product save, which removed alt text. API now preserves unchanged image records; added regression. Restored original local image metadata affected during acceptance. After final restart, complete public payload before/after browser save is identical, including gallery identities/alt text, variant IDs, SKU/stock, tags and descriptions. Restart seeding itself refreshed seeded image/variant IDs; this is an existing separate seed behavior, not a text-save change, and broader seed audit is outside19.3.

Checks: 12 isolated PostgreSQL product information cases pass (including authorization/length/plaintext negatives), one migration test passes (custom defaults/product text preserved and no downgrade promises), previous13 frontend/typecheck passes retained (frontend unchanged). Local frontend/API rebuilt and running, migrations applied. Security/self-review: parameterized exact-match defaults updates, preserve admin custom content, read-only public accordion, no HTML/secret leakage or new auth mechanism. Firefox unavailable; no Firefox claim. Screenshot /tmp/sulocraft-product-defaults-approved.png. Log /tmp/work019-acceptance-tests.log. No push/deployment.

19.1,19.2,19.3 complete. Owner wording decision recorded DEC019-5; no outstanding input for this work.
