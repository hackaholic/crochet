import os
import shutil
import stat
import subprocess
from pathlib import Path
import pytest


SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
BOOTSTRAP_KEY_SCRIPT = SCRIPTS_DIR / "bootstrap_vps_key.sh"
BOOTSTRAP_SECRETS_SCRIPT = SCRIPTS_DIR / "bootstrap_secrets.sh"
ROTATE_KEY_SCRIPT = SCRIPTS_DIR / "rotate_vps_key.sh"
DEPLOY_SCRIPT = SCRIPTS_DIR / "deploy_vps.sh"


def _has_docker():
    return shutil.which("docker") is not None


def _generate_test_age_key(dest_path: Path) -> str:
    """Generate disposable test age key using alpine ephemeral container."""
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    res = subprocess.run(
        ["docker", "run", "--rm", "alpine", "sh", "-c", "apk add --no-cache age >/dev/null 2>&1 && age-keygen"],
        capture_output=True,
        text=True,
        check=True,
    )
    dest_path.write_text(res.stdout, encoding="utf-8")
    dest_path.chmod(0o600)
    for line in res.stdout.splitlines():
        if "public key:" in line:
            return line.split()[-1]
    raise RuntimeError("Failed to extract public key from generated age output")


def _encrypt_dotenv_sops(plain_content: str, pub_key: str, out_path: Path):
    """Encrypt a dotenv string using SOPS in ephemeral container."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_plain = out_path.parent / f"tmp_{out_path.stem}.plain"
    tmp_plain.write_text(plain_content, encoding="utf-8")
    try:
        w_dir = str(out_path.parent)
        plain_name = tmp_plain.name
        res = subprocess.run(
            [
                "docker", "run", "--rm",
                "-v", f"{w_dir}:/work",
                "-w", "/work",
                "ghcr.io/getsops/sops:v3.9.4-alpine",
                "-e", "--age", pub_key,
                "--input-type", "dotenv",
                "--output-type", "dotenv",
                plain_name,
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        out_path.write_text(res.stdout, encoding="utf-8")
    finally:
        if tmp_plain.exists():
            tmp_plain.unlink()


@pytest.mark.skipif(not _has_docker(), reason="Docker required for ephemeral SOPS/age testing")
def test_bootstrap_vps_key_absent_and_existing(tmp_path):
    """Task 3.6: Verify absent-key creation, strict modes, and refusal on existing key."""
    age_dir = tmp_path / "age"
    env = os.environ.copy()
    env["AGE_KEY_DIR"] = str(age_dir)
    env["AGE_KEY_FILE"] = str(age_dir / "keys.txt")

    # 1. Creation on absent key
    res = subprocess.run(
        ["bash", str(BOOTSTRAP_KEY_SCRIPT)],
        capture_output=True,
        text=True,
        env=env,
    )
    assert res.returncode == 0, f"Failed absent key creation: {res.stderr}"
    assert "VPS age key generated successfully." in res.stdout
    assert "Public recipient: age1" in res.stdout
    assert "AGE-SECRET-KEY" not in res.stdout, "Private key must never be logged"

    # Verify restrictive modes
    dir_mode = stat.S_IMODE(age_dir.stat().st_mode)
    assert dir_mode == 0o700, f"Expected 0700 dir mode, got {oct(dir_mode)}"

    key_file = age_dir / "keys.txt"
    assert key_file.is_file()
    file_mode = stat.S_IMODE(key_file.stat().st_mode)
    assert file_mode == 0o600, f"Expected 0600 file mode, got {oct(file_mode)}"

    # 2. Refusal on existing key (fail-closed)
    res_refusal = subprocess.run(
        ["bash", str(BOOTSTRAP_KEY_SCRIPT)],
        capture_output=True,
        text=True,
        env=env,
    )
    assert res_refusal.returncode != 0
    assert "Refusing to overwrite" in res_refusal.stderr


def test_bootstrap_secrets_missing_age_key(tmp_path):
    """Task 3.3/3.4: Fails closed when age key is missing."""
    empty_enc_dir = tmp_path / "encrypted"
    empty_enc_dir.mkdir()
    env = os.environ.copy()
    env["TARGET_ENV"] = "preprod"
    env["SOPS_AGE_KEY_FILE"] = str(tmp_path / "nonexistent" / "keys.txt")
    env["SECRETS_DIR"] = str(empty_enc_dir)
    env["RUNTIME_SECRETS_DIR"] = str(tmp_path / "run")

    res = subprocess.run(
        ["bash", str(BOOTSTRAP_SECRETS_SCRIPT)],
        capture_output=True,
        text=True,
        env=env,
    )
    assert res.returncode != 0
    assert "Required age private key file" in res.stderr


def test_bootstrap_secrets_missing_required_group(tmp_path):
    """Task 3.3/3.4: Fails closed when required postgres/backend group is missing."""
    key_file = tmp_path / "keys.txt"
    key_file.write_text("# dummy key\n", encoding="utf-8")
    key_file.chmod(0o600)

    empty_enc_dir = tmp_path / "empty_enc"
    empty_enc_dir.mkdir()

    env = os.environ.copy()
    env["TARGET_ENV"] = "preprod"
    env["SOPS_AGE_KEY_FILE"] = str(key_file)
    env["SECRETS_DIR"] = str(empty_enc_dir)
    env["RUNTIME_SECRETS_DIR"] = str(tmp_path / "run")

    res = subprocess.run(
        ["bash", str(BOOTSTRAP_SECRETS_SCRIPT)],
        capture_output=True,
        text=True,
        env=env,
    )
    assert res.returncode != 0
    assert "Missing PostgreSQL encrypted secrets file" in res.stderr


def test_bootstrap_prod_fails_closed_without_prod_secret_groups(tmp_path):
    """A missing PROD group must not fall back to the root PREPROD encrypted set."""
    runtime_root = tmp_path / "runtime"
    env = os.environ.copy()
    env.pop("SECRETS_DIR", None)
    env["RUNTIME_SECRETS_ROOT"] = str(runtime_root)

    res = subprocess.run(
        ["bash", str(BOOTSTRAP_SECRETS_SCRIPT), "--env", "prod"],
        capture_output=True,
        text=True,
        env=env,
    )

    assert res.returncode != 0
    assert "cannot fall back across environments" in res.stderr
    assert not runtime_root.exists()
    assert "POSTGRES_PASSWORD" not in res.stderr


def test_database_secret_target_validator_matches_postgres_group(tmp_path):
    validator = SCRIPTS_DIR / "validate_database_target.py"
    files = {
        "database": tmp_path / "postgres_db",
        "user": tmp_path / "postgres_user",
        "password": tmp_path / "postgres_password",
        "url": tmp_path / "database_url",
    }
    files["database"].write_text("db_one\n", encoding="utf-8")
    files["user"].write_text("user_one\n", encoding="utf-8")
    files["password"].write_text("password_one\n", encoding="utf-8")
    files["url"].write_text(
        "postgresql://user_one:password_one@postgres:5432/db_one\n", encoding="utf-8"
    )

    valid = subprocess.run(
        ["python3", str(validator), *(str(path) for path in files.values())],
        capture_output=True,
        text=True,
    )
    assert valid.returncode == 0, valid.stderr

    files["url"].write_text(
        "postgresql://other_user:other_password@postgres:5432/other_db\n", encoding="utf-8"
    )
    invalid = subprocess.run(
        ["python3", str(validator), *(str(path) for path in files.values())],
        capture_output=True,
        text=True,
    )
    assert invalid.returncode != 0
    assert "do not target the same PostgreSQL database" in invalid.stderr
    assert "other_password" not in invalid.stderr


@pytest.mark.skipif(not _has_docker(), reason="Docker required for ephemeral SOPS/age testing")
def test_bootstrap_secrets_materialization_and_permissions(tmp_path):
    """Task 3.3/3.4: Materializes service secrets with 0700/0600 without disclosing secret values."""
    key_file = tmp_path / "keys.txt"
    pub_key = _generate_test_age_key(key_file)

    enc_dir = tmp_path / "secrets" / "encrypted"
    pg_plain = "POSTGRES_DB=test_db\nPOSTGRES_USER=test_user\nPOSTGRES_PASSWORD=super_secret_pw_999\n"
    backend_plain = "DATABASE_URL=postgresql://test_user:super_secret_pw_999@postgres:5432/test_db\nRESEND_API_KEY=re_dummy_secret_abc\n"

    _encrypt_dotenv_sops(pg_plain, pub_key, enc_dir / "postgres.enc.env")
    _encrypt_dotenv_sops(backend_plain, pub_key, enc_dir / "backend.enc.env")

    run_dir = tmp_path / "run" / "sulocraft"
    env = os.environ.copy()
    env["TARGET_ENV"] = "preprod"
    env["SOPS_AGE_KEY_FILE"] = str(key_file)
    env["SECRETS_DIR"] = str(enc_dir)
    env["RUNTIME_SECRETS_DIR"] = str(run_dir)

    res = subprocess.run(
        ["bash", str(BOOTSTRAP_SECRETS_SCRIPT)],
        capture_output=True,
        text=True,
        env=env,
    )
    assert res.returncode == 0, f"Bootstrap script failed: {res.stderr}"

    # Secret values must NEVER be in stdout or stderr
    assert "super_secret_pw_999" not in res.stdout
    assert "super_secret_pw_999" not in res.stderr
    assert "re_dummy_secret_abc" not in res.stdout
    assert "re_dummy_secret_abc" not in res.stderr

    # Verify restrictive permissions
    root_mode = stat.S_IMODE(run_dir.stat().st_mode)
    assert root_mode == 0o700, f"Expected 0700 for runtime root, got {oct(root_mode)}"

    pg_dir = run_dir / "postgres"
    assert stat.S_IMODE(pg_dir.stat().st_mode) == 0o700

    backend_dir = run_dir / "backend"
    assert stat.S_IMODE(backend_dir.stat().st_mode) == 0o700

    # Verify individual secret files
    pg_pw_file = pg_dir / "postgres_password"
    assert pg_pw_file.is_file()
    assert stat.S_IMODE(pg_pw_file.stat().st_mode) == 0o600
    assert pg_pw_file.read_text(encoding="utf-8") == "super_secret_pw_999"

    db_url_file = backend_dir / "database_url"
    assert db_url_file.is_file()
    assert stat.S_IMODE(db_url_file.stat().st_mode) == 0o600
    assert db_url_file.read_text(encoding="utf-8") == "postgresql://test_user:super_secret_pw_999@postgres:5432/test_db"

    resend_file = backend_dir / "resend_api_key"
    assert resend_file.is_file()
    assert stat.S_IMODE(resend_file.stat().st_mode) == 0o600
    assert resend_file.read_text(encoding="utf-8") == "re_dummy_secret_abc"


@pytest.mark.skipif(not _has_docker(), reason="Docker required for ephemeral SOPS/age testing")
def test_rotate_vps_key_lifecycle(tmp_path):
    """Task 3.7: Candidate key staging, promotion with active backup, and rollback."""
    age_dir = tmp_path / "age"
    env = os.environ.copy()
    env["AGE_KEY_DIR"] = str(age_dir)
    env["ACTIVE_KEY_FILE"] = str(age_dir / "keys.txt")
    env["CANDIDATE_KEY_FILE"] = str(age_dir / "keys.txt.candidate")

    # 1. Bootstrap initial active key
    subprocess.run(["bash", str(BOOTSTRAP_KEY_SCRIPT)], check=True, env=env)
    active_key_before = (age_dir / "keys.txt").read_text(encoding="utf-8")

    # 2. Stage candidate key
    res_gen = subprocess.run(
        ["bash", str(ROTATE_KEY_SCRIPT), "--generate"],
        capture_output=True,
        text=True,
        check=True,
        env=env,
    )
    assert "Candidate key staged" in res_gen.stdout
    candidate_key_file = age_dir / "keys.txt.candidate"
    assert candidate_key_file.is_file()
    assert stat.S_IMODE(candidate_key_file.stat().st_mode) == 0o600
    candidate_content = candidate_key_file.read_text(encoding="utf-8")
    assert candidate_content != active_key_before

    # 3. Promote candidate key
    res_promote = subprocess.run(
        ["bash", str(ROTATE_KEY_SCRIPT), "--promote"],
        capture_output=True,
        text=True,
        check=True,
        env=env,
    )
    assert "Candidate key promoted to active" in res_promote.stdout
    assert not candidate_key_file.exists()

    # Active key must now have candidate content
    active_key_after = (age_dir / "keys.txt").read_text(encoding="utf-8")
    assert active_key_after == candidate_content

    # Backup file must exist with mode 0600 and original content
    backup_files = list(age_dir.glob("keys.txt.backup.*"))
    assert len(backup_files) == 1
    assert stat.S_IMODE(backup_files[0].stat().st_mode) == 0o600
    assert backup_files[0].read_text(encoding="utf-8") == active_key_before

    # 4. Rollback
    res_rollback = subprocess.run(
        ["bash", str(ROTATE_KEY_SCRIPT), "--rollback"],
        capture_output=True,
        text=True,
        check=True,
        env=env,
    )
    assert "Active key restored from backup" in res_rollback.stdout
    assert (age_dir / "keys.txt").read_text(encoding="utf-8") == active_key_before


def test_rotate_key_verification_uses_dotenv_format_in_docker_fallback():
    """SOPS must receive the dotenv format flags for encrypted .enc.env groups."""
    content = ROTATE_KEY_SCRIPT.read_text(encoding="utf-8")
    assert (
        'ghcr.io/getsops/sops:v3.9.4-alpine --input-type dotenv '
        '--output-type dotenv -d "/secrets/${enc_name}" >/dev/null'
    ) in content


def test_deploy_script_excludes_ignored_plaintext_env_files():
    """Task 3.3/3.4: Verify deploy_vps.sh excludes all plaintext .env files and build artifacts from rsync."""
    assert DEPLOY_SCRIPT.is_file()
    content = DEPLOY_SCRIPT.read_text(encoding="utf-8")

    # Exclusions must be present in rsync command
    assert 'DEPLOY_HOST="${DEPLOY_HOST:-root@201.18.212.183}"' in content
    assert "--exclude '.env*'" in content
    assert "--exclude '.git/'" in content
    assert "--exclude 'node_modules/'" in content
    assert "--exclude 'dist/'" in content
    assert "--exclude 'backend/.venv/'" in content

    # Plaintext scp must NOT be present
    assert "scp \"${SSH_OPTIONS[@]}\" \"${DEPLOY_ENV_FILE}\"" not in content

    # bootstrap_secrets.sh must be invoked on the host
    assert "bootstrap_secrets.sh" in content


def test_deploy_backup_uses_mounted_postgres_secrets_and_fails_closed():
    """Backups must use Docker secret files and abort before deployment on backup failure."""
    content = DEPLOY_SCRIPT.read_text(encoding="utf-8")

    assert 'pg_dump -U "$(cat /run/secrets/postgres_user)" "$(cat /run/secrets/postgres_db)"' in content
    assert 'backup_tmp="${backup_file}.tmp.$$"' in content
    assert 'test -s "${backup_tmp}"' in content
    assert "Pre-deploy database backup failed; refusing to deploy." in content
