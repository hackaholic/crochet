# Work 002 — Product gallery media

**Objective:** Finish distinct, correctly mapped gallery images for Sulocraft's product catalogue.

**Scope:** Audit product SKUs and assigned media; add approved alternate views without replacing primary images; coordinate persisted image URL/key changes with Gemini when backend data changes are needed.

**Current state:** Pending in the active queue; earlier work exists and must be inspected before continuing.

**Dependencies:** `docs/product-media.md`, catalogue API, R2 upload workflow, and Gemini coordination files.

**Constraints:** Never reuse unrelated product images or hardcode product media in UI components. Verify local rendering before any push/deploy.

**Done when:** Each targeted product has valid distinct media, API records resolve the expected URLs, relevant tests pass, and local product galleries render correctly.
