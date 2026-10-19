# Task 7.10 — Ranked discovery local acceptance

**Owner:** Codex
**Status:** Completed
**Work item:** Work 007

## Objective and scope
After Gemini returns 7.6, verify real New arrivals/Featured/Trending/Popular sections, API ordering, eligibility, deduplication and pagination across basket and all checkout steps. Reuse the implemented adapter/template; no parallel copy of backend ranking or product fixtures. Backend must not issue reserved catalogue: compatibility cursors.

## Dependencies
- Depends on: 7.6, 7.6.1, 7.7
- Dependency context: UI and newest compatibility can be verified before ranked API exists; named ranking sections need the real backend return.
- Blocked by: None
- Blocker reason: None; Gemini7.6.1 returned tested fixes.
- Next action: Read task-008 returned contract/tests, rebuild relevant services and verify actual localhost/API.

## Tests and security validation
Verify backend integration test evidence for guest/auth ownership, cursor limits and active/stock eligibility. Exercise each supplied section and pagination, safe errors and retry without order/payment side effects; inspect full-width mobile/desktop rendering and images, preserve inputs across all steps. No fabricated ranking labels. Run affected tests/SAST once after any integration fix and record self-review, exact results and screenshots here. No push/deploy.

## Review checkpoint — 2026-10-20
API schema matches frontend. Service review found newest backfill exhausts candidates before Featured/Trending; returned six tests do not cover this. Created7.6.1 rather than silently accept missing requested sections. Work019/19.4 is independently completed with25tests/SAST/local proof.

## Integrated return — 2026-10-20
- Accepted returned7.6.1:9 isolated backend tests, purchase regression6 tests and SAST evidence recorded in task-013. Fair allocation and ranking/ownership negatives cover prior review findings.
- Live local public API first page: Popular6/New3/Featured5/Trending2 (16 total); next page8, zero overlapping IDs, terminal cursor null.
- Actual localhost checkout with guest cart: Recommended/Best Sellers/New Arrivals/Featured Picks/Trending Now all render; scrolling grows16→21 eligible cards. All sections remain through Delivery/Payment/Review; returning to Contact preserves Anupama. No order/payment submitted. Mobile390 page width380 has no overflow. [Browser proof](../reports/ranked-discovery-mobile.jpg).
- Integrated frontend release check: typecheck and30 relevant tests pass across checkout/cart/discovery/drawer/admin topbar/app, retaining safe-error/cursor/deduplication/async behavior. Earlier product-info14 backend+11 frontend and shared card tests remain valid; source unchanged since their checks.
- Security disposition Pass: returned tenant isolation/no-mutation/ranking tests reviewed; current public API integration read-only. Existing lower-severity SAST/deprecation warnings remain documented. Self-review complete. Native-engine matrix remains7.3, not claimed done.
- Owner now authorizes commit/push of all accumulated changes to dev; no production promotion.
