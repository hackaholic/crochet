"""Regression test for frontend dependency vulnerability audits.

Ensures that pnpm audit has zero high or critical unresolved vulnerabilities,
matching the policy enforced by .github/workflows/security.yml and scan-dependencies.sh.
"""

import json
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_frontend_dependencies_zero_high_or_critical():
    """Verify frontend dependencies contain zero High or Critical vulnerabilities."""
    result = subprocess.run(
        ["bash", "scripts/security/scan-dependencies.sh"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, f"scan-dependencies.sh failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"

    report_path = REPO_ROOT / "work/work-013-security-audit/reports/dependencies-report.json"
    assert report_path.is_file(), f"Expected report file {report_path} was not created"

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report.get("status") == "PASS", f"Security scan status is not PASS: {report}"
    assert report.get("frontend_high_critical") == [], f"Found high/critical frontend vulns: {report.get('frontend_high_critical')}"
    assert report.get("total_blocking") == 0, f"Found blocking vulnerabilities: {report.get('total_blocking')}"
