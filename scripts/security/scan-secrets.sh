#!/usr/bin/env bash
# =============================================================================
# Sulocraft Security Gate: Secret Scanner (Gitleaks + Redacted Fallback)
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
REPORT_DIR="${REPO_ROOT}/work/work-013-security-audit/reports"
REPORT_FILE="${REPORT_DIR}/secrets-report.json"
mkdir -p "${REPORT_DIR}"

MODE="${1:---working-tree}" # Options: --staged, --working-tree, --history

echo "==> [SECRETS] Initiating secret scan (Mode: ${MODE})..."

# Check if native gitleaks is installed
if command -v gitleaks >/dev/null 2>&1; then
    RUNNER="native"
elif command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
    RUNNER="docker"
else
    RUNNER="python-fallback"
fi

echo "==> [SECRETS] Using scanner runner: ${RUNNER}"

if [ "${RUNNER}" = "native" ]; then
    if [ "${MODE}" = "--staged" ]; then
        CMD=(gitleaks git "${REPO_ROOT}" --staged -c "${REPO_ROOT}/.gitleaks.toml" -r "${REPORT_FILE}" -f json --redact)
    elif [ "${MODE}" = "--history" ]; then
        CMD=(gitleaks git "${REPO_ROOT}" -c "${REPO_ROOT}/.gitleaks.toml" -r "${REPORT_FILE}" -f json --redact)
    else
        CMD=(gitleaks dir "${REPO_ROOT}" -c "${REPO_ROOT}/.gitleaks.toml" -r "${REPORT_FILE}" -f json --redact)
    fi

    if "${CMD[@]}"; then
        echo "==> [SECRETS] PASS: Zero leaked secrets detected by Gitleaks."
        exit 0
    else
        echo "==> [SECRETS] FAIL: Leaked credentials detected by Gitleaks!" >&2
        if [ -f "${REPORT_FILE}" ] && [ -s "${REPORT_FILE}" ]; then
            python3 -c "
import json
try:
    with open('${REPORT_FILE}') as f:
        findings = json.load(f)
    print(f'Total findings: {len(findings)}')
    for f in findings:
        print(f' - Rule: {f.get(\"RuleID\")} | File: {f.get(\"File\")} (Line {f.get(\"StartLine\")})')
except Exception as e:
    print('Failed to parse report:', e)
"
        fi
        exit 1
    fi

elif [ "${RUNNER}" = "docker" ]; then
    if [ "${MODE}" = "--staged" ]; then
        DOCKER_CMD=(docker run --rm -v "${REPO_ROOT}:/path" zricethezav/gitleaks:latest git /path --staged -c /path/.gitleaks.toml -r /path/work/work-013-security-audit/reports/secrets-report.json -f json --redact)
    elif [ "${MODE}" = "--history" ]; then
        DOCKER_CMD=(docker run --rm -v "${REPO_ROOT}:/path" zricethezav/gitleaks:latest git /path -c /path/.gitleaks.toml -r /path/work/work-013-security-audit/reports/secrets-report.json -f json --redact)
    else
        DOCKER_CMD=(docker run --rm -v "${REPO_ROOT}:/path" zricethezav/gitleaks:latest dir /path -c /path/.gitleaks.toml -r /path/work/work-013-security-audit/reports/secrets-report.json -f json --redact)
    fi

    if "${DOCKER_CMD[@]}"; then
        echo "==> [SECRETS] PASS: Zero leaked secrets detected by Gitleaks (Docker)."
        exit 0
    else
        echo "==> [SECRETS] FAIL: Leaked credentials detected by Gitleaks (Docker)!" >&2
        if [ -f "${REPORT_FILE}" ] && [ -s "${REPORT_FILE}" ]; then
            python3 -c "
import json
try:
    with open('${REPORT_FILE}') as f:
        findings = json.load(f)
    print(f'Total findings: {len(findings)}')
    for f in findings:
        print(f' - Rule: {f.get(\"RuleID\")} | File: {f.get(\"File\")} (Line {f.get(\"StartLine\")})')
except Exception as e:
    print('Failed to parse report:', e)
"
        fi
        exit 1
    fi

else
    export REPO_ROOT
    python3 - <<'PY'
import sys, os, re, subprocess

REPO_ROOT = os.environ.get("REPO_ROOT", os.getcwd())
PATTERNS = [
    (r"AGE-SECRET-KEY-1[A-Z0-9]{58}", "Age Private Key"),
    (r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", "Private Key Header"),
    (r"(?:r2_secret_access_key|aws_secret_access_key)\s*[:=]\s*['\"][A-Za-z0-9/+=]{40}['\"]", "Cloudflare R2 / AWS Secret"),
    (r"(?:resend_api_key|fast2sms_api_key)\s*[:=]\s*['\"][A-Za-z0-9_-]{20,}['\"]", "API Secret Key"),
    (r"(?:razorpay_key_secret)\s*[:=]\s*['\"][A-Za-z0-9]{20,}['\"]", "Razorpay Secret Key"),
]

ALLOWLIST_PATHS = [
    ".env.example",
    "backend/.env.example",
    "docs/",
    "work/work-013-security-audit/",
    "backend/tests/",
    ".gitleaks.toml",
]

findings = []

res = subprocess.run(["git", "ls-files"], cwd=REPO_ROOT, capture_output=True, text=True)
files = res.stdout.splitlines()

for rel_path in files:
    if any(rel_path.startswith(allow) or rel_path == allow for allow in ALLOWLIST_PATHS):
        continue
    full_path = os.path.join(REPO_ROOT, rel_path)
    if not os.path.isfile(full_path):
        continue
    try:
        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
            for idx, line in enumerate(f, 1):
                for pat, label in PATTERNS:
                    if re.search(pat, line, re.IGNORECASE):
                        if "dummy_" in line or "test-" in line or "sulocraft_secure_pw" in line:
                            continue
                        findings.append((label, rel_path, idx))
    except Exception:
        pass

if findings:
    print(f"==> [SECRETS] FAIL: {len(findings)} potential secret(s) detected:")
    for label, path, line in findings:
        print(f"  - [{label}] in {path}:{line} (Redacted)")
    sys.exit(1)
else:
    print("==> [SECRETS] PASS: Zero leaked secrets found by fallback scanner.")
    sys.exit(0)
PY
fi
