import os
import shutil
import subprocess
from pathlib import Path
import yaml
from app.core.config import config_value, migration_database_url


def test_config_value_prefers_file_and_removes_final_newline(tmp_path, monkeypatch):
    secret_file = tmp_path / "resend_api_key"
    secret_file.write_text("secret-value\n", encoding="utf-8")
    monkeypatch.setenv("RESEND_API_KEY", "stale-environment-value")
    monkeypatch.setenv("RESEND_API_KEY_FILE", str(secret_file))

    assert config_value("RESEND_API_KEY") == "secret-value"


def test_config_value_falls_back_to_environment_and_default(monkeypatch):
    monkeypatch.delenv("SULO_TEST_SECRET_FILE", raising=False)
    monkeypatch.setenv("SULO_TEST_SECRET", "local-development-value")
    assert config_value("SULO_TEST_SECRET") == "local-development-value"
    assert config_value("SULO_UNSET_SECRET", "") == ""


def test_config_value_fails_closed_without_disclosing_secret(tmp_path, monkeypatch):
    monkeypatch.setenv("SULO_TEST_SECRET", "must-not-be-used")
    monkeypatch.setenv("SULO_TEST_SECRET_FILE", str(tmp_path / "missing-secret"))

    try:
        config_value("SULO_TEST_SECRET")
    except RuntimeError as exc:
        assert str(exc) == "Unable to read configured secret file for SULO_TEST_SECRET"
        assert "must-not-be-used" not in str(exc)
    else:
        raise AssertionError("A configured but unreadable secret file must fail closed")


def test_migrations_use_database_url_file_over_stale_environment(tmp_path, monkeypatch):
    """Alembic must use file-backed credentials just like the API."""
    secret_file = tmp_path / "database_url"
    secret_file.write_text("postgresql://file_user:file_pass@db:5432/store", encoding="utf-8")
    monkeypatch.setenv("DATABASE_URL", "postgresql://stale:stale@invalid.example/unused")
    monkeypatch.setenv("DATABASE_URL_FILE", str(secret_file))

    assert migration_database_url() == "postgresql+psycopg://file_user:file_pass@db:5432/store"


def test_compose_secret_isolation_and_no_fallback_passwords():
    compose_path = Path(__file__).resolve().parent.parent / "docker-compose.yml"
    assert compose_path.is_file(), f"Expected compose file at {compose_path}"

    with open(compose_path, "r", encoding="utf-8") as f:
        compose_content = f.read()
        compose_data = yaml.safe_load(compose_content)

    # Insecure fallback passwords must not appear anywhere in the compose file
    assert "sulocraft_secure_pw" not in compose_content

    services = compose_data.get("services", {})
    api = services.get("api", {})
    postgres = services.get("postgres", {})

    api_secrets = api.get("secrets", [])
    postgres_secrets = postgres.get("secrets", [])

    # API receives only database_url, not postgres user/password
    assert "database_url" in api_secrets
    assert "postgres_password" not in api_secrets
    assert "postgres_user" not in api_secrets
    assert "postgres_db" not in api_secrets

    # PostgreSQL receives only its own DB credentials, not backend secrets
    assert "postgres_password" in postgres_secrets
    assert "postgres_user" in postgres_secrets
    assert "postgres_db" in postgres_secrets
    assert "database_url" not in postgres_secrets

    # Top-level secrets are defined and map to service-scoped groups
    top_secrets = compose_data.get("secrets", {})
    assert "database_url" in top_secrets
    assert "postgres_password" in top_secrets
    assert "postgres_user" in top_secrets
    assert "postgres_db" in top_secrets

    # Check top-level secret paths stay service-scoped
    assert "/postgres/" in top_secrets["postgres_password"]["file"]
    assert "/backend/" in top_secrets["database_url"]["file"]


def test_compose_config_validation_with_dummy_secrets(tmp_path):
    compose_path = Path(__file__).resolve().parent.parent / "docker-compose.yml"
    docker_compose_bin = shutil.which("docker-compose") or "/usr/local/bin/docker-compose"
    if not Path(docker_compose_bin).is_file():
        return

    # Create dummy secret files
    pg_dir = tmp_path / "postgres"
    backend_dir = tmp_path / "backend"
    pg_dir.mkdir(parents=True)
    backend_dir.mkdir(parents=True)

    db_file = pg_dir / "postgres_db"
    user_file = pg_dir / "postgres_user"
    pw_file = pg_dir / "postgres_password"
    db_url_file = backend_dir / "database_url"

    db_file.write_text("dummy_db\n")
    user_file.write_text("dummy_user\n")
    pw_file.write_text("dummy_pw\n")
    db_url_file.write_text("postgresql://dummy_user:dummy_pw@postgres:5432/dummy_db\n")

    env = os.environ.copy()
    env["POSTGRES_DB_FILE"] = str(db_file)
    env["POSTGRES_USER_FILE"] = str(user_file)
    env["POSTGRES_PASSWORD_FILE"] = str(pw_file)
    env["DATABASE_URL_FILE"] = str(db_url_file)

    res = subprocess.run(
        [docker_compose_bin, "-f", str(compose_path), "config"],
        capture_output=True,
        text=True,
        env=env,
    )
    assert res.returncode == 0, f"docker-compose config failed: {res.stderr}"
    # Verify no fallback password in generated config
    assert "sulocraft_secure_pw" not in res.stdout
    # Verify secrets in parsed output
    resolved = yaml.safe_load(res.stdout)
    api_secrets = [s["source"] for s in resolved["services"]["api"]["secrets"]]
    pg_secrets = [s["source"] for s in resolved["services"]["postgres"]["secrets"]]
    assert api_secrets == ["database_url"]
    assert sorted(pg_secrets) == ["postgres_db", "postgres_password", "postgres_user"]


def test_backup_script_fails_closed_when_password_missing(tmp_path):
    backup_script = Path(__file__).resolve().parent.parent / "scripts" / "backup_db.sh"
    assert backup_script.is_file()

    env = {
        "PATH": os.environ.get("PATH", "/bin:/usr/bin"),
        "BACKUP_DIR": str(tmp_path / "backups"),
    }
    res = subprocess.run(
        ["bash", str(backup_script)],
        capture_output=True,
        text=True,
        env=env,
    )
    assert res.returncode != 0
    assert "Database password must be supplied" in res.stderr
    assert "sulocraft_secure_pw" not in res.stderr
    assert "sulocraft_secure_pw" not in res.stdout


def test_backup_script_fails_closed_on_unreadable_secret_file(tmp_path):
    backup_script = Path(__file__).resolve().parent.parent / "scripts" / "backup_db.sh"

    env = {
        "PATH": os.environ.get("PATH", "/bin:/usr/bin"),
        "BACKUP_DIR": str(tmp_path / "backups"),
        "POSTGRES_PASSWORD_FILE": str(tmp_path / "nonexistent_password"),
    }
    res = subprocess.run(
        ["bash", str(backup_script)],
        capture_output=True,
        text=True,
        env=env,
    )
    assert res.returncode != 0
    assert "Configured secret file for POSTGRES_PASSWORD could not be read" in res.stderr


def test_backup_script_dedicated_r2_credentials_precedence(tmp_path):
    backup_script = Path(__file__).resolve().parent.parent / "scripts" / "backup_db.sh"

    backup_key_file = tmp_path / "backup_key"
    backup_key_file.write_text("dedicated-backup-key\n")

    general_key_file = tmp_path / "general_key"
    general_key_file.write_text("general-key\n")

    test_cmd = f"""
    eval "$(sed -n '/^read_secret()/,/^}}/p' "{backup_script}")"
    val=""
    if k=$(read_secret "BACKUP_R2_ACCESS_KEY_ID"); then
        val="$k"
    elif k=$(read_secret "R2_ACCESS_KEY_ID"); then
        val="$k"
    fi
    echo "$val"
    """

    env = {
        "PATH": os.environ.get("PATH", "/bin:/usr/bin"),
        "BACKUP_R2_ACCESS_KEY_ID_FILE": str(backup_key_file),
        "R2_ACCESS_KEY_ID_FILE": str(general_key_file),
    }

    res = subprocess.run(
        ["bash", "-c", test_cmd],
        capture_output=True,
        text=True,
        env=env,
    )
    assert res.returncode == 0, f"Error: {res.stderr}"
    assert res.stdout.strip() == "dedicated-backup-key"
