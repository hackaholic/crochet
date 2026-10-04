# Task 13.10 — Resolve failed dev security release gate

**Owner:** Codex
**Status:** In Progress
**Work item:** Work 013 / Automated security audit & release gate

## Objective

Resolve the frontend dependency findings that caused the security release gate to fail on commit `e98b53f21d24798975658686df4bdf206ea28cd7`, then verify the push-triggered security workflow passes.

## Context and contract

- Failed run: [Automated Security Release Gate #8](https://github.com/hackaholic/crochet/actions/runs/37210927884).
- Failed job: `Frontend Dependency Audit`; `pnpm audit --audit-level=high` reported 9 vulnerabilities (6 high, 3 moderate), including Vite, PostCSS, and nanoid advisories. The downstream `Master Security Release Gate` consequently failed.
- The other listed security jobs passed in this run.
- Preserve the fail-closed release-gate policy. Prefer compatible patched dependency updates and lockfile regeneration. Use an exception only if the policy permits it and the risk is documented and approved; do not lower the audit threshold just to make CI green.

## Scope

- In scope: inspect affected dependency paths and available patched versions, update compatible dependencies/lockfile, run frontend audit/build/tests, and verify a new `dev` security workflow run passes.
- Out of scope: backend CI test failures (tracked in Work 006 Task 6.3.5), backend deployment implementation, and production release.

## Dependencies and relevant files

- Depends on: Work 013 Tasks 9.3 and 9.8 (dependency scanner and CI release gate).
- Inspect/edit: frontend `package.json`, `pnpm-lock.yaml`, `.github/workflows/security.yml`, and relevant frontend tests/build configuration.

## Acceptance checks

- [x] All high-severity findings are resolved with patched versions or explicitly approved, documented exceptions.
- [x] `pnpm audit --audit-level=high` passes locally using the lockfile generated and checked with pnpm 10.11.1.
- [x] Frontend tests (25 files / 60 tests), typecheck, and preprod build pass under Node 24.19.0.
- [ ] A new push-triggered security workflow completes with all required jobs and `Master Security Release Gate` successful.

## Handoff back

- Update Work 013 `tasks.md`, `notes.md`, and `coordination.md` with changed packages, scan output summary, and the successful/failed GitHub run URL.
- Report any advisory that cannot be fixed without a breaking change before expanding scope.

## Pickup checklist

- [ ] Read `work/INDEX.md`, Work 013 `README.md`, `tasks.md`, `decisions.md`, `coordination.md`, and this contract.
- [ ] Confirm task ownership before changing its status to In Progress.
- [ ] Preserve the current security threshold and avoid unrelated dependency upgrades.
