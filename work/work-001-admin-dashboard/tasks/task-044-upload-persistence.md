# Task 1.7.12 — Real admin upload persistence and honest image errors

**Task ID:** 1.7.12
**Owner:** Gemini
**Status:** Completed
**Work item:** Work 001

## Objective
Admin photo uploads must render the actual uploaded bytes and survive service recreation. Missing images must not silently substitute unrelated Unsplash content.

## Context and contract
Work0011.6 browser acceptance followed the uploaded key `products/0a78532f6c4f.png`. It returns307 to an Unsplash photo. The apparent loaded-image check under1.7.6 was insufficient: the displayed image was unrelated to the supplied upload. `MockStorageProvider` stores bytes only in a newly instantiated in-memory dictionary. Durable1.7.11 sequences already returned; do not repeat that fix.

## Scope
- In scope: validate configured storage provider/upload bytes persistence; configuration-selected local durable storage or configured R2; correct served image URLs; no silent mock fallback when an explicitly configured provider fails; remove unrelated remote placeholder fallback for missing uploaded keys.
- Out of scope: replacing approved product images, bulk uploads, frontend redesign, deployment, secrets changes.

## Dependencies and relevant files
- Depends on: None
- Dependency context: Read work/GEMINI_WORKFLOW_PROMPT.md; reuse existing upload endpoint, configured image URL helper and admin authorization. Missing asset must fail honestly. Same code path selected by environment/config in production/preprod; no preprod-only fix.
- Blocked by: None
- Next action: Return to Codex for Task 1.7.6 real local browser upload/save/reopen.
- Inspect/edit: backend/app/services/storage/{factory,mock,r2,local}.py, backend/app/main.py image route, upload endpoint, tests.
- Verified inputs: original approved test file `public/images/products/crochet-tulip-bouquet/primary.png`; returned key above. Existing QA listing is ARCHIVED; do not activate it. No new credentials needed for durable local test storage.

## Test cases
| ID | Scenario | Expected | Result |
| --- | --- | --- | --- |
|1.7.12-TC01|Admin uploads valid image; retrieve URL|Actual uploaded bytes/image returned, no unrelated substitution|Passed|
|1.7.12-TC02|Recreate storage provider/service|File still retrievable from configured persistent storage|Passed|
|1.7.12-TC03|Missing key/provider failure|Honest404/safe failure; no Unsplash/mock success fallback|Passed|
|1.7.12-TC04|Unauthorized/invalid/oversized/traversal upload|401/403/400; no storage side effect or arbitrary filesystem write|Passed|

## Security validation
Preserve admin access/CSRF, MIME/size checks, safe generated filenames, path containment and least-privilege storage credentials. Never print credentials or persist them in code. Confirm no storage writes on denied requests.

## Acceptance checks
- [x] Actual image content survives provider recreation.
- [x] Missing/upload/provider failures do not fabricate success.
- [x] Tests/security/self-review recorded; local configuration documented.

## Handoff back
Task 1.7.12 completed:
- Implemented `LocalStorageProvider` in `backend/app/services/storage/local.py` for durable filesystem persistence under `public/images/`.
- Updated `backend/app/services/storage/factory.py` so that environments without Cloudflare R2 credentials automatically persist to local disk rather than dropping files into an ephemeral dictionary.
- Removed arbitrary Unsplash fallback from `backend/app/core/images.py` and `backend/app/main.py`. Requests for unmapped missing images now return an honest HTTP 404 (`{"detail": "Image not found"}`).
- Verified 5/5 storage test suite cases in `backend/tests/test_storage.py` and 2/2 media tests in `backend/tests/test_admin_product_media.py`.
- Rebuilt and restarted `docker-api-1`. Verified live image upload and exact byte retrieval against `http://localhost:8000`, and confirmed honest 404 on nonexistent image keys.
- Returning to Codex for unblocked Task 1.7.6 catalogue browser acceptance. No git push or VPS deployment performed.
