# Task 5.15 — merchant center feed

**Owner:** Gemini
**Status:** Pending
**Work item:** Work 005
**Work owner:** Codex

## Objective
Implement centrally configured Merchant Center/free listings feed from eligible real catalogue entities/variants. Stable SKU IDs, titles/descriptions/public images/prices/currency/stock/canonical URLs/brand; validated policy config. Document missing approved shipping/returns and account actions.

## Context and contract
Read ../README.md, ../architecture.md, ../decisions.md and ../contracts/seo.md. Reuse existing SEO/API/image/product-detail work; no visual redesign. Gemini first reads work/GEMINI_WORKFLOW_PROMPT.md. Source audit5.5 controls readiness; this planning pass does not claim implementation complete.

## Scope
- In scope: Objective and acceptance below.
- Out of scope: Unrelated redesign, framework migration without ADR, production deployment, fabricated business facts or external-account changes.

## Dependencies and relevant files
- Depends on: 5.5, 5.6, 5.7, 5.17, 5.18, 5.19, 5.20
- Dependency context: Wait for dependency return and inspect actual code/API evidence; do not rebuild already completed foundations.
- Blocked by: None
- Blocker reason: None; external ownership/config requirements must be recorded at pickup
- Next action: Verify dependency readiness, then mark only this assigned task In Progress.
- Inspect/edit: backend/services and schemas for product feed; thin SEO/feed routes; catalogue repositories; backend tests; env/config examples

## Test cases (define before implementation)
| ID | Category | Input/action | Expected result | Verification | Evidence |
| --- | --- | --- | --- | --- | --- |
| 5.15-TC01 | Acceptance/regression | Representative real catalogue and public route fixtures | Feed validates against current official specification with stable variants/IDs and landing-page price/stock parity; only eligible active products exported. | Focused automated/API/raw HTML/browser checks applicable to task; record exact command/target | Not run |
| 5.15-TC02 | Failure/security | Invalid/unapproved/missing/private data and environment boundaries | Missing GTIN/MPN handled truthfully, never invented; absent merchant/policy facts reported clearly; no customer/private data, XML injection, internal URLs or draft records; bounded generation/caching. | Negative tests or documented read-only review when no application behavior changes | Not run |

## Security validation
- Treat content/path/media URL/feed data as untrusted; typed bounded fields, escaping/serialization and safe URL/config validation.
- API/DB changes: object/field authorization for edits, parameterized queries, least privilege, no private customer/session/secret data in public SEO.
- Documentation-only tasks: no application trust boundary changes; check docs for credentials and unsupported factual claims.
- Disposition: Pending; record commands/results, findings, owner and blockers before return.

## Acceptance checks
- [ ] Feed validates against current official specification with stable variants/IDs and landing-page price/stock parity; only eligible active products exported.
- [ ] Missing GTIN/MPN handled truthfully, never invented; absent merchant/policy facts reported clearly; no customer/private data, XML injection, internal URLs or draft records; bounded generation/caching.
- [ ] Relevant tests pass; Docker/API and actual local browser checks where behavior changes, before push.
- [ ] Security disposition and accurately labeled self/peer review recorded.
- [ ] Work-local docs updated; no unapproved business facts or design changes.

## Handoff back
Return to Codex: feed URL/schema/sample fixtures/tests and owner Merchant Center setup checklist. Update this exact contract, tasks.md, notes.md and coordination.md with status/files/tests, dependency readiness and blockers. Preserve completed contracts and source provenance. Global docs link here only; no push/deploy without gated approval.

## Pickup checklist
- [ ] Read work/INDEX.md and selected Work005 files plus this contract only.
- [ ] Confirm owner/dependencies; mark only assigned task In Progress.
- [ ] Reuse existing verified assets/endpoints and record questions rather than inventing facts.
