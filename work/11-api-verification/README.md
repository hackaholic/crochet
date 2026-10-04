# Work 011 — Automated API Verification & Reporting Suite

**GitHub Issue:** [#11](https://github.com/hackaholic/crochet/issues/11) · Work 011

**Objective:** Automate local and CI-ready API verification and structured report generation for the Sulocraft e-commerce platform, covering storefront content resolution, catalogue querying and filtering, and admin occasion governance and evergreen constraints.

**Scope:**
- Standalone Python verification script (`scripts/verify_api.py`) with zero external runtime dependencies (using Python standard library).
- Automated test coverage of Storefront Home API, Catalogue Occasions, Product Filtering by Occasion, and Admin Occasions governance.
- Verification of evergreen business rules (non-disabling, non-scheduling, non-deletable) and seasonal schedule management.
- Generation of human-readable Markdown test reports in `work/11-api-verification/reports/` with granular check breakdown, HTTP latency, and status codes.
- Repeatable execution against local Docker environments or deployed stages via `--base-url`.

**Architecture:**
- Standalone test runner with modular check classes/methods.
- Checks execute real HTTP requests against the running API container.
- Results collected into structured objects that render both formatted terminal output and detailed Markdown reports.

**Definition of Done:**
- `scripts/verify_api.py` successfully exercises all target endpoints and validation checks.
- Generates a timestamped markdown report in `work/11-api-verification/reports/`.
- Exits with return code 0 on complete pass, non-zero on failure.
- Documented in `tasks.md`, `decisions.md`, and referenced in `work/INDEX.md`.
