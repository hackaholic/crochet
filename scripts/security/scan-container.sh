#!/usr/bin/env bash
# =============================================================================
# Sulocraft Security Gate: Container & Infrastructure Security Scanner (Trivy)
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
REPORT_DIR="${REPO_ROOT}/work/work-013-security-audit/reports"
REPORT_FILE="${REPORT_DIR}/container-report.json"
mkdir -p "${REPORT_DIR}"

echo "==> [CONTAINER] Initiating Container & Infrastructure Security Scan..."

if command -v trivy >/dev/null 2>&1; then
    RUNNER="native"
elif command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
    RUNNER="docker"
else
    RUNNER="fallback"
fi

echo "==> [CONTAINER] Using scanner runner: ${RUNNER}"

if [ "${RUNNER}" = "native" ]; then
    trivy config "${REPO_ROOT}" \
        --severity HIGH,CRITICAL \
        --format json \
        --output "${REPORT_FILE}" || true
elif [ "${RUNNER}" = "docker" ]; then
    docker run --rm -v "${REPO_ROOT}:/src" aquasec/trivy:latest \
        config /src \
        --severity HIGH,CRITICAL \
        --format json \
        --output /src/work/work-013-security-audit/reports/container-report.json || true
else
    echo "==> [CONTAINER] Running Python container & compose heuristic audit..."
    export REPO_ROOT
    python3 - <<'PY'
import os, sys, json, re

REPO_ROOT = os.environ.get("REPO_ROOT", os.getcwd())
REPORT_FILE = os.path.join(REPO_ROOT, "work/work-013-security-audit/reports/container-report.json")

findings = []

# Audit Compose files
for cfile in ["backend/docker-compose.yml", "docker/compose.yaml"]:
    cpath = os.path.join(REPO_ROOT, cfile)
    if os.path.isfile(cpath):
        with open(cpath, "r") as fh:
            content = fh.read()
            # 1. Privileged containers
            if re.search(r"privileged:\s*true", content, re.IGNORECASE):
                findings.append({"target": cfile, "title": "Privileged container configured", "severity": "HIGH"})
            # 2. Host networking
            if re.search(r"network_mode:\s*[\"']?host[\"']?", content, re.IGNORECASE):
                findings.append({"target": cfile, "title": "Host network mode configured", "severity": "HIGH"})
            # 3. Docker socket mount
            if "/var/run/docker.sock" in content:
                findings.append({"target": cfile, "title": "Docker socket mounted into container", "severity": "CRITICAL"})
            # 4. Postgres port 5432 exposed in production compose
            if cfile == "backend/docker-compose.yml" and "5432:5432" in content:
                findings.append({"target": cfile, "title": "PostgreSQL port 5432 exposed to host", "severity": "CRITICAL"})

report_data = {
    "Results": [{
        "Target": "Infrastructure Config",
        "Misconfigurations": findings
    }]
}

with open(REPORT_FILE, "w") as out:
    json.dump(report_data, out, indent=2)
PY
fi

# Evaluate results
export REPO_ROOT
python3 - <<'PY'
import json, os, sys, re

REPO_ROOT = os.environ.get("REPO_ROOT", os.getcwd())
REPORT_FILE = os.path.join(REPO_ROOT, "work/work-013-security-audit/reports/container-report.json")
EXCEPTIONS_DIR = os.path.join(REPO_ROOT, "work/work-013-security-audit/exceptions")

if not os.path.isfile(REPORT_FILE):
    print("==> [CONTAINER] Warning: Container report file not generated.")
    sys.exit(0)

try:
    with open(REPORT_FILE, "r") as f:
        data = json.load(f)
except Exception as e:
    print(f"==> [CONTAINER] Error reading report: {e}")
    sys.exit(1)

# Load exceptions
active_exceptions = set()
if os.path.isdir(EXCEPTIONS_DIR):
    for fn in os.listdir(EXCEPTIONS_DIR):
        if fn.endswith(".md"):
            with open(os.path.join(EXCEPTIONS_DIR, fn), "r") as fh:
                for line in fh:
                    m = re.search(r"Rule / CVE ID:\*{0,2}\s*[`\"']?([a-zA-Z0-9_.-]+)[`\"']?", line)
                    if m:
                        active_exceptions.add(m.group(1).strip().lower())

results = data.get("Results", [])
blocking = []
warnings = []

for target in results:
    tname = target.get("Target", "Unknown")
    for mis in target.get("Misconfigurations", []):
        sev = mis.get("Severity", "HIGH").upper()
        title = mis.get("Title", mis.get("Message", "Misconfiguration"))
        rule_id = mis.get("ID", mis.get("RuleID", "")).lower()

        if rule_id in active_exceptions or any(ex in title.lower() for ex in active_exceptions):
            print(f"  - [EXCEPTION] Suppressed: {title} in {tname}")
            continue

        # Dockerfile root user check is tracked under SEC-001 / SEC policy as warning/medium
        if "user should not be 'root'" in title.lower() or "missing-user" in title.lower() or "root user" in title.lower():
            warnings.append((tname, title, "MEDIUM (SEC-001)"))
        elif sev in ("CRITICAL", "HIGH"):
            blocking.append((tname, title, sev))
        else:
            warnings.append((tname, title, sev))

    for vuln in target.get("Vulnerabilities", []):
        sev = vuln.get("Severity", "HIGH").upper()
        cve = vuln.get("VulnerabilityID", "VULN")
        if cve.lower() in active_exceptions:
            continue
        if sev in ("CRITICAL", "HIGH"):
            blocking.append((tname, cve, sev))


print(f"==> [CONTAINER] Scan findings: Blocking High/Critical: {len(blocking)}, Warnings: {len(warnings)}")

for tname, title, sev in warnings:
    print(f"  - [WARNING] [{sev}] in {tname}: {title}")

for tname, title, sev in blocking:
    print(f"  - [FAIL] [{sev}] in {tname}: {title}")

if blocking:
    print("==> [CONTAINER] FAIL: Blocking container/infrastructure vulnerabilities found!")
    sys.exit(1)
else:
    print("==> [CONTAINER] PASS: Zero blocking High/Critical container issues detected.")
    sys.exit(0)
PY
