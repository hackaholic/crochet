# Task 5.18.1 — Global snapshot version consistency
**Owner:** Gemini
**Status:** Completed
**Work item:** Work005

## Objective
Return one global versionHash for all pages of the same complete public SEO snapshot, covering actual metadata/entities/prices/stock/images/brand/config changes. Existing get_content_snapshot hashes only paginated path/lastmod/title, so different pages have different versions and price changes may be missed.

## Dependencies and relevant files
- Depends on: 5.18
- Dependency context: Codex5.6 needs consistent multi-page build inputs
- Blocked by: None
- Blocker reason: None
- Next action: Returned to Codex; global versionHash verified across pages and mutations.
- Inspect/edit: backend/app/services/seo.py; tests/test_seo.py; docs/api-seo.md

## Scope
Global version and bounded deterministic public snapshot only; no frontend edits, private data or DB resets.

## Test cases/security
- 5.18.1-TC01: All pages share the same version for unchanged public snapshot; deterministic ordering and limits retained. Passed (`test_content_snapshot_endpoint` asserts `data1["versionHash"] == data2["versionHash"]`).
- 5.18.1-TC02: Price/stock/title/image/brand or eligible route deletion changes version even without parent updated_at changes; no draft/private/customer payloads in hash output. Passed (`test_snapshot_version_consistency_and_mutation` verifies in-place variant price change immediately updates versionHash on all pages, while draft products do not alter the public hash).
Parameterize ORM reads, bound generation and avoid secret-derived values.
Security disposition: Passed; version hash uses public route inventory, active entity models, and store brand settings only. No customer, draft, secret, or private administrative records are hashed or leaked. Full regression suite clean (420 passed, 7 skipped).

## Acceptance/handoff
- [x] Exact version contract, mutation/page tests and isolated runner results returned to Codex; no push.
Update this contract plus work-local tasks/notes/coordination. Read work/GEMINI_WORKFLOW_PROMPT.md. Codex temporarily double-reads full typed snapshot for consistency; will use global version after return.
