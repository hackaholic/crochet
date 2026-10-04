"""Local contract tests for Work 012 database and volume isolation."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
COMPOSE_FILE = REPO_ROOT / "backend" / "docker-compose.yml"
COMPOSE_BIN = shutil.which("docker-compose")


def render_environment(target: str, runtime_dir: str | None = None) -> dict:
    """Render one target using its isolated runtime secret root."""
    secret_root = runtime_dir or f"/run/sulocraft/{target}"
    environment = os.environ.copy()
    for name in (
        "TARGET_ENV",
        "RUNTIME_SECRETS_DIR",
        "POSTGRES_DB_FILE",
        "POSTGRES_USER_FILE",
        "POSTGRES_PASSWORD_FILE",
        "DATABASE_URL_FILE",
    ):
        environment.pop(name, None)
    environment.update(
        {
            "TARGET_ENV": target,
            "APP_ENV": "test",
            "POSTGRES_DB_FILE": f"{secret_root}/postgres/postgres_db",
            "POSTGRES_USER_FILE": f"{secret_root}/postgres/postgres_user",
            "POSTGRES_PASSWORD_FILE": f"{secret_root}/postgres/postgres_password",
            "DATABASE_URL_FILE": f"{secret_root}/backend/database_url",
        }
    )
    if runtime_dir:
        environment["RUNTIME_SECRETS_DIR"] = runtime_dir
    result = subprocess.run(
        [COMPOSE_BIN, "-p", f"sulocraft-{target}", "-f", str(COMPOSE_FILE), "config"],
        cwd=REPO_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=True,
    )
    return yaml.safe_load(result.stdout)


@pytest.mark.skipif(COMPOSE_BIN is None, reason="docker-compose is unavailable")
def test_prod_and_preprod_database_storage_and_secret_paths_are_separate():
    preprod = render_environment("preprod")
    prod = render_environment("prod")

    preprod_volume = preprod["volumes"]["postgres_data"]["name"]
    prod_volume = prod["volumes"]["postgres_data"]["name"]
    assert preprod_volume == "sulocraft-preprod_postgres_data"
    assert prod_volume == "sulocraft-prod_postgres_data"
    assert preprod_volume != prod_volume

    for config in (preprod, prod):
        postgres = config["services"]["postgres"]
        api = config["services"]["api"]
        assert postgres.get("ports", []) == []
        assert [secret["source"] for secret in api["secrets"]] == ["database_url"]
        assert sorted(secret["source"] for secret in postgres["secrets"]) == [
            "postgres_db",
            "postgres_password",
            "postgres_user",
        ]
        assert "database_url" not in {
            secret["source"] for secret in postgres["secrets"]
        }

    preprod_files = {name: item["file"] for name, item in preprod["secrets"].items()}
    prod_files = {name: item["file"] for name, item in prod["secrets"].items()}
    assert set(preprod_files) == set(prod_files)
    assert all(path.startswith("/run/sulocraft/preprod/") for path in preprod_files.values())
    assert all(path.startswith("/run/sulocraft/prod/") for path in prod_files.values())
    assert set(preprod_files.values()).isdisjoint(prod_files.values())


@pytest.mark.skipif(COMPOSE_BIN is None, reason="docker-compose is unavailable")
def test_runtime_secret_root_is_configurable():
    config = render_environment("prod", "/srv/sulocraft/runtime/prod")
    assert config["secrets"]["postgres_db"]["file"] == "/srv/sulocraft/runtime/prod/postgres/postgres_db"
    assert config["secrets"]["database_url"]["file"] == "/srv/sulocraft/runtime/prod/backend/database_url"


def test_vps_deploy_selects_environment_specific_project_and_secret_root():
    deploy_script = (REPO_ROOT / "backend" / "scripts" / "deploy_vps.sh").read_text(encoding="utf-8")
    assert 'RUNTIME_SECRETS_ROOT="${RUNTIME_SECRETS_ROOT:-/run/sulocraft}"' in deploy_script
    assert 'runtime_secrets_dir="${runtime_secrets_root%/}/${target_env}"' in deploy_script
    assert 'compose_cmd=(docker compose -p "sulocraft-${target_env}"' in deploy_script
    for setting in ("POSTGRES_DB_FILE", "POSTGRES_USER_FILE", "POSTGRES_PASSWORD_FILE", "DATABASE_URL_FILE"):
        assert f'export {setting}="${{runtime_secrets_dir}}/' in deploy_script
