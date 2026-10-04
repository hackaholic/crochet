"""Regression tests for the GitHub Actions preprod deploy command."""

import os
import subprocess
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_preprod_deploy_step_passes_configured_host_and_release_id(tmp_path):
    workflow_path = REPO_ROOT / ".github/workflows/deploy-dev-backend.yml"
    workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))
    step = next(
        step
        for step in workflow["jobs"]["deploy"]["steps"]
        if step.get("name") == "Deploy isolated preprod release"
    )

    deploy_script = tmp_path / "backend/scripts/deploy_vps.sh"
    deploy_script.parent.mkdir(parents=True)
    deploy_script.write_text(
        "#!/usr/bin/env bash\nprintf '%s\\n' \"$DEPLOY_HOST\" \"$RELEASE_ID\" \"$@\"\n",
        encoding="utf-8",
    )
    deploy_script.chmod(0o755)

    env = os.environ.copy()
    env.update(
        VPS_USER="deploy-user",
        VPS_HOST="192.0.2.10",
        RELEASE_ID="0123456789abcdef0123456789abcdef01234567",
    )
    result = subprocess.run(
        ["bash", "-e", "-c", step["run"]],
        cwd=tmp_path,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )

    assert result.stdout.splitlines() == [
        "deploy-user@192.0.2.10",
        "0123456789ab",
        "--env",
        "preprod",
        "--host",
        "deploy-user@192.0.2.10",
    ]
