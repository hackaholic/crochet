# Task 7.7 — Scrollable database-driven discovery

**Owner:** Codex
**Status:** Completed
**Work item:** Work 007

## Objective and scope
Render backend-ordered sections using reusable ProductCard with shared async Quick Add. Fetch bounded additional pages near scroll end with visible Load more fallback/retry; stop on exhaustion/nonadvancing cursor. Deduplicate across sections/pages and exclude basket products. Same feed persists across contact/delivery/payment/review. Failure never blocks checkout. Until 7.6 exists, compatibility fallback uses real paginated newest catalogue only, labelled honestly; no fake featured/trending/popular labels. Implement deterministic adapter/component failure/security tests; frontend integration remains pending real 7.6 return.

## Dependencies
- Depends on: 7.5
- Dependency context: 7.6 supplies ranked sections; 7.7 can implement typed client and honest catalogue compatibility independently.
- Blocked by: None
- Blocker reason: None
- Next action: Execute assigned scope and return evidence.

## Security and acceptance
Meaningful tests and security validation are mandatory: escaped API text, no private errors, no duplicate add/order side effects, bounded requests and safe URLs, keyboard/touch controls. Run focused Docker tests/typecheck, SAST, rebuild frontend and inspect actual localhost before completion. Record evidence, self-review and remaining limitations. No push/deploy.

## Return — 2026-10-20
- Implemented ProductRecommendations + useDiscoveryFeed + validated productDiscovery adapter. Server sections/order/labels render generically, deduplicated across pages and excluding cart items; one bounded abortable request at a time, retry/load-more, scroll observer and repeated-cursor/exhaustion/page-budget stops. Shared request budgets live in src/config/discovery.ts.
- Local API currently returns 404 for ranked discovery; explicit compatibility uses real newest catalogue pages and does not invent Featured/Trending/Popular. Eligible newest products fill the first row after exclusions. Actual localhost scrolling grew 5 to 13 cards; first row remains 4, next New arrivals grows dynamically.
- Tests: full focused run 22/22 passed; final packing adds one regression, affected adapter/component rerun 7/7 passed. Unique final coverage 23 tests. Typecheck passed. Includes auto-scroll, duplicate concurrent load guard, error retry, repeated cursor, cursor/page bounds, unsafe image URL rejection, cart exclusion, safe text, failed add and all four checkout steps.
- Security disposition Pass: SAST zero blocking High/Critical, existing lower-severity repository warnings unchanged. No private error exposure, new raw HTML/credentials/PII storage, payment/order side effects or client-selected ranking URLs. API fallback occurs only for missing initial endpoint, never 403/429/5xx. Self-reviewed; trust-boundary negative tests pass.
- Frontend implementation Completed; real ranked-section integrated verification intentionally remains 7.10, dependent on Gemini 7.6. No claim those sections are live yet.

Browser evidence: [wide checkout](../reports/discovery-wide-checkout.jpg), [mobile checkout](../reports/discovery-mobile-checkout.jpg), [catalogue preview](../reports/discovery-catalogue-preview.jpg). Native browser/device matrix remains 7.3; only local in-app rendering is claimed.
