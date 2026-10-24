# Work 013 tasks

## In Progress

## Pending

- [ ] 13.12 Gemini: Schemathesis OpenAPI Property-Based Contract & Fuzz Testing per [task-012-schemathesis-api-fuzzing.md](tasks/task-012-schemathesis-api-fuzzing.md).
  - [ ] 13.12.1 Add `schemathesis>=3.38` to `backend/pyproject.toml` dev dependencies.
  - [ ] 13.12.2 Implement in-process ASGI pytest suite in `backend/tests/test_api_schemathesis.py` checking schema conformance, boundary values, and auth bypass detection.
  - [ ] 13.12.3 Implement standalone CLI runner script `scripts/security/scan-api-schemathesis.sh` targeting `/openapi.json` with JSON report output.
  - [ ] 13.12.4 Integrate into master release gate `scripts/security/full-audit.sh` and `.github/workflows/security.yml`.
- [ ] 13.13 Gemini: OWASP ZAP DAST Preprod Pipeline Integration & Authenticated Profiling per [task-013-zap-dast-preprod-pipeline.md](tasks/task-013-zap-dast-preprod-pipeline.md).
  - [ ] 13.13.1 Authenticated session profile support in `scripts/security/scan-dast.sh`.
  - [ ] 13.13.2 Automated post-deploy gating in `.github/workflows/deploy-dev-backend.yml`.
  - [ ] 13.13.3 Header, cookie flag, and XSS threshold tuning.
- [ ] 13.14 Gemini: Business-Logic & Authorization Test Matrix Expansion per [task-014-authorization-matrix-expansion.md](tasks/task-014-authorization-matrix-expansion.md).
  - [ ] 13.14.1 Tracking IDOR & guest token boundary tests (Work 017).
  - [ ] 13.14.2 Saved addresses and customer account multi-tenant isolation (Work 018).
  - [ ] 13.14.3 State transition and checkout tampering regression guards.
- [ ] 13.9 Gemini: VPS deployment SSH key hardening, capability restriction & least-privilege runner isolation per [task-009-ssh-deployment-hardening.md](tasks/task-009-ssh-deployment-hardening.md).
  - [ ] 13.9.1 SSH Capability Restriction (`no-pty`, `no-port-forwarding`, `no-agent-forwarding`, `no-X11-forwarding`)
  - [ ] 13.9.2 Dedicated Non-Root `deploy` System User
  - [ ] 13.9.3 Forced Command / Wrapper Enforcement
  - [ ] 13.9.4 Security Audit Verification

## Completed
- [x] 13.15 Codex — [Patch Vite/undici advisories](tasks/task-015-vite-undici-advisories.md): audit gate/typecheck/26tests/full build/local smoke pass.

- [x] 13.11 Gemini: Patch frontend source-map-js high advisory & add local audit test verification per [task-011-source-map-js-advisory.md](tasks/task-011-source-map-js-advisory.md). CI run: [38064775352](https://github.com/hackaholic/crochet/actions/runs/38064775352).
- [x] 13.10 Codex: Patched frontend dependency advisories; pnpm 10.11.1 audit is clean and [Automated Security Release Gate run 37214436868](https://github.com/hackaholic/crochet/actions/runs/37214436868) passed all jobs.
- [x] 9.1 Gemini + Codex: Work directory structure, Threat Model, and Audit Policy per [task-001-threat-model-policy.md](tasks/task-001-threat-model-policy.md).
- [x] 9.2 Gemini: Secret scanning & secret architecture audit per [task-002-secrets-audit.md](tasks/task-002-secrets-audit.md).
- [x] 9.3 Gemini: Static Application Security Testing (SAST) & dependency auditing per [task-003-sast-deps.md](tasks/task-003-sast-deps.md).
- [x] 9.4 Gemini: Container & infrastructure security scanning per [task-004-container-infra.md](tasks/task-004-container-infra.md).
- [x] 9.5 Gemini: Custom backend authorization & e-commerce business logic tests per [task-005-auth-business-tests.md](tasks/task-005-auth-business-tests.md).
- [x] 9.6 Gemini: Dynamic security testing (DAST) & TLS auditing per [task-006-dast-tls.md](tasks/task-006-dast-tls.md).
- [x] 9.7 Gemini: Local pre-push security gate & master audit runner per [task-007-prepush-full-audit.md](tasks/task-007-prepush-full-audit.md).
- [x] 9.8 Gemini: CI security workflow (.github/workflows/security.yml) per [task-008-ci-security-workflow.md](tasks/task-008-ci-security-workflow.md).
