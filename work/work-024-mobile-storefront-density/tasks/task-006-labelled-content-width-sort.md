# Task 24.7 — Label and size compact sorting to selected text

**Owner:** Codex
**Status:** In Progress

## Scope / acceptance
Show visible `Sort by:` prefix and a thin subtle boundary around the complete sort control (owner refinement). Size selected-value/chevron presentation to current option, with small consistent arrow gap. Preserve native labelled select, keyboard/focus interaction,32px target, all sort options, breadcrumb flow and no mobile overflow. No backend/push.

## Dependencies
- Depends on: 24.6
- Blocked by: None
- Next action: Implement selected-text sizing, regression tests, local Docker/browser verification.

## Tests / security
Verify visible label and selected text after sort changes; price ordering and existing filters/escaping regressions. Browser320/390/430/1280, Featured and longest option fit; native focus/select remains usable. Presentation-only, no new trust boundary or HTML sink. No Gemini dependency.
