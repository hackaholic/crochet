# Work 009 decisions

### DEC-009-1 — Defense in Depth across 3 Release Levels

**Decision:** Enforce security checks across three distinct boundaries:
- Level 1: Local / Pre-push (fast developer feedback under 60 seconds).
- Level 2: CI / Pull Request (complete static analysis, container scan, and backend authorization suites).
- Level 3: Deployed Development Environment (OWASP ZAP baseline DAST and TLS audit).

**Reason:** Catches vulnerabilities as early as possible without slowing down daily local iteration or risking destructive scans against live environments.

### DEC-009-2 — Authoritative Backend Business & Authorization Enforcement

**Decision:** Client-side form validation and role checks in React are treated solely as user experience affordances. The backend must enforce all role authorizations, order ownership filters, and price calculations independently.

**Reason:** Automated scanners do not catch subtle business logic flaws (e.g. submitting negative quantities or manipulated coupon codes). Explicit defensive unit/integration tests must prove enforcement.

### DEC-009-3 — Machine-Readable Gating & Redacted Disclosures

**Decision:** Security scripts must generate structured JSON/Markdown reports in `work/13-security-audit/reports/` and exit non-zero on High/Critical actionable findings. Discovered secret findings must be redacted in all console and CI logs.

**Reason:** Prevents sensitive credential leakage in CI build logs while providing unambiguous pass/fail criteria for deployment gates.
