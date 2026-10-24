# Security coordination

This file is the work-local coordination entry point. The work folder is the source of truth: read this file with README.md, tasks.md, decisions.md, and only the assigned task contract.

## Current handoffs

Task 13.11 (frontend source-map-js advisory & local audit test verification) is completed by Gemini; [security workflow run 38064775352](https://github.com/hackaholic/crochet/actions/runs/38064775352) passed all jobs including frontend audit and Master Security Release Gate. Task 13.10 is completed. Task 13.9 (VPS SSH deployment hardening) remains pending. Newly planned subtasks: [13.12 Schemathesis API fuzzing](tasks/task-012-schemathesis-api-fuzzing.md), [13.13 OWASP ZAP preprod DAST pipeline](tasks/task-013-zap-dast-preprod-pipeline.md), and [13.14 Authorization & business-logic matrix expansion](tasks/task-014-authorization-matrix-expansion.md).

## Return protocol

The assigned agent updates the exact contract, tasks.md, notes.md, and this file before returning the task. The global registry at docs/handoffs.md points here; it does not duplicate this work's status.

13.15 Active — Codex: Vite/undici dependency audit blocker; task-015 contract, no Gemini dependency.

13.15 Returned/Completed — Codex: patched Vite8.3.5/undici8.12.3; unchanged high-severity audit passes,26tests/typecheck/full build and local9image smoke passed. Task-015 return/evidence. CI/deployment pending push, no Gemini dependency.

13.12 Returned/Completed — Gemini: Schemathesis OpenAPI Property-Based Contract & Fuzz Testing; task-012 contract. In-process test suite (`backend/tests/test_api_schemathesis.py`) and standalone CLI runner (`scripts/security/scan-api-schemathesis.sh`) implemented and integrated into `scripts/security/full-audit.sh` and `.github/workflows/security.yml`. Discovered and patched integer overflow vulnerabilities on `GET /api/v1/products` and `POST /api/v1/payments/verify`. 654 live test cases and 123 isolated container tests passing.
