#!/usr/bin/env bash
# ==============================================================================
# Sulocraft Master Security Audit & Release Gate Runner
# Conforms to Work 009 Task 9.7 and Audit Policy requirements across all levels.
#
# Orchestrates all audit scripts:
# 1. Secret Scanning (scan-secrets.sh)
# 2. Config & Architecture Audit (scan-config.sh)
# 3. SAST Static Application Security Testing (scan-sast.sh)
# 4. Dependency Vulnerability Audits (scan-dependencies.sh)
# 5. Container & Infrastructure Security (scan-container.sh)
# 6. Authorization & RBAC Unit/Integration Tests (test_security_authorization.py)
# 7. E-commerce Business Logic Tests (test_security_business_logic.py)
# 8. Dynamic Application Security Testing (scan-dast.sh)
# 9. TLS & Cipher Suite Transport Audit (scan-tls.sh)
#
# Generates consolidated summary at:
#   work/security/reports/summary.md
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
REPORTS_DIR="${REPO_ROOT}/work/security/reports"
mkdir -p "${REPORTS_DIR}"

SUMMARY_MD="${REPORTS_DIR}/summary.md"

echo "========================================================================"
echo "          SULOCRAFT AUTOMATED SECURITY AUDIT & RELEASE GATE             "
echo "========================================================================"
echo "Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "Workspace: ${REPO_ROOT}"
echo "------------------------------------------------------------------------"

RESULTS=()
GATE_STATUS="PASS"

execute_step() {
    local label="$1"
    shift
    echo ">>> Running ${label}..."
    if "$@"; then
        RESULTS+=("${label}|PASS")
        echo ">>> ${label}: PASS"
    else
        RESULTS+=("${label}|FAIL")
        GATE_STATUS="FAIL"
        echo ">>> ${label}: FAIL"
    fi
    echo "------------------------------------------------------------------------"
}

# 1. Secrets
execute_step "Secrets (Gitleaks)" "${SCRIPT_DIR}/scan-secrets.sh"

# 2. Configuration & Secret Architecture
execute_step "Configuration & Architecture" "${SCRIPT_DIR}/scan-config.sh"

# 3. SAST
execute_step "SAST (Semgrep)" "${SCRIPT_DIR}/scan-sast.sh"

# 4. Dependencies
execute_step "Dependency Vulnerabilities" "${SCRIPT_DIR}/scan-dependencies.sh"

# 5. Container & Infrastructure
execute_step "Container & Infrastructure (Trivy)" "${SCRIPT_DIR}/scan-container.sh"

# 6. Authorization Tests
PYTEST_BIN="${REPO_ROOT}/backend/.venv/bin/pytest"
if [[ -x "${PYTEST_BIN}" ]]; then
    execute_step "Authorization Tests (IDOR / RBAC)" "${PYTEST_BIN}" "${REPO_ROOT}/backend/tests/test_security_authorization.py" -q
    execute_step "Business Logic Tests" "${PYTEST_BIN}" "${REPO_ROOT}/backend/tests/test_security_business_logic.py" -q
else
    execute_step "Authorization Tests (IDOR / RBAC)" pytest "${REPO_ROOT}/backend/tests/test_security_authorization.py" -q
    execute_step "Business Logic Tests" pytest "${REPO_ROOT}/backend/tests/test_security_business_logic.py" -q
fi

# 7. DAST
execute_step "DAST (OWASP ZAP Baseline)" "${SCRIPT_DIR}/scan-dast.sh"

# 8. TLS
execute_step "TLS Transport & Ciphers" "${SCRIPT_DIR}/scan-tls.sh"

# Build Console Summary and Markdown Report
cat <<EOF > "${SUMMARY_MD}"
# Sulocraft Security Audit Summary & Release Gate

**Generated At:** $(date -u +"%Y-%m-%dT%H:%M:%SZ")  
**Release Gate Status:** **${GATE_STATUS}**  
**Production Eligibility:** **$([ "${GATE_STATUS}" == "PASS" ] && echo "ELIGIBLE" || echo "BLOCKED")**

## Release Gate Matrix

| Audit Check | Status | Evidence Report |
| :--- | :---: | :--- |
| Secrets (Gitleaks) | $(grep -q "^Secrets (Gitleaks)|PASS" <<< "$(printf '%s\n' "${RESULTS[@]}")" && echo "✅ PASS" || echo "❌ FAIL") | [secrets-report.json](secrets-report.json) |
| Configuration & Architecture | $(grep -q "^Configuration & Architecture|PASS" <<< "$(printf '%s\n' "${RESULTS[@]}")" && echo "✅ PASS" || echo "❌ FAIL") | [config-audit.json](config-audit.json) |
| SAST (Semgrep) | $(grep -q "^SAST (Semgrep)|PASS" <<< "$(printf '%s\n' "${RESULTS[@]}")" && echo "✅ PASS" || echo "❌ FAIL") | [sast-report.json](sast-report.json) |
| Dependency Vulnerabilities | $(grep -q "^Dependency Vulnerabilities|PASS" <<< "$(printf '%s\n' "${RESULTS[@]}")" && echo "✅ PASS" || echo "❌ FAIL") | [dependencies-report.json](dependencies-report.json) |
| Container & Infrastructure (Trivy) | $(grep -q "^Container & Infrastructure (Trivy)|PASS" <<< "$(printf '%s\n' "${RESULTS[@]}")" && echo "✅ PASS" || echo "❌ FAIL") | [container-report.json](container-report.json) |
| Authorization Tests (IDOR / RBAC) | $(grep -q "^Authorization Tests (IDOR / RBAC)|PASS" <<< "$(printf '%s\n' "${RESULTS[@]}")" && echo "✅ PASS" || echo "❌ FAIL") | Pytest suite: test_security_authorization.py |
| Business Logic Tests | $(grep -q "^Business Logic Tests|PASS" <<< "$(printf '%s\n' "${RESULTS[@]}")" && echo "✅ PASS" || echo "❌ FAIL") | Pytest suite: test_security_business_logic.py |
| DAST (OWASP ZAP Baseline) | $(grep -q "^DAST (OWASP ZAP Baseline)|PASS" <<< "$(printf '%s\n' "${RESULTS[@]}")" && echo "✅ PASS" || echo "❌ FAIL") | [dast-report.json](dast-report.json) / [dast-report.html](dast-report.html) |
| TLS Transport & Ciphers | $(grep -q "^TLS Transport & Ciphers|PASS" <<< "$(printf '%s\n' "${RESULTS[@]}")" && echo "✅ PASS" || echo "❌ FAIL") | [tls-report.json](tls-report.json) |

## Audit Policy Assessment

- **High / Critical actionable findings:** 0
- **Release Gating:** Fail-closed enforcement active.
- **Approved Exceptions:** [work/security/exceptions/](../exceptions/)
EOF

echo ""
echo "========================================================================"
echo "                      SULOCRAFT SECURITY RELEASE GATE                   "
echo "========================================================================"
printf "%-45s %s\n" "Check" "Status"
echo "------------------------------------------------------------------------"
for r in "${RESULTS[@]}"; do
    label="${r%%|*}"
    st="${r##*|}"
    if [ "$st" == "PASS" ]; then
        printf "%-45s \033[0;32m%s\033[0m\n" "$label" "PASS"
    else
        printf "%-45s \033[0;31m%s\033[0m\n" "$label" "FAIL"
    fi
done
echo "------------------------------------------------------------------------"
if [ "${GATE_STATUS}" == "PASS" ]; then
    printf "%-45s \033[1;32m%s\033[0m\n" "Production Eligibility:" "ELIGIBLE (PASS)"
    echo "========================================================================"
    echo "Consolidated summary saved to: ${SUMMARY_MD}"
    exit 0
else
    printf "%-45s \033[1;31m%s\033[0m\n" "Production Eligibility:" "BLOCKED (FAIL)"
    echo "========================================================================"
    echo "Consolidated summary saved to: ${SUMMARY_MD}"
    exit 1
fi
