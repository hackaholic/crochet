# Task 13.15 — Patch Vite and undici release-gate advisories

**Owner:** Codex
**Status:** Completed

## Objective / scope
Unblock frontend high-severity dependency audit by patching Vite>=8.3.3 and undici8>=8.12.2 (GHSA-587h-7wmj-h5pm, GHSA-xjj6-f33q-929c). Update package constraints and pnpm10 lockfile together. Do not bypass/disable security gate or widen deployment scope.

## Dependencies
- Depends on: None
- Blocked by: None
- Next action: Push verified fix to dev and await CI/deployment outcome.

## Acceptance / security
Verify patched versions in resolved dependency graph; pnpm audit --audit-level=high passes without suppressions. Frozen install, typecheck, affected Vitest/jsdom catalogue tests and build pass. Rebuild frontend and inspect localhost minimally. Record residual lower-severity advisories and unverified CI/deployment. No Gemini dependency. Existing push/deployment-fix authorization applies to dev only.

## Verified inputs
- [Vite advisory](https://github.com/advisories/GHSA-587h-7wmj-h5pm):8.3.3 patched minimum for installed8.3 line.
- [undici advisory](https://github.com/advisories/GHSA-xjj6-f33q-929c):8.12.2 patched minimum for installed8.x line.
- Generated lock resolves Vite8.3.5 and undici8.12.3. Frozen Docker install passed. No new application feature/tests required; audit is the direct security acceptance and existing jsdom/build regressions validate compatibility.

## Return — 2026-10-24
- Patched Vite constraint^8.3.3 (resolved8.3.5), added scoped undici8 override^8.12.2 (resolved8.12.3), regenerated pnpm10.11.1 lock. Security threshold unchanged, no advisory suppressions.
- Frozen Docker install passed; normal local frontend rebuilt/restarted. `pnpm audit --audit-level=high` exit0:0high/critical,2moderate remain.26 focused jsdom/Vitest catalogue/price/config tests and typecheck passed. This dependency-only patch adds no application behavior; audit and existing regressions are the direct security/compatibility checks.
- Full `pnpm build:dev` passed client+SSR+prerender+SEO resources+performance budgets (JS115691/120000 gzip,CSS16979/20000). Local verification inputs: SEO_INDEXING_ENABLED=false; SEO_PUBLIC_ORIGIN=https://dev.sulocraft.com; SEO_API_BASE_URL=http://api:8000/api/v1; SEO_EDGE_API_BASE_URL=https://api-dev.sulocraft.com/api/v1. Earlier verification commands missed required public routing settings/API prefix; corrected command passed without code changes or weakening validation.
- Actual localhost Amigurumi smoke:9cards/9loaded images after new Vite restart. Existing UI unaffected. Native Firefox/device coverage not repeated for dependency patch.
- Self-review/security Pass for both requested High advisories: patched versions resolved, audit gate passes.2moderate audit findings and existing react-router/React peer/deprecation warnings are residual, not hidden/suppressed. No backend/auth/secret changes. Evidence reports/task-015-checks.txt.
- No Gemini dependency. CI/deployed acceptance pending new dev push; do not equate local pass with successful remote deployment.
