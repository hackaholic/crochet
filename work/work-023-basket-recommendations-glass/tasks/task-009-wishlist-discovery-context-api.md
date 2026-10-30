# Work 023.9 — Wishlist discovery context in the API

**Owner:** Gemini
**Status:** Completed
**Work item:** Work 023

## Objective

Allow the existing bounded storefront discovery API to serve Wishlist's layered recommendation feed using a distinct `wishlist` context.

## Context and contract

Current `GET /api/v1/storefront/discovery` accepts only `checkout|basket`; the shared frontend feed scopes its opaque pagination cursor by context. Wishlist should reuse the existing database-driven discovery strategies/sections and bounded pagination. This is a context/validation extension, not a new recommendation engine. Do not add hardcoded catalogue data, wishlist personalization claims, or a migration.

## Scope

- In scope: accept `wishlist` as an allowed context, ensure cursors are context-scoped, return the existing bounded public catalogue sections, add backend tests and security validation.
- Out of scope: checkout/basket ranking changes, reading customer wishlist records, new endpoint/table/columns, client changes, credentials, deployment.

## Dependencies and relevant files

- Depends on: 23.3
- Dependency context: existing discovery strategies and opaque pagination are complete.
- Blocked by: None
- Blocker reason: None
- Next action: Returned/Completed by Gemini; Codex unblocked for [23.8 Wishlist layered discovery UI](task-008-wishlist-recommendation-ui.md).
- Inspect/edit: `backend/app/api/v1/storefront.py`, `backend/app/services/discovery.py`, `docs/api-storefront.md`, `docs/openapi.yaml`, `backend/tests/test_storefront_discovery.py`.

## Test cases (define before implementation)

| ID | Requirement/subtask | Category | Setup/actor and action | Expected response and state | Test file/command or manual procedure | Result/evidence |
| --- | --- | --- | --- | --- | --- | --- |
| 23.9-TC01 | Wishlist context returns existing feed | Success | Request `/storefront/discovery?context=wishlist&limit=16` | Valid bounded sections with active public products and correct response schema | `backend/tests/test_storefront_discovery.py::test_23_9_tc01_wishlist_context_returns_existing_feed` | PASS (200 OK; `<=5` sections, `<=8` products/section, `<=16` total active in-stock public products, 0 duplicates) |
| 23.9-TC02 | Wishlist pagination advances safely | Boundary/regression | Follow returned cursor using `context=wishlist` | Cursor advances, products do not repeat, page/product bounds hold | `backend/tests/test_storefront_discovery.py::test_23_9_tc02_wishlist_pagination_advances_safely` | PASS (cursor `<=512` chars with `"c":"wishlist"`, page 1 & page 2 disjoint, bounds respected) |
| 23.9-TC03 | Cursor cannot cross contexts | Failure/security | Reuse wishlist cursor under basket or checkout context | Reject invalid/mismatched cursor safely; no private data or state change | `backend/tests/test_storefront_discovery.py::test_23_9_tc03_cursor_cannot_cross_contexts` | PASS (`wishlist` cursor replayed on `basket`/`checkout` and `basket`/`checkout` cursors replayed on `wishlist` all rejected with `422`) |
| 23.9-TC04 | Invalid contexts remain rejected | Failure | Send unsupported `context` value | Request fails validation (422), no side effect | `backend/tests/test_storefront_discovery.py::test_23_9_tc04_invalid_contexts_remain_rejected` | PASS (`invalid`, `wishlists`, `WISHLIST`, `account`, `admin`, `wishlist;drop` all fail with `422`) |
| 23.9-TC05 | Wishlist remains private | Security | Call endpoint unauthenticated and inspect payload | Response contains only public catalogue data; no customer wishlist IDs/items | `backend/tests/test_storefront_discovery.py::test_23_9_tc05_wishlist_remains_private` | PASS (seeded `Wishlist`/`WishlistItem` untouched; response contains only `sections` + `nextCursor` public catalogue items; 0 DB mutations) |

## Security validation

- Changed assets/trust boundaries and plausible abuse: Public GET query parameter (`context`) and cursor parsing (`decode_cursor` / `encode_cursor`). Risk: accepting malformed context/cursor could mix pagination results across surfaces or disclose private wishlist data.
- Applicable controls and linked negative test IDs: FastAPI Query pattern allowlist `^(checkout|basket|wishlist)$`, service-level `ALLOWED_DISCOVERY_CONTEXTS = {"checkout", "basket", "wishlist"}` enforcement in `encode_cursor`/`decode_cursor`, context-bound opaque cursor validation (`data.get("c") == expected_context`), zero `Wishlist`/`WishlistItem` database lookups or customer identifiers in discovery response (`23.9-TC03`, `23.9-TC04`, `23.9-TC05`).
- API/database work: no schema migration; parameterized ORM queries, eligible/active in-stock product filtering, existing bounded query/page limits (`<=16` total products, `<=5` sections, `<=8` products/section, cursor `<=512` chars) and safe `422` validation handling.
- Commands/target/results and evidence (redacted):
  - `(cd backend && bash scripts/run_isolated_tests.sh tests/test_storefront_discovery.py)` -> `14 passed in 7.8s` (`9` existing discovery tests + `5` new `23.9-TC01`..`TC05` tests)
  - `bash scripts/security/scan-sast.sh` -> `PASS: Zero blocking High/Critical SAST findings detected`
  - Live Docker API rebuilt and verified: `GET http://localhost:8000/api/v1/storefront/discovery?context=wishlist&limit=4` -> `200 OK` returning bounded `sections` and `nextCursor`.
- Disposition: Pass
- Findings, severity, remediation owner, and blockers: None.

## Acceptance checks

- [x] API accepts `wishlist` and preserves current `checkout`/`basket` behavior.
- [x] Cursor remains opaque/context-bound; response stays bounded and public catalogue-only.
- [x] Relevant backend tests, security checks and local API integration pass.
- [x] Update this contract, Work023 tasks, notes, and coordination with files/schema effects and evidence; return to Codex.

## Handoff back

Codex will consume the returned context in [23.8](task-008-wishlist-recommendation-ui.md), implement Wishlist rendering, then run integrated Docker/browser acceptance. Do not edit Wishlist frontend files or push/deploy as part of this backend task.

## Pickup checklist

- [x] Read `work/GEMINI_WORKFLOW_PROMPT.md`, Work023 README/tasks/decisions/coordination, and this contract.
- [x] Confirm Gemini ownership and mark only 23.9 In Progress; update Work023 coordination to Active.
- [x] No migrations, media uploads, or credentials are required.
