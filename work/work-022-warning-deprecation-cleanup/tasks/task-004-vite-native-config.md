# Task 22.4 — Vite native config deprecation
**Owner:** Codex
**Status:** Pending
**Work item:** Work022

## Objective
Replace deprecated CommonJS __dirname usage in vite.config.ts with an ESM-compatible path resolution supported by the project's pinned runtime. Do not suppress Vite warnings or globally upgrade Vite.

## Context and contract
Work005 audit build/preview emitted: configLoader native is planned default; __dirname(vite.config.ts:10:25) unsupported; use import.meta.dirname. Inspect exact installed Node/Vite compatibility before choosing implementation.

## Scope
Targeted config fix and regressions only; no SEO redesign or global dependency changes.

## Dependencies and relevant files
- Depends on: None
- Dependency context: Captured during Work005 audit; this is separate queued work
- Blocked by: None
- Blocker reason: None
- Next action: Inspect pinned runtime/config support when assigned
- Inspect/edit: vite.config.ts; build/dev config tests

## Test cases
- 22.4-TC01: Shared test.sh frontend build, dev/preview proxy and module alias paths work and this warning is absent.
- 22.4-TC02: Execution from another cwd/pinned supported Node still resolves repository paths safely; no warning suppression or config/import regression.

## Security validation
Preserve proxy targets/path boundaries and environment configuration; no arbitrary import/path expansion. Record exact checks/security disposition and self/peer review. Pending.

## Acceptance checks
- [ ] Specific warning removed by supported config API; tests/build/local browser pass.
- [ ] No broad suppression or unrelated upgrade; isolated environment controls preserved.
- [ ] Work-local evidence/status/coordination updated.

## Handoff back
Return files, exact test commands and before/after warning evidence in this task and work-local notes/coordination. No push without user instruction.
