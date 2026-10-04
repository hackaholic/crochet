# Work 013 — Sulocraft Automated Security Audit & Release Gate

**Objective:** Establish a permanent, automated security-audit workflow and release gate across local development, CI pull requests, and deployed development environments.

**Scope:**
1. Level 1: Local / Pre-push security checks (Gitleaks, Semgrep, dependency audits, fast tests).
2. Level 2: CI / Pull Request security gate (GitHub Actions jobs for secrets, SAST, dependencies, container config, authorization & business logic tests).
3. Level 3: Deployed Development Environment dynamic scanning (OWASP ZAP baseline DAST + TLS audit with test accounts against `https://dev.sulocraft.com` and development API).
4. Threat modeling, audit policies, exception workflows, and consolidated reporting.

**Current state:** In Progress. Tasks 9.1–9.8 and 13.10 are completed. Task 13.9 runner SSH hardening remains pending by owner direction.

**Architecture:**
- Security policy: Fail-closed on High/Critical actionable findings.
- Zero feature redesign: pure security infrastructure, test suites, and gating scripts.
- Secrets: strictly enforce the SOPS + age vault architecture.

**Done when:** All Level 1, 2, and 3 security check scripts exist in `scripts/security/`, authorization and business logic tests pass in `backend/tests/`, CI workflow `.github/workflows/security.yml` gates releases, and full audit reports `PASS`.
