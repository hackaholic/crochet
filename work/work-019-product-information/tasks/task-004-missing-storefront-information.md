# Task 19.4 — Missing product-information accordions regression

**Owner:** Codex
**Status:** Completed
**Work item:** Work 019

## Objective and scope
Trace actual product API data through storefront product-page rendering to find why editable specification disclosures disappear. Restore persisted product information using owner-approved product-first/default-second resolution for null, blank or whitespace values; no invented details or product-record rewrites. Preserve completed work and Gemini Work007/7.6 ownership.

## Dependencies
- Depends on: 19.1, 19.2, 19.3
- Dependency context: Existing schema, persisted defaults, UI and local Docker are available; verify actual data before choosing remediation.
- Blocked by: None
- Blocker reason: None
- Next action: Inspect actual public API and product page, reproduce, add regression test, fix the verified cause.

## Tests and security validation
Cover real product detail -> page -> six disclosure fields, click/keyboard expansion, omission only when resolved product/default content is empty, product switching, failed fetch safe retry, stale snapshots and escaped plain text. No fabricated factual claims, private admin data or silent DB overwrite. Resolve missing public values from persisted backend defaults; no frontend business-text fallback. Run relevant Docker tests/typecheck, applicable security checks and rebuild affected services; verify actual localhost/API/browser and record self-review/evidence here before completion. No push/deploy.

## Owner clarification / verified cause
2026-10-20: Owner says use specifications if provided, otherwise defaults. Read-only audit found 24/24 products with no populated specification fields: 23 all-null, 1 all-empty. Code retained six accordions; the public API returned raw empty fields while SEO FAQs already used defaults. Implement one resolver for public product fields and SEO fields/FAQs, preserve admin raw edits/storage. Add backend API+SEO+no-write regression and retain unauthorized defaults-edit tests. Codex owns this small independent backend fix; Gemini continues Work007/7.6 without interruption.

## Return — 2026-10-20
- Root cause verified: all 24 local catalogue products lacked stored information; 23 were null, one all-empty. Accordion code still existed. API raw fields and SEO entity ignored existing configured defaults, while SEO FAQs already used them. Before audit: reports/task-004-public-information-audit.json.
- Owner clarified saved specifications first, otherwise defaults (DEC019-6 supersedes old blank-hides rule). Added shared backend service resolver for public product API and SEO entity/FAQs. No product record or default copy changed; admin storage/edit API remains raw. If both sources are empty, no claims are invented.
- Tests: 14 backend tests passed, including real DB/public API/SEO six-field consistency, override precedence, null/blank/whitespace fallback, no-write verification, unauthorized edits, input-size and stored-XSS validation. Frontend typecheck and 11 product-page/accordion/adapter tests passed, including six disclosures from the actual page and safe plain-text rendering. Initial frontend process exited137; isolated rerun passed and is the acceptance evidence. Existing Starlette/httpx/cookie deprecation warnings remain Work022, not suppressed.
- SAST PASS, zero blocking High/Critical findings; existing lower-severity repository findings unchanged. Security disposition Pass; self-reviewed resolver has no writes, new endpoint or admin-secret exposure.
- Rebuilt/restarted local API. Post-fix public API audit: 24/24 products now expose all six fields, recorded in reports/task-004-resolved-information-audit.json. Actual localhost product page shows all six sections; each expanded correctly. Mobile390 width has no overflow. Desktop/mobile screenshots: reports/restored-product-information.jpg and reports/restored-product-information-mobile.jpg. Frontend runtime unchanged, so no unnecessary frontend rebuild.
- No push/deploy. No additional Gemini work needed for this fix; Gemini7.6 remains separate.
