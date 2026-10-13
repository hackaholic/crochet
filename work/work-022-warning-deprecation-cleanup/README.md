# Work022 — Warnings and deprecation cleanup

**Owner:** Codex
**Status:** Pending
**CURRENT:**22.1 — Starlette/TestClient transport warning

Objective: Resolve actionable warnings as they are encountered in normal development/test/build/deployment output; avoid a repository-wide warning hunt.

Known evidence: Work009 discovery tests passed25 tests with StarletteDeprecationWarning for TestClient/httpx transport, and DeprecationWarning for per-request cookies. Warning messages are recorded in exact contracts.

Scope: Small targeted fixes, compatible dependency changes only when required, meaningful regression/security checks. Add each distinct newly encountered warning as a focused task; deduplicate by cause. Do not hide warnings globally or upgrade dependencies indiscriminately.

Constraints: Gemini's current failing-test repair remains separate; coordinate overlapping test/dependency files before pickup. No implementation or push in this planning pass. Preserve environment parity and isolated test DBs.

Done when: Known tasks resolved with warning-free affected paths and regression evidence; existing contracts remain preserved. Future discoveries reopen/add tasks. No claim that the entire repository is warning-free.
