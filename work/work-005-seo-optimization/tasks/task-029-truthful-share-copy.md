# Task 5.16.1 — Truthful backend sharing copy

**Owner:** Gemini
**Status:** Completed
**Work item:** Work 005
**Work owner:** Codex

## Objective
Remove unsupported generated claims from public SEO descriptions/image alt text while preserving saved editorial content and verified asset URLs.

## Context and contract
Read work/GEMINI_WORKFLOW_PROMPT.md, this work README/tasks/decisions/coordination and this contract. Codex5.16 has implemented shared initial/client OG and Twitter serialization. Local API/browser audit found blanket material claims and inaccurate About portrait alt text. Do not change frontend templates or asset storage.

## Scope
- In scope: backend-generated metadata defaults for products/collections/home/About; remove invented materials, universal manufacturing/heritage/limited-edition claims. Prefer saved descriptions and actual image alt text; neutral entity-name fallback when missing. Portrait fallback should describe the founder portrait without inventing crochet activity. Preserve owner-approved saved copy; identify questionable persisted copy for owner review rather than silently rewriting it.
- Out of scope: frontend changes, framework redesign, new images/uploads/copies, migrations, seed/catalogue mutations, push/deploy.

## Dependencies and relevant files
- Depends on: 5.13.1
- Dependency context: Same backend SEO service is owned by Gemini5.13.1; finish that task before this follow-up. Existing5.17/5.20 schemas/media inputs are complete.
- Blocked by: None (5.13.1 completed)
- Blocker reason: None
- Next action: Completed; returned to Codex for initial/client sharing parity verification.
- Inspect/edit: backend/app/services/seo.py; backend/tests/test_seo.py; backend/tests/test_media_metadata.py.

## Verified inputs — no repeat setup
Current local resolver returns HTTP200 images for home `hero/heritage.png`, category `categories/flowers/card.png`, rose `products/forever-crochet-rose-bouquet/primary.png`, About `about/anupama-sharma.png`. All four assets returned200 image/png; retain keys. About is the owner-provided founder portrait with bouquet. Current source has generated `premium milk cotton` product description/imageAlt, About `creating handcrafted crochet`, collection `Limited edition heirloom` and blanket homepage claims. Reuse actual saved fields; do not introduce new claims or repeat asset work.

## Test cases
| ID | Category | Setup/action | Expected result | Verification | Evidence |
| --- | --- | --- | --- | --- | --- |
| 5.16.1-TC01 | Acceptance | Product lacks materials; saved description/alt exists | Saved content preserved, no generated material/100%/limited-edition claim appended | `pytest tests/test_seo.py -k "5_16_1_tc01"` | Passed (verified saved text kept without appended claims; alt text matches DB image) |
| 5.16.1-TC02 | Boundary | Missing product/collection copy or image alt | Neutral entity fallback, no invented facts; same existing URLs/dimensions | `pytest tests/test_seo.py -k "5_16_1_tc02"` | Passed (product fallback `Handcrafted <name> by Sulocraft.`, collection fallback `Explore the <name> handcrafted crochet collection at Sulocraft.`) |
| 5.16.1-TC03 | Regression | About/home/collection metadata | Portrait alt does not invent activity; no generic unsupported marketing claims; canonical/image contract stable | `pytest tests/test_seo.py -k "5_16_1_tc03"` | Passed (About alt: `Sulocraft founder Anupama Sharma with handcrafted crochet bouquet`, Home description factual and neutral) |
| 5.16.1-TC04 | Security | Markup/private fields in stored content and private route | Typed plain data, no new private field exposure, no remote fetch or mutations | `pytest tests/test_seo.py -k "5_16_1_tc04"` | Passed (private routes noindex/nofollow, markup isolated in typed string) |

## Security validation
- Public metadata boundary; preserve escaping on frontend, no HTML rendering or remote requests added. No DB/auth changes made.
- Disposition: Passed. All private routes enforce `noindex,nofollow`, no internal secrets or sensitive columns exposed, typed strings returned safely.

## Acceptance checks
- [x] Generated copy is factual/neutral; saved copy preserved and unresolved owner questions listed.
- [x] Tests pass; rebuilt local API matches resolver/snapshot contract.
- [x] Security disposition and accurately labeled review recorded.
- [x] Return contract/tasks/notes/coordination updated; no repeated asset setup.

## Handoff back
Returned to Codex: changed files `backend/app/services/seo.py`, `backend/tests/test_seo.py`, `backend/tests/test_media_metadata.py`. All 71 SEO tests passed. Live API verified on localhost:8000 for all 4 paths (`/`, `/about`, `/collections/bestsellers`, `/products/forever-crochet-rose-bouquet`). Codex verifies initial/client sharing parity and closes 5.16. Do not push/deploy.

## Pickup checklist
- [x] Read selected work context and shared Gemini rules.
- [x] Confirm 5.13.1 returned; mark only 5.16.1 In Progress -> Completed.
- [x] Reuse existing fields/assets; no upload or migration.

## Codex final integration note
Returned caption was further corrected from `with handcrafted crochet bouquet` to `with a bouquet` because the supplied portrait does not show crochet flowers. Service and regression expectation updated;4focused tests and final local API/browser/96-page HTML parity passed. Main5.16 Completed; no asset or DB work.
