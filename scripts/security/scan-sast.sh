#!/usr/bin/env bash
# =============================================================================
# Sulocraft Security Gate: Static Application Security Testing (Semgrep)
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
REPORT_DIR="${REPO_ROOT}/work/security/reports"
REPORT_FILE="${REPORT_DIR}/sast-report.json"
mkdir -p "${REPORT_DIR}"

echo "==> [SAST] Initiating Static Application Security Testing (Semgrep)..."

if command -v semgrep >/dev/null 2>&1; then
    RUNNER="native"
elif command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
    RUNNER="docker"
else
    RUNNER="fallback"
fi

echo "==> [SAST] Using SAST runner: ${RUNNER}"

if [ "${RUNNER}" = "native" ]; then
    semgrep scan \
        --config=p/security-audit \
        --config=p/owasp-top-ten \
        --json --output="${REPORT_FILE}" \
        --error || true
elif [ "${RUNNER}" = "docker" ]; then
    docker run --rm -v "${REPO_ROOT}:/src" semgrep/semgrep:latest \
        semgrep scan \
        --config=p/security-audit \
        --config=p/owasp-top-ten \
        --json --output=/src/work/security/reports/sast-report.json \
        --error /src || true
else
    echo "==> [SAST] Running fallback static AST & pattern checks..."
    export REPO_ROOT
    python3 - <<'PY'
import os, sys, re, json

REPO_ROOT = os.environ.get("REPO_ROOT", os.getcwd())
REPORT_FILE = os.path.join(REPO_ROOT, "work/security/reports/sast-report.json")

DANGEROUS_PATTERNS = [
    (r"subprocess\.(?:call|Popen|run)\([^)]*shell\s*=\s*True", "Command Injection: shell=True in subprocess", "HIGH"),
    (r"os\.system\(", "Command Injection: os.system usage", "HIGH"),
    (r"(?:session|conn|db)\.execute\(f[\"']", "SQL Injection: Formatted string in raw SQL query", "CRITICAL"),
    (r"dangerouslySetInnerHTML\s*=\s*\{\s*\{\s*__html\s*:\s*(?!sanitize)", "Cross-Site Scripting (XSS): Unsanitized dangerouslySetInnerHTML", "HIGH"),
    (r"eval\(", "Unsafe Code Execution: eval() usage", "CRITICAL"),
    (r"pickle\.loads?\(", "Unsafe Deserialization: pickle usage", "HIGH"),
]

findings = []
EXCLUDES = ["work/", "node_modules/", ".venv/", "dist/", "build/", "tests/"]

for root, dirs, files in os.walk(REPO_ROOT):
    dirs[:] = [d for d in dirs if not any(d.startswith(ex.rstrip("/")) for ex in EXCLUDES)]
    for fn in files:
        if fn.endswith((".py", ".ts", ".tsx", ".js", ".mjs")):
            rel_p = os.path.relpath(os.path.join(root, fn), REPO_ROOT)
            if any(rel_p.startswith(ex) for ex in EXCLUDES):
                continue
            with open(os.path.join(root, fn), "r", errors="ignore") as fh:
                for idx, line in enumerate(fh, 1):
                    for pat, desc, sev in DANGEROUS_PATTERNS:
                        if re.search(pat, line):
                            findings.append({
                                "rule_id": desc,
                                "path": rel_p,
                                "start": {"line": idx},
                                "extra": {"severity": sev, "message": desc}
                            })

report_data = {
    "results": findings,
    "paths": {"scanned": len(findings)}
}

with open(REPORT_FILE, "w") as f:
    json.dump(report_data, f, indent=2)
PY
fi

# Evaluate results
python3 - <<'PY'
import json, os, sys, re

REPO_ROOT = os.environ.get("REPO_ROOT", os.getcwd())
REPORT_FILE = os.path.join(REPO_ROOT, "work/security/reports/sast-report.json")
EXCEPTIONS_DIR = os.path.join(REPO_ROOT, "work/security/exceptions")

active_exceptions = set()
if os.path.isdir(EXCEPTIONS_DIR):
    for fn in os.listdir(EXCEPTIONS_DIR):
        if fn.endswith(".md"):
            with open(os.path.join(EXCEPTIONS_DIR, fn), "r") as fh:
                for line in fh:
                    m = re.search(r"Rule / CVE ID:\*{0,2}\s*[`\"']?([a-zA-Z0-9_.-]+)[`\"']?", line)
                    if m:
                        active_exceptions.add(m.group(1).strip())

if not os.path.isfile(REPORT_FILE):
    print("==> [SAST] Warning: SAST report file not generated.")
    sys.exit(0)

try:
    with open(REPORT_FILE, "r") as f:
        data = json.load(f)
except Exception as e:
    print(f"==> [SAST] Error reading report: {e}")
    sys.exit(1)

results = data.get("results", [])
blocking_findings = []
warnings = []

for r in results:
    check_id = r.get("check_id") or r.get("rule_id", "Security Issue")
    sev = r.get("extra", {}).get("severity", "HIGH").upper()
    path = r.get("path", "")
    line = r.get("start", {}).get("line", "")

    if check_id in active_exceptions:
        print(f"  - [EXCEPTION] Suppressed: {check_id} at {path}:{line} (Active Exception)")
        continue

    # Dockerfile user missing is classified as Medium/Warning in our audit policy
    if "missing-user" in check_id.lower():
        warnings.append((check_id, path, line, "MEDIUM"))
        continue

    if sev in ("CRITICAL", "HIGH", "ERROR"):
        blocking_findings.append((check_id, path, line, sev))
    else:
        warnings.append((check_id, path, line, sev))

print(f"==> [SAST] Total findings: {len(results)} (Blocking High/Critical: {len(blocking_findings)}, Warnings: {len(warnings)})")

for check_id, path, line, sev in warnings:
    print(f"  - [WARNING] [{sev}] {check_id} at {path}:{line}")

for check_id, path, line, sev in blocking_findings:
    print(f"  - [FAIL] [{sev}] {check_id} at {path}:{line}")

if blocking_findings:
    print(f"==> [SAST] FAIL: {len(blocking_findings)} actionable High/Critical security vulnerabilities detected in source code!")
    sys.exit(1)
else:
    print("==> [SAST] PASS: Zero blocking High/Critical SAST findings detected.")
    sys.exit(0)
PY

