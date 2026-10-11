# Task 20.26 — Stable popup loading height

**Owner:** Codex
**Status:** Completed
**Work item:** Work 020

## Objective and scope
Prevent entity dialogs expanding abruptly when API content arrives. Shared dialog reserves responsive height, fixed header and independently scrolling content. No data/API/navigation changes.

## Dependencies
- Depends on: 20.24
- Blocked by: None
- Dependency context: Native entity dialogs locally verified; sizing currently intrinsic to asynchronously loaded content.

## Acceptance/tests
Dialog frame height unchanged for loading, loaded and error content; desktop/mobile fit, internal overflow works, close/Escape/focus unaffected. Focused dialog tests/typecheck, Docker rebuild and localhost browser size check.

## Security and handoff
Presentation only, existing authorization unchanged. Record self-review and checks here; update work tasks/notes/coordination. No push.

## Verified return
2026-10-11: shared dialog reserves min(42rem,90dvh) height; fixed header, independent content scrolling. 6 focused preview tests passed, typecheck passed. Docker frontend rebuilt/restarted. Local customer popup frame measured672px at y114 on desktop before/after subsequent observation; mobile630px within700px viewport, width358px within390px viewport, content scrolling522px/1093px. Async-content regression confirms dialog identity/close focus retained. Security/self-review Pass: CSS/container-only change, native modal semantics unchanged. Screenshot /tmp/admin-stable-popup.png. Firefox unverified. No push.
