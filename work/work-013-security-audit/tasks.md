# Work 013 tasks

## In Progress

- [ ] 13.10 Codex: Remediate the failed `dev` frontend dependency audit and verify a passing security workflow.

## Pending

- [ ] 13.9 Gemini: VPS deployment SSH key hardening, capability restriction & least-privilege runner isolation per [task-009-ssh-deployment-hardening.md](tasks/task-009-ssh-deployment-hardening.md).
  - [ ] 13.9.1 SSH Capability Restriction (`no-pty`, `no-port-forwarding`, `no-agent-forwarding`, `no-X11-forwarding`)
  - [ ] 13.9.2 Dedicated Non-Root `deploy` System User
  - [ ] 13.9.3 Forced Command / Wrapper Enforcement
  - [ ] 13.9.4 Security Audit Verification

## Completed

- [x] 13.10 Codex: Patched frontend dependency advisories; pnpm 10.11.1 audit is clean and [Automated Security Release Gate run 37214436868](https://github.com/hackaholic/crochet/actions/runs/37214436868) passed all jobs.
- [x] 9.1 Gemini + Codex: Work directory structure, Threat Model, and Audit Policy per [task-001-threat-model-policy.md](tasks/task-001-threat-model-policy.md).
- [x] 9.2 Gemini: Secret scanning & secret architecture audit per [task-002-secrets-audit.md](tasks/task-002-secrets-audit.md).
- [x] 9.3 Gemini: Static Application Security Testing (SAST) & dependency auditing per [task-003-sast-deps.md](tasks/task-003-sast-deps.md).
- [x] 9.4 Gemini: Container & infrastructure security scanning per [task-004-container-infra.md](tasks/task-004-container-infra.md).
- [x] 9.5 Gemini: Custom backend authorization & e-commerce business logic tests per [task-005-auth-business-tests.md](tasks/task-005-auth-business-tests.md).
- [x] 9.6 Gemini: Dynamic security testing (DAST) & TLS auditing per [task-006-dast-tls.md](tasks/task-006-dast-tls.md).
- [x] 9.7 Gemini: Local pre-push security gate & master audit runner per [task-007-prepush-full-audit.md](tasks/task-007-prepush-full-audit.md).
- [x] 9.8 Gemini: CI security workflow (.github/workflows/security.yml) per [task-008-ci-security-workflow.md](tasks/task-008-ci-security-workflow.md).
