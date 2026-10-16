# Task 5.2 — International SEO & hreflang architecture

**Owner:** Codex
**Status:** Completed

## Objective

Define supported-market, canonical-origin and optional hreflang policy without inventing international variants. Runtime/build implementation belongs to5.3/5.6/5.7 after backend contract return.

## Context and contract

Multi-region e-commerce requires explicit canonicalization, `hreflang` tags (including `x-default`), regional currency formatting hints, and localized metadata.

## Scope

- In scope:
  - Add `hreflang="en"` and `hreflang="x-default"` tags to page `<head>`.
  - Ensure canonical tags point unambiguously to canonical URL without tracking parameters.
  - Add locale/alternate metadata only for real approved supported markets; no invented en_US variant.
- Out of scope:
  - Full multi-language translation machine in V1 (content is in English).

## Dependencies and relevant files

- Depends on: 5.5
- Dependency context: Audit supported markets/languages and route facts first.
- Inspect/edit:
  - `src/components/SeoManager.tsx`
  - `backend/app/services/seo.py`
  - `scripts/prerender.mjs`

## Acceptance checks

- [x] Policy requires configured canonical and permits reciprocal hreflang only for approved real localized equivalents; implementation owners assigned.
- [x] Query/filter/pagination policy review remains5.7; unconditional removal of meaningful page parameters is prohibited by contract.

## Handoff back

- Update `work/work-005-seo-optimization/tasks.md` and `notes.md`.

## Planning clarification — 2026-10-13
**Work item:** Work 005
**Work owner:** Codex
Implementation boundary: Architecture decision only: validate real supported countries/languages before any hreflang. One English market does not require invented locales. Approved origin/indexing config mandatory.
- Blocked by: None
- Blocker reason: Dependency return not yet verified; do not start dependent implementation
- Next action: Read5.5 audit return and exact dependencies above

## Traceable test and security additions
- 5.2-TC01: Test stated acceptance against actual active DB records and raw HTML/client output; record exact automated/local commands and results.
- 5.2-TC02: Test missing/private/unapproved content, injected text/URLs and conflicting canonical/schema/environment input; no secrets, invented facts or duplicate head tags.
- Security: Safe JSON-LD/HTML escaping, bounded typed API data and validated origins; schema must match visible data. Record disposition and self/peer review.
- Local Docker/API/browser acceptance required for behavior changes; no push or production/account action in this planning task.
- Update exact contract plus work-local tasks/notes/coordination on return. Preserve original objective/history above; split ownership prevents duplicate work.

## Return —2026-10-13
DEC-005-7 records final policy. Document review scenarios: production valid origin+explicit indexing→eligible public index; local/preprod→noindex; missing production origin→fail closed; unapproved locale/equivalent missing→omit hreflang. These are specification checks, not claims runtime already changed. No app changes/tests required for this documentation-only decision. Security disposition Pass for policy (approved origins, no domain/secret fallback); Codex self-review. Runtime output/security tests mandatory in assigned implementation tasks. Country shipping/account facts remain owner-confirmed before Merchant rollout; no task blocker for defining safe default policy.
