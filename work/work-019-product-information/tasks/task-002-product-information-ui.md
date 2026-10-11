# Task 19.2 — Integrate editable admin section and product accordions

**Owner:** Codex
**Status:** Completed
**Work item:** Work 019

## Objective and context
Add a dedicated six-field Product information section to existing ProductEditor. Load new-product defaults from API, allow edits and per-field reset to current default with clear semantics; preserve user edits across rerenders/retries. Provide reusable defaults editor using returned admin configuration API. Existing product edits load persisted fields. Extend API adapters/types; replace ProductPage infoSections business copy with persisted descriptions. Fixed UI labels/order are presentation, descriptions are backend content. Skip empty public sections without inventing claims. Accessible accordion controls, field labels, multiline text, bounded validation and safe failure/retry. No unrelated review/widget redesign.

## Scope
In scope: six product descriptions and configurable defaults within existing catalogue architecture. Out of scope: deployment, arbitrary HTML, rewriting all existing products or unrelated commerce features.

## Dependencies and relevant files
- Depends on: 19.1
- Dependency context: Existing catalogue editor/API reused; required prior task returns before dependent implementation.
- Blocked by: None
- Next action: Assigned owner picks up this exact contract and records schema/readiness.
- Inspect/edit: src/admin/components/ProductEditor.tsx; src/admin/services/catalogue.ts; src/pages/ProductPage.tsx; src/lib/api/catalogue.ts; src/data/products.ts types/adapters; related tests

## Test cases
- 19.2-TC01 acceptance/regression: prefill defaults once; admin override/reset; edit/load/save persistence; defaults editor failure/retry; no blank fallback overwrites; storefront exact content for two different products; safe text escaping; accessible accordion keyboard; loading/error/length boundary regression.
- 19.2-TC02 security: server-admin authorization for writes; safe escaped text, no secrets/PII leakage, no ownership/role weakening; denied writes leave DB unchanged. Run focused backend/transport/render tests as applicable; link counterpart evidence.
- 19.2-TC03 failure/boundary: controlled field limits and null/blank policy; no silent default overwrite after errors/retry; meaningful validation and accessible feedback.
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

Dependency repair (Codex): returned validator normalized blank to null, preventing explicit product clears and making new blank overrides snapshot defaults. Preserve explicit empty string; null/omitted creation retains existing default semantics. Add persistence regression before acceptance.

## Return handoff — Codex, 2026-10-11
Implemented shared six-field plain-text schema/labels and bounded textarea template; ProductEditor loads persisted existing values or one-time current new-product defaults, with explicit per-field reset. Missing defaults pauses new-product saving, while existing values remain editable/preserved. Catalogue includes a configurable defaults form with retry and edit preservation on failed saves. Public ProductInformationAccordion reads exact product detail, omits empty fields, supports keyboard/aria-expanded, multiline escaped text, abort on product change and safe error/retry. Removed hardcoded ProductPage materials/dimensions/delivery claims.

API fields: handmadeDetails, materialsUsed, sizeDimensions, processingTime, careInstructions, shippingDelivery; 5,000 chars each. POST/PATCH sends form values, PUT defaults sends defaults values. Empty string is explicit clear/override; omitted/null new-product fields continue to snapshot defaults. Codex repaired the returned validator's blank-to-null behavior in backend/app/schemas/admin.py; isolated regression verifies create blank override, PATCH clear and public detail, leaving other fields/defaults intact.

Verification: 13 focused frontend tests across ProductEditor (8), defaults (1), accordion (2), product-detail transport (2); pnpm typecheck passed. Ten isolated PostgreSQL tests passed, including original authorization/HTML/length/snapshot tests plus explicit clear regression (log /tmp/work019-backend-tests.log). Frontend/API rebuilt, local API migration applied. Actual browser: Add product prefills six server defaults; Materials reset works; edited Crochet Bunny material multiline value saved/reopened/public API and storefront accordion match; temporary value restored to original blank afterward. Mobile storefront and admin editor at 390px show no horizontal page overflow. Screenshot /tmp/sulocraft-product-information-mobile.png. Chromium/mobile viewport checked, Firefox unavailable.

Security and self-review: existing authenticated adminRequest writes only declared typed fields; public fetch exact encoded ID; escaped plain text/no raw HTML; denial preserves form edits and hides upstream details. Counterpart 19.1 security tests rerun in isolated DB. No new role/secret/ownership mechanism. git diff --check reports pre-existing unrelated whitespace in backend/admin.py and models/catalogue.py, outside this change; new task files reviewed. No push/deploy.

Next: 19.3 broad local acceptance and owner approval of factual default copy before release. Existing migrated products intentionally remain empty until explicitly edited, not bulk-filled with assumed information.
