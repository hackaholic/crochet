# Task 5.5 — current seo audit

**Owner:** Codex
**Status:** Completed
**Work item:** Work 005
**Work owner:** Codex

## Objective
Audit initial HTML, live client rendering, actual route/status behavior, metadata/schema, images, links, filtering, sitemap/robots and performance. Produce severity-ranked evidence and implementation order; no application changes.

## Context and contract
Read ../README.md, ../architecture.md, ../decisions.md and ../contracts/seo.md. Reuse existing SEO/API/image/product-detail work; no visual redesign. Gemini first reads work/GEMINI_WORKFLOW_PROMPT.md. Source audit5.5 controls readiness; this planning pass does not claim implementation complete.

## Scope
- In scope: Objective and acceptance below.
- Out of scope: Unrelated redesign, framework migration without ADR, production deployment, fabricated business facts or external-account changes.

## Dependencies and relevant files
- Depends on: None
- Dependency context: Read-only task ready now; select this as CURRENT.
- Blocked by: None
- Blocker reason: None; external ownership/config requirements must be recorded at pickup
- Next action: Perform read-only audit and return prioritized findings.
- Inspect/edit: src/App.tsx; src/lib/routes.ts; src/components/SeoManager.tsx; scripts/prerender*.mjs; backend/app/services/seo.py; backend/app/schemas/seo.py; deployment routing config

## Test cases (define before implementation)
| ID | Category | Input/action | Expected result | Verification | Evidence |
| --- | --- | --- | --- | --- | --- |
| 5.5-TC01 | Acceptance/regression | Representative real catalogue and public route fixtures | Compare raw HTML and hydrated DOM for home/product/category/collection/info/private/missing routes; record actual status, canonical and critical visible fields. | Focused automated/API/raw HTML/browser checks applicable to task; record exact command/target | Not run |
| 5.5-TC02 | Failure/security | Invalid/unapproved/missing/private data and environment boundaries | Identify static/DB divergence, duplicate/query URLs and fabricated facts; preserve design and report unknowns instead of treating them as verified. | Negative tests or documented read-only review when no application behavior changes | Not run |

## Security validation
- Treat content/path/media URL/feed data as untrusted; typed bounded fields, escaping/serialization and safe URL/config validation.
- API/DB changes: object/field authorization for edits, parameterized queries, least privilege, no private customer/session/secret data in public SEO.
- Documentation-only tasks: no application trust boundary changes; check docs for credentials and unsupported factual claims.
- Disposition: Pending; record commands/results, findings, owner and blockers before return.

## Acceptance checks
- [x] Compare raw HTML and hydrated DOM for home/product/category/collection/info/private/missing routes; record actual status, canonical and critical visible fields.
- [x] Identify static/DB divergence, duplicate/query URLs and fabricated facts; preserve design and report unknowns instead of treating them as verified.
- [x] Relevant tests pass; Docker/API and actual local browser checks where behavior changes, before push.
- [x] Security disposition and accurately labeled self/peer review recorded.
- [x] Work-local docs updated; no unapproved business facts or design changes.

## Handoff back
Return to Codex: read-only audit report in this task; architecture.md and contracts/seo.md for durable decisions. Update this exact contract, tasks.md, notes.md and coordination.md with status/files/tests, dependency readiness and blockers. Preserve completed contracts and source provenance. Global docs link here only; no push/deploy without gated approval.

## Pickup checklist
- [x] Read work/INDEX.md and selected Work005 files plus this contract only.
- [x] Confirm owner/dependencies; mark only assigned task In Progress.
- [x] Reuse existing verified assets/endpoints and record questions rather than inventing facts.

## Return —2026-10-13
Audit report: [task005 findings](../reports/task-005-audit.md). Public HTTP/API/DOM evidence in adjacent reports. Frontend baseline3 tests and prerender2 tests pass via scripts/test.sh frontend; backend SEO9 tests pass via scripts/test.sh backend tests/test_seo.py. Build:56 static routes. No application changes or deployment; security disposition Pass for read-only audit (findings remain assigned implementation tasks), Codex self-review. Unknown external account/CWV/edge403 access recorded honestly. Gemini5.17/5.19/5.20 dependencies now ready;5.18 waits5.17. Next Codex5.2 policy decision.
