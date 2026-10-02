#!/usr/bin/env bash
# ==============================================================================
# Sulocraft Local Pre-Push Security Gate (Level 1)
# Conforms to Work 009 Task 9.7 and Audit Policy Level 1 requirements.
#
# Fast local checks executed before pushing commits:
# 1. Secret Scanning (Gitleaks)
# 2. Secret Architecture & Config Check
# 3. Static Application Security Testing (Semgrep)
# 4. Dependency Vulnerability Auditing (npm/pnpm audit & pip-audit)
# 5. Core Authorization & Business Logic Security Tests
#
# Usage:
#   ./scripts/security/pre-push.sh
#   ./scripts/security/pre-push.sh --install-hook
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

if [[ "${1:-}" == "--install-hook" ]]; then
    HOOK_PATH="${REPO_ROOT}/.git/hooks/pre-push"
    cat <<'HOOK_EOF' > "${HOOK_PATH}"
#!/usr/bin/env bash
# Sulocraft pre-push git hook
exec ./scripts/security/pre-push.sh
HOOK_EOF
    chmod +x "${HOOK_PATH}"
    echo "✅ Successfully installed pre-push hook at .git/hooks/pre-push"
    exit 0
fi

echo "========================================================"
echo " Sulocraft Local Pre-Push Security Gate (Level 1)       "
echo "========================================================"

FAILED_CHECKS=()

run_check() {
    local name="$1"
    shift
    echo -n "[Level 1] Running ${name}... "
    if "$@" >/dev/null 2>&1; then
        echo "✅ PASS"
    else
        echo "❌ FAIL"
        FAILED_CHECKS+=("${name}")
    fi
}

# 1. Secret scanning
run_check "Secret Scanning" "${SCRIPT_DIR}/scan-secrets.sh"

# 2. Configuration & Secret Architecture audit
run_check "Config & Architecture" "${SCRIPT_DIR}/scan-config.sh"

# 3. Static Application Security Testing (SAST)
run_check "SAST (Semgrep)" "${SCRIPT_DIR}/scan-sast.sh"

# 4. Dependency Vulnerability Audits
run_check "Dependency Audits" "${SCRIPT_DIR}/scan-dependencies.sh"

# 5. Authorization & Business Logic Security Tests
PYTHON_BIN="${REPO_ROOT}/backend/.venv/bin/python"
PYTEST_BIN="${REPO_ROOT}/backend/.venv/bin/pytest"
if [[ -x "${PYTEST_BIN}" ]]; then
    run_check "Security Tests" "${PYTEST_BIN}" \
        "${REPO_ROOT}/backend/tests/test_security_authorization.py" \
        "${REPO_ROOT}/backend/tests/test_security_business_logic.py" \
        "${REPO_ROOT}/backend/tests/test_config_secrets.py" \
        -q
elif command -v pytest >/dev/null 2>&1; then
    run_check "Security Tests" pytest \
        "${REPO_ROOT}/backend/tests/test_security_authorization.py" \
        "${REPO_ROOT}/backend/tests/test_security_business_logic.py" \
        "${REPO_ROOT}/backend/tests/test_config_secrets.py" \
        -q
else
    echo "⚠️ Python pytest not found; skipping security unit test suite locally."
fi

echo "--------------------------------------------------------"
if [ ${#FAILED_CHECKS[@]} -gt 0 ]; then
    echo "❌ PRE-PUSH SECURITY GATE FAILED!"
    echo "The following checks failed:"
    for fc in "${FAILED_CHECKS[@]}"; do
        echo "  - ${fc}"
    done
    echo ""
    echo "Please resolve all security findings before pushing to remote repository."
    exit 1
else
    echo "✅ ALL LEVEL 1 SECURITY CHECKS PASSED. Ready to push."
    exit 0
fi
