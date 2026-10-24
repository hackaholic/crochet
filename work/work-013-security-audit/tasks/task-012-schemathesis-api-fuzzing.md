# Task 13.12 — Schemathesis OpenAPI Property-Based Contract & Fuzz Testing

**Owner:** Gemini
**Status:** Completed
**Work item:** Work 013 / Automated security audit & release gate

## Objective

Integrate **Schemathesis** into the Sulocraft security testing suite to automatically scan and fuzz all FastAPI endpoints from `/openapi.json`. Automatically generate boundary, malformed, and randomized inputs to detect:
1. Unhandled 500 Internal Server Errors on unusual inputs or edge-case IDs.
2. OpenAPI schema non-conformance (endpoints returning undocumented status codes or schemas).
3. Auth bypass failures (unauthenticated or malformed tokens unexpectedly receiving 200).
4. Content-type and header contract violations.

Provide both an in-process, network-free pytest suite (`backend/tests/test_api_schemathesis.py`) and a standalone CLI runner script (`scripts/security/scan-api-schemathesis.sh`) that integrates into the master release gate.

## Context and contract

- Tool Reference: [Schemathesis Documentation](https://schemathesis.readthedocs.io/).
- Architecture Decision: DEC-009-1 (Defense in Depth across release levels) and DEC-013-4 (Schemathesis contract testing).
- OpenAPI Endpoint: `http://localhost:8000/openapi.json` and in-memory ASGI app `app.main.app`.
- Policy: Zero 500 errors or unhandled schema violations on valid or invalid inputs.

## Scope

- In scope:
  - Add `schemathesis>=3.38` to `backend/pyproject.toml` (dev dependencies).
  - Create `backend/tests/test_api_schemathesis.py` with direct ASGI testing against `app` (fast, deterministic, container-compatible).
  - Configure checks: `not_a_server_error`, `status_code_conformance`, `content_type_conformance`, and auth validation.
  - Create `scripts/security/scan-api-schemathesis.sh` for live scanning against running local or preprod endpoints with structured JSON reporting (`work/work-013-security-audit/reports/schemathesis-report.json`).
  - Wire into `scripts/security/full-audit.sh` and `.github/workflows/security.yml`.
- Out of scope:
  - Modifying business authorization tests (covered in Task 13.14).
  - Live production fuzzing (strictly prohibited).

## Dependencies and relevant files

- Depends on: None
- Dependency context: Backend FastAPI application running with OpenAPI enabled at `/openapi.json`.
- Blocked by: None
- Blocker reason: None
- Next action: Ready for pickup.
- Inspect/edit:
  - `backend/pyproject.toml`
  - `backend/tests/test_api_schemathesis.py`
  - `scripts/security/scan-api-schemathesis.sh`
  - `scripts/security/full-audit.sh`
  - `.github/workflows/security.yml`

## Test cases (define before implementation)

| ID | Requirement/subtask | Category | Setup/actor and action | Expected response and state | Test file/command or manual procedure | Result/evidence |
| --- | --- | --- | --- | --- | --- | --- |
| 13.12-TC01 | OpenAPI schema fuzzing without 500 crashes | Security / Fuzzing | Run Schemathesis against all public storefront/catalogue routes | All generated inputs return valid HTTP status codes (2xx, 4xx); zero 500 server errors | `bash backend/scripts/run_isolated_tests.sh backend/tests/test_api_schemathesis.py` | PASS: 99/99 in-process tests passed; caught and fixed integer overflow in `min_price`/`max_price`/`page` and `payment_id` |
| 13.12-TC02 | Schema response conformance | Contract | Schemathesis validates response headers and body against OpenAPI schema | Zero schema validation mismatches or undeclared properties violating spec | `bash backend/scripts/run_isolated_tests.sh backend/tests/test_api_schemathesis.py -k test_public_routes` | PASS: Public routes conform to OpenAPI specification with zero status code/content-type mismatches |
| 13.12-TC03 | Auth bypass fuzzing on protected routes | Security | Send randomized/missing auth tokens to `/api/v1/admin/*`, `/api/v1/orders/*`, `/api/v1/profile/*` | Zero endpoints return 200 without valid credentials; properly returns 401 or 403 | `bash backend/scripts/run_isolated_tests.sh backend/tests/test_api_schemathesis.py -k test_protected_routes` | PASS: All unauthenticated fuzzed requests rejected with 401/403/400/404/422; 0 auth bypasses |
| 13.12-TC04 | Standalone CLI runner script | Release Gate | Run `scripts/security/scan-api-schemathesis.sh` against local Docker API | Generates `schemathesis-report.json`, exits 0 on pass, exits 1 on detected vulnerability | `bash scripts/security/scan-api-schemathesis.sh` | PASS: 654 test cases generated and passed across 142 operations; 0 crashes; exits 0 |
| 13.12-TC05 | CI & full-audit integration | Integration | Execute master audit runner `scripts/security/full-audit.sh` | Schemathesis step executed and recorded in `summary.md` matrix | `bash scripts/security/full-audit.sh` / `.github/workflows/security.yml` | PASS: Integrated into `full-audit.sh` and `security.yml` `security-tests` job |

## Security validation

- Changed assets/trust boundaries: Dynamic API input parsing and boundary fuzzing across all public and protected HTTP endpoints.
- Applicable controls: Input validation via Pydantic models, integer overflow protection, safe 404/422 responses, and unhandled exception guards.
- API/database work: Read and write fuzzing against disposable test databases only; verify zero data corruption or unhandled DB driver exceptions.
- Disposition: Passed. Fuzzing discovered two unhandled integer overflow vectors in `GET /api/v1/products` and `POST /api/v1/payments/verify`; both patched with Pydantic bounds (`le=100_000_000` and `le=2_147_483_647`) returning clean 422 errors instead of 500 DB driver exceptions.

## Acceptance checks

- [x] `schemathesis` added to dev dependencies.
- [x] `backend/tests/test_api_schemathesis.py` implemented and passing against isolated test container.
- [x] `scripts/security/scan-api-schemathesis.sh` implemented with structured JSON report output.
- [x] `scripts/security/full-audit.sh` and `.github/workflows/security.yml` updated and passing.
- [x] Evidence recorded in task contract and work-local notes.

## Handoff back

Update `work/work-013-security-audit/tasks.md`, `notes.md`, and `coordination.md` with execution results and report links.
