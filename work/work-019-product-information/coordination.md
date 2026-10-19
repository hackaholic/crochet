# Work 019 coordination

**Work lead:** Codex.

| Task | Owner | Handoff | Dependency |
| --- | --- | --- | --- |
| [19.1](tasks/task-001-product-information-api.md) | Gemini | Returned | Existing catalogue APIs |
| [19.2](tasks/task-002-product-information-ui.md) | Codex | Returned | 19.1 returned typed contract |
| [19.3](tasks/task-003-product-information-acceptance.md) | Codex | Returned | 19.1, 19.2 |

Task 19.1 returned by Gemini with typed contract and verified tests. Ready for Codex to pick up Task 19.2.

Codex19.2 Returned: UI + targeted blank-clear repair verified locally. 19.3 ready; owner default-copy approval remains before release. No push/deployment.

19.3 Completed: all-six-field UI roundtrip, defaults isolation, gallery regression fixed, owner neutral copy applied. No remaining handoff/input; exact evidence in task-003.

## Current pickup — 2026-10-20
Codex active on [19.4 missing specifications](tasks/task-004-missing-storefront-information.md). First verify actual API data vs rendering; no hardcoded defaults or changes to explicit blank behavior. Gemini 7.6 remains independent.

19.4 Returned/Completed2026-10-20: backend defaults resolve missing public values, product/SEO consistency verified.14 backend +11 frontend tests, SAST and24-product API/browser audit pass. Exact return task-004. No new Gemini dependency, no push.
