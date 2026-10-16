# Task 5.21 — seo monitoring followup

**Owner:** Codex
**Status:** Completed
**Work item:** Work 005
**Work owner:** Codex

## Objective
Prepare lightweight weekly/monthly SEO checks for indexed pages/crawl errors/impressions/clicks/CTR/queries/landing pages/schema/CWV/Merchant issues, with owners and next actions. No new analytics platform.

## Context and contract
Read ../README.md, ../architecture.md, ../decisions.md and ../contracts/seo.md. Reuse existing SEO/API/image/product-detail work; no visual redesign. Gemini first reads work/GEMINI_WORKFLOW_PROMPT.md. Source audit5.5 controls readiness; this planning pass does not claim implementation complete.

## Scope
- In scope: Objective and acceptance below.
- Out of scope: Unrelated redesign, framework migration without ADR, production deployment, fabricated business facts or external-account changes.

## Dependencies and relevant files
- Depends on: 5.14, 5.15
- Dependency context:5.14/5.15 preparation returned. Planning clarification: this task prepares the monitoring plan; live rollout/field baselines depend on5.4 and account/traffic availability, not prerequisites to writing an honest plan. No automated schedule created.
- Blocked by: None
- Blocker reason: None; external ownership/config requirements must be recorded at pickup
- Next action: Verify dependency readiness, then mark only this assigned task In Progress.
- Inspect/edit: work-local monitoring checklist; existing CI/check scripts and release docs

## Test cases (define before implementation)
| ID | Category | Input/action | Expected result | Verification | Evidence |
| --- | --- | --- | --- | --- | --- |
| 5.21-TC01 | Acceptance/regression | Representative real catalogue and public route fixtures | Small scheduled cadence/action thresholds and export/report location; distinguish baseline data from missing external account data. | Focused automated/API/raw HTML/browser checks applicable to task; record exact command/target | Passed; documentation/security self-review, account/field state explicitly unavailable |
| 5.21-TC02 | Failure/security | Invalid/unapproved/missing/private data and environment boundaries | No ranking/indexing guarantees, credentials or unnecessary tracking/PII collection; unresolved launch/account dependencies remain visible. | Negative tests or documented read-only review when no application behavior changes | Passed; documentation/security self-review, account/field state explicitly unavailable |

## Security validation
- Treat content/path/media URL/feed data as untrusted; typed bounded fields, escaping/serialization and safe URL/config validation.
- API/DB changes: object/field authorization for edits, parameterized queries, least privilege, no private customer/session/secret data in public SEO.
- Documentation-only tasks: no application trust boundary changes; check docs for credentials and unsupported factual claims.
- Disposition: Pass; documentation-only, no credentials/account changes, unsupported completion claims or new telemetry.

## Acceptance checks
- [x] Small scheduled cadence/action thresholds and export/report location; distinguish baseline data from missing external account data.
- [x] No ranking/indexing guarantees, credentials or unnecessary tracking/PII collection; unresolved launch/account dependencies remain visible.
- [x] Relevant tests pass; Docker/API and actual local browser checks where behavior changes, before push.
- [x] Security disposition and accurately labeled self/peer review recorded.
- [x] Work-local docs updated; no unapproved business facts or design changes.

## Handoff back
Return to Codex: monitoring checklist and launch handoff. Update this exact contract, tasks.md, notes.md and coordination.md with status/files/tests, dependency readiness and blockers. Preserve completed contracts and source provenance. Global docs link here only; no push/deploy without gated approval.

## Pickup checklist
- [x] Read work/INDEX.md and selected Work005 files plus this contract only.
- [x] Confirm owner/dependencies; mark only assigned task In Progress.
- [x] Reuse existing verified assets/endpoints and record questions rather than inventing facts.

## Return —2026-10-16
[Monitoring runbook](../checklists/monitoring.md): per-publication/deployment, weekly and monthly checks; owners, failure triggers, report location/privacy and truthful missing-baseline status. Documentation-only security/self-review Pass; no credentials, PII collection, new telemetry or unrequested automation. Test matrix satisfied by checklist review; field data explicitly not collected.
