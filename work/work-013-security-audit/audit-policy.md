# Sulocraft Security Audit & Release Gate Policy

## 1. Objective

This policy defines the automated security thresholds that every code change and deployment must satisfy before being eligible for merge into integration branches or release to production.

---

## 2. Release Gate Levels

```text
Level 1: Local / Pre-Push Gate (Developer Machine)
Level 2: CI / Pull Request Gate (GitHub Actions)
Level 3: Deployed Development Dynamic Gate (https://dev.sulocraft.com)
```

---

## 3. Severity & Blocking Criteria

| Vulnerability Category | Severity | Action | Release Gate Outcome |
| :--- | :--- | :--- | :--- |
| **Confirmed Secret / Key Leak** | Critical | Immediately Block commit/push/merge | **FAIL** |
| **Known SQL / Command Injection** | Critical | Immediately Block commit/push/merge | **FAIL** |
| **Broken Access Control (IDOR / Admin Bypass)**| Critical | Immediately Block commit/push/merge | **FAIL** |
| **Business Logic Flaw (Price/Qty Tampering)** | Critical | Immediately Block commit/push/merge | **FAIL** |
| **Dependency CVE with Exploit Available** | Critical / High | Block CI merge | **FAIL** |
| **Unsafe Docker Exposure (Exposed DB port, root socket)** | Critical / High | Block deployment | **FAIL** |
| **High SAST Finding (XSS, SSRF, Path Traversal)** | High | Block merge | **FAIL** |
| **Medium SAST / Container Misconfig** | Medium | Warning / Review required | **PASS with Warning** (unless policy escalated) |
| **Low Finding / Informational** | Low | Document in audit report | **PASS** |

---

## 4. Specific Tool Requirements

1. **Gitleaks (Secrets)**:
   - Scans tracked files, staged changes, and commit history.
   - Any unencrypted real secret (API keys, R2 keys, DB passwords, private age keys, JWT secrets) triggers an immediate **FAIL**.
   - Redacted logging only: never print discovered secret values to terminal or CI logs.

2. **Semgrep (SAST)**:
   - Must scan Python backend, TypeScript/JavaScript frontend, Shell scripts, and Dockerfiles.
   - Zero tolerance for SQLi, command injection, path traversal, and unescaped XSS.

3. **npm audit & pip-audit (Dependencies)**:
   - CI fails on unresolved **High** or **Critical** vulnerabilities.
   - Automatic `--force` updates are forbidden to prevent silent breaking changes.

4. **Trivy (Container & Infrastructure)**:
   - Filesystem, Dockerfile, and Compose scans.
   - PostgreSQL port `5432` must NOT be published to host interfaces.
   - No image layers containing production `.env` files.

5. **Authorization & Business Logic Tests**:
   - `test_security_authorization.py` and `test_security_business_logic.py` must achieve 100% pass rate.
   - Any cross-tenant data leak or price tampering vulnerability blocks the release.

6. **OWASP ZAP (DAST)**:
   - Baseline scan against explicit targets (`https://dev.sulocraft.com` and dev API).
   - Never run destructive scans against production.

7. **TLS Audit**:
   - Must enforce TLS 1.2+ with forward secrecy; zero weak ciphers (SSLv3, TLS 1.0/1.1, RC4, 3DES).

---

## 5. Security Exception Workflow

If a vulnerability has no upstream patch or represents an accepted false positive:
1. Document the finding in `work/work-013-security-audit/exceptions/<EXCEPTION_ID>.md`.
2. Must include:
   - Finding title and CVE / Rule ID
   - Affected component
   - Detailed justification explaining why it cannot be exploited in the Sulocraft architecture
   - Temporary mitigation in place
   - Review date and expiration deadline (maximum 60 days)
   - Owner approval signature
3. Documented, active exceptions will not block the release gate until expiration.
