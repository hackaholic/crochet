#!/usr/bin/env bash
# =============================================================================
# Sulocraft Security Gate: Secret Architecture & Configuration Audit
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
REPORT_DIR="${REPO_ROOT}/work/security/reports"
REPORT_FILE="${REPORT_DIR}/config-audit.json"
mkdir -p "${REPORT_DIR}"

echo "==> [CONFIG] Auditing secret architecture, Docker compose, and environment configs..."

export REPO_ROOT

python3 - <<'PY'
import sys, os, subprocess, json, re

REPO_ROOT = os.environ.get("REPO_ROOT", os.getcwd())
REPORT_FILE = os.path.join(REPO_ROOT, "work/security/reports/config-audit.json")
os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)

failures = []
warnings = []
checks_passed = 0

# 1. Plaintext production env and secrets check in git tracked files
res = subprocess.run(["git", "ls-files"], cwd=REPO_ROOT, capture_output=True, text=True)
tracked = res.stdout.splitlines()

forbidden_files = [".env", ".env.local", ".env.preprod", "backend/.env", "backend/.env.preprod", "backend/.env.production"]
for f in forbidden_files:
    if f in tracked:
        failures.append(f"Plaintext environment file '{f}' must not be tracked by Git!")

# Check root .env.production if tracked: must only contain public VITE_ vars
if ".env.production" in tracked:
    p_path = os.path.join(REPO_ROOT, ".env.production")
    with open(p_path, "r", errors="ignore") as fh:
        for line in fh:
            line_str = line.strip()
            if line_str and not line_str.startswith("#"):
                if not line_str.startswith("VITE_"):
                    failures.append(f"Non-public variable found in tracked .env.production: {line_str.split('=')[0]}")

# 2. Check age private keys in repo
for t in tracked:
    if "key" in t.lower() and t.endswith(".txt"):
        full_p = os.path.join(REPO_ROOT, t)
        if os.path.isfile(full_p):
            with open(full_p, "r", errors="ignore") as fh:
                if "AGE-SECRET-KEY-" in fh.read():
                    failures.append(f"Age private key discovered in tracked file: {t}")

# 3. Check *.sops.yaml files are actually encrypted
secrets_dir = os.path.join(REPO_ROOT, "secrets")
if os.path.isdir(secrets_dir):
    for f in os.listdir(secrets_dir):
        if f.endswith(".sops.yaml"):
            fp = os.path.join(secrets_dir, f)
            with open(fp, "r", errors="ignore") as fh:
                content = fh.read()
                if "sops:" not in content or "mac: ENC[" not in content:
                    failures.append(f"SOPS secret file '{f}' is not encrypted or lacks valid SOPS metadata!")
                else:
                    checks_passed += 1

# 4. Check PostgreSQL port 5432 is NOT exposed in backend/docker-compose.yml
backend_compose = os.path.join(REPO_ROOT, "backend/docker-compose.yml")
if os.path.isfile(backend_compose):
    with open(backend_compose, "r") as fh:
        compose_text = fh.read()
        # Look for postgres service port exposure
        if re.search(r"postgres:.*?(?:ports:\s*\n\s*-\s*[\"']?5432)", compose_text, re.DOTALL):
            failures.append("PostgreSQL port 5432 is publicly exposed in backend/docker-compose.yml!")
        else:
            checks_passed += 1

        # Check absence of fallback passwords
        if "sulocraft_secure_pw" in compose_text:
            failures.append("Insecure fallback password 'sulocraft_secure_pw' found in backend/docker-compose.yml!")
        else:
            checks_passed += 1

# 5. Check frontend src/ does NOT contain backend secret references
frontend_src = os.path.join(REPO_ROOT, "src")
forbidden_backend_vars = [
    "R2_SECRET_ACCESS_KEY",
    "RESEND_API_KEY",
    "RAZORPAY_KEY_SECRET",
    "GOOGLE_CLIENT_SECRET",
    "FACEBOOK_APP_SECRET",
    "FAST2SMS_API_KEY",
    "TWILIO_AUTH_TOKEN",
    "POSTGRES_PASSWORD",
]

for root, _, files in os.walk(frontend_src):
    for fn in files:
        if fn.endswith((".ts", ".tsx", ".js", ".jsx", ".html")):
            fpath = os.path.join(root, fn)
            with open(fpath, "r", errors="ignore") as fh:
                fc = fh.read()
                for bvar in forbidden_backend_vars:
                    if bvar in fc:
                        failures.append(f"Backend secret '{bvar}' referenced in frontend file: {os.path.relpath(fpath, REPO_ROOT)}")

# 6. Check backup_db.sh does not contain fallback password
backup_script = os.path.join(REPO_ROOT, "backend/scripts/backup_db.sh")
if os.path.isfile(backup_script):
    with open(backup_script, "r") as fh:
        btext = fh.read()
        if "sulocraft_secure_pw" in btext:
            failures.append("Insecure fallback password found in backend/scripts/backup_db.sh!")
        else:
            checks_passed += 1

# Generate report
report_data = {
    "status": "PASS" if not failures else "FAIL",
    "failures": failures,
    "warnings": warnings,
    "checks_passed": checks_passed,
}

with open(REPORT_FILE, "w") as out:
    json.dump(report_data, out, indent=2)

if failures:
    print(f"==> [CONFIG] FAIL: {len(failures)} critical configuration violation(s):")
    for f in failures:
        print(f"  - [FAIL] {f}")
    sys.exit(1)
else:
    print(f"==> [CONFIG] PASS: All {checks_passed} architectural configuration checks passed.")
    sys.exit(0)
PY
