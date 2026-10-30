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


def test_config_value_environment_and_file_sources_resolve_identically(tmp_path, monkeypatch):
    """Local env config and SOPS-rendered file config share one setting contract."""
    setting_name = "SULO_PARITY_TEST_VALUE"
    expected_value = "public-client-id-for-test"
    value_file = tmp_path / "sops-rendered-value"
    value_file.write_text(f"{expected_value}\n", encoding="utf-8")

    monkeypatch.delenv(f"{setting_name}_FILE", raising=False)
    monkeypatch.setenv(setting_name, expected_value)
    local_value = config_value(setting_name)

    monkeypatch.setenv(f"{setting_name}_FILE", str(value_file))
    file_backed_value = config_value(setting_name)

    assert local_value == file_backed_value == expected_value


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

    # API receives backend credentials, not PostgreSQL service credentials.
    assert "database_url" in api_secrets
    assert "google_client_id" in api_secrets
    assert "google_client_secret" in api_secrets
    assert "cashfree_app_id" in api_secrets
    assert "cashfree_secret_key" in api_secrets
    assert "postgres_password" not in api_secrets
    assert "postgres_user" not in api_secrets
    assert "postgres_db" not in api_secrets

    # PostgreSQL receives only its own DB credentials, not backend secrets
    assert "postgres_password" in postgres_secrets
    assert "postgres_user" in postgres_secrets
    assert "postgres_db" in postgres_secrets
    assert "database_url" not in postgres_secrets
    assert "cashfree_app_id" not in postgres_secrets
    assert "cashfree_secret_key" not in postgres_secrets
    assert "google_client_id" not in postgres_secrets
    assert "google_client_secret" not in postgres_secrets

    # Top-level secrets are defined and map to service-scoped groups
    top_secrets = compose_data.get("secrets", {})
    assert "database_url" in top_secrets
    assert "google_client_id" in top_secrets
    assert "google_client_secret" in top_secrets
    assert "cashfree_app_id" in top_secrets
    assert "cashfree_secret_key" in top_secrets
    assert "postgres_password" in top_secrets
    assert "postgres_user" in top_secrets
    assert "postgres_db" in top_secrets

    # Secret source paths must be explicitly supplied by the selected environment.
    assert top_secrets["postgres_password"]["file"] == (
        "${POSTGRES_PASSWORD_FILE:?Set POSTGRES_PASSWORD_FILE to this target's database secret path}"
    )
    assert top_secrets["database_url"]["file"] == (
        "${DATABASE_URL_FILE:?Set DATABASE_URL_FILE to this target's API database URL secret path}"
    )
    assert top_secrets["google_client_id"]["file"] == (
        "${GOOGLE_CLIENT_ID_FILE:?Set GOOGLE_CLIENT_ID_FILE to this target's Google client ID secret path}"
    )
    assert top_secrets["google_client_secret"]["file"] == (
        "${GOOGLE_CLIENT_SECRET_FILE:?Set GOOGLE_CLIENT_SECRET_FILE to this target's Google client secret path}"
    )
    assert top_secrets["cashfree_app_id"]["file"] == (
        "${CASHFREE_APP_ID_FILE:?Set CASHFREE_APP_ID_FILE to this target's Cashfree App ID secret path}"
    )
    assert top_secrets["cashfree_secret_key"]["file"] == (
        "${CASHFREE_SECRET_KEY_FILE:?Set CASHFREE_SECRET_KEY_FILE to this target's Cashfree Secret Key secret path}"
    )


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
    cf_app_file = backend_dir / "cashfree_app_id"
    cf_sec_file = backend_dir / "cashfree_secret_key"
    google_id_file = backend_dir / "google_client_id"
    google_secret_file = backend_dir / "google_client_secret"

    db_file.write_text("dummy_db\n")
    user_file.write_text("dummy_user\n")
    pw_file.write_text("dummy_pw\n")
    db_url_file.write_text("postgresql://dummy_user:dummy_pw@postgres:5432/dummy_db\n")
    cf_app_file.write_text("dummy_cf_app_id\n")
    cf_sec_file.write_text("dummy_cf_secret_key\n")
    google_id_file.write_text("dummy_google_client_id\n")
    google_secret_file.write_text("dummy_google_client_secret\n")

    env = os.environ.copy()
    env["POSTGRES_DB_FILE"] = str(db_file)
    env["POSTGRES_USER_FILE"] = str(user_file)
    env["POSTGRES_PASSWORD_FILE"] = str(pw_file)
    env["DATABASE_URL_FILE"] = str(db_url_file)
    env["CASHFREE_APP_ID_FILE"] = str(cf_app_file)
    env["CASHFREE_SECRET_KEY_FILE"] = str(cf_sec_file)
    env["GOOGLE_CLIENT_ID_FILE"] = str(google_id_file)
    env["GOOGLE_CLIENT_SECRET_FILE"] = str(google_secret_file)

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
    api_secrets = sorted(s["source"] for s in resolved["services"]["api"]["secrets"])
    pg_secrets = sorted(s["source"] for s in resolved["services"]["postgres"]["secrets"])
    assert api_secrets == ["cashfree_app_id", "cashfree_secret_key", "database_url", "google_client_id", "google_client_secret"]
    assert pg_secrets == ["postgres_db", "postgres_password", "postgres_user"]


def test_7_2_4_1_tc02_local_compose_stays_on_mock_and_excludes_secrets():
    """7.2.4.1-TC02 & TC04: Local docker/compose.yaml stays on mock provider and never exposes Cashfree secrets to frontend."""
    local_compose_path = Path(__file__).resolve().parents[2] / "docker" / "compose.yaml"
    assert local_compose_path.is_file()
    local_data = yaml.safe_load(local_compose_path.read_text(encoding="utf-8"))
    api_env = local_data["services"]["api"]["environment"]
    frontend_env = local_data["services"]["frontend"]["environment"]

    assert api_env["PAYMENT_PROVIDER"] == "mock"
    assert "CASHFREE_APP_ID" not in frontend_env
    assert "CASHFREE_SECRET_KEY" not in frontend_env
    assert "CASHFREE_APP_ID_FILE" not in frontend_env
    assert "CASHFREE_SECRET_KEY_FILE" not in frontend_env


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
