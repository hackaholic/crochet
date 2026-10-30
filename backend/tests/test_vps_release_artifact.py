import hashlib
import importlib.util
import json
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "deploy_vps.py"
SPEC = importlib.util.spec_from_file_location("deploy_vps_release", SCRIPT_PATH)
release = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(release)


COMMIT = "a" * 40
IMAGE_ID = "sha256:" + "b" * 64


def fake_runner_factory(tmp_path, *, dirty=""):
    calls = []

    def fake_run(command, *, cwd):
        calls.append(command)
        if command[:3] == ["git", "rev-parse", "HEAD"]:
            return COMMIT
        if command[:3] == ["git", "status", "--porcelain"]:
            return dirty
        if command[:4] == ["docker", "image", "inspect", "--format"]:
            return IMAGE_ID
        if command[:2] == ["docker", "save"]:
            Path(command[command.index("--output") + 1]).write_bytes(b"fake immutable docker image archive")
        return ""

    return fake_run, calls


def test_preparation_fingerprints_dirty_tree_before_build(tmp_path):
    runner, calls = fake_runner_factory(tmp_path, dirty=" M backend/app/main.py")

    _, manifest = release.prepare_release(repo_root=tmp_path, verified_commit=COMMIT, runner=runner)

    assert manifest["dirty_worktree"] is True
    assert manifest["source_fingerprint"]
    assert any(command[:2] == ["docker", "build"] for command in calls)


def test_preparation_requires_the_locally_verified_head(tmp_path):
    runner, calls = fake_runner_factory(tmp_path)

    with pytest.raises(release.ReleaseError, match="does not match checked-out HEAD"):
        release.prepare_release(repo_root=tmp_path, verified_commit="c" * 40, runner=runner)

    assert not any(command[:2] == ["docker", "build"] for command in calls)


def test_preparation_writes_commit_image_and_archive_digests(tmp_path):
    runner, calls = fake_runner_factory(tmp_path)

    release_dir, manifest = release.prepare_release(
        repo_root=tmp_path,
        verified_commit=COMMIT,
        runner=runner,
        created_at="2026-10-04T00:00:00+00:00",
    )

    archive = release_dir / "api-image.tar"
    assert archive.is_file()
    assert manifest["commit"] == COMMIT
    assert manifest["image_ref"] == f"sulocraft-api:{COMMIT[:12]}-{manifest['source_fingerprint'][:12]}"
    assert manifest["image_id"] == IMAGE_ID
    assert manifest["artifact_sha256"] == hashlib.sha256(archive.read_bytes()).hexdigest()
    assert (release_dir / "manifest.json").is_file()
    assert any(command[:2] == ["docker", "build"] for command in calls)
    assert any(command[:2] == ["docker", "save"] for command in calls)


def test_existing_release_is_reused_without_rebuilding(tmp_path):
    runner, calls = fake_runner_factory(tmp_path)
    release_dir, first = release.prepare_release(
        repo_root=tmp_path,
        verified_commit=COMMIT,
        runner=runner,
        created_at="2026-10-04T00:00:00+00:00",
    )
    calls.clear()

    reused_dir, second = release.prepare_release(
        repo_root=tmp_path,
        verified_commit=COMMIT,
        runner=runner,
    )

    assert reused_dir == release_dir
    assert second == first
    assert not any(command[:2] == ["docker", "build"] for command in calls)


def test_existing_release_with_modified_archive_fails_integrity_check(tmp_path):
    runner, _ = fake_runner_factory(tmp_path)
    release_dir, _ = release.prepare_release(
        repo_root=tmp_path,
        verified_commit=COMMIT,
        runner=runner,
    )
    (release_dir / "api-image.tar").write_bytes(b"tampered")

    with pytest.raises(release.ReleaseError, match="failed integrity validation"):
        release.prepare_release(repo_root=tmp_path, verified_commit=COMMIT, runner=runner)


def test_build_context_ignores_plaintext_environment_files():
    ignore_rules = (REPO_ROOT / ".dockerignore").read_text(encoding="utf-8")

    assert "**/.env*" in ignore_rules
    assert "**/.secrets/**" in ignore_rules
    assert ".deploy" in ignore_rules


def test_target_resolution_is_explicit_and_environment_scoped(tmp_path):
    secrets = tmp_path / "secrets" / "encrypted"
    secrets.mkdir(parents=True)
    (secrets / "backend.enc.env").write_text("encrypted", encoding="utf-8")
    (secrets / "postgres.enc.env").write_text("encrypted", encoding="utf-8")
    config = {
        "runtime_secrets_root": "/run/sulocraft",
        "environments": {
            "preprod": {
                "host": "root@example.invalid",
                "deploy_root": "/opt/sulocraft",
                "encrypted_secrets_dir": "secrets/encrypted",
                "app_env": "staging",
                "frontend_url": "https://dev.sulocraft.com",
                "public_api_url": "https://api-dev.sulocraft.com",
                "gateway_network_name": "sulocraft-gateway",
                "payment_provider": "cashfree",
                "cashfree_environment": "sandbox",
            },
            "prod": {
                "host": "root@example.invalid",
                "deploy_root": "/opt/sulocraft",
                "encrypted_secrets_dir": "secrets/encrypted/prod",
                "app_env": "production",
                "frontend_url": "https://sulocraft.com",
                "public_api_url": "https://api.sulocraft.com",
                "gateway_network_name": "sulocraft-gateway",
                "payment_provider": "cashfree",
                "cashfree_environment": "production",
            },
        },
    }

    target = release.resolve_environment("preprod", config, repo_root=tmp_path)

    assert target["compose_project"] == "sulocraft-preprod"
    assert target["runtime_secrets_dir"] == "/run/sulocraft/preprod"
    assert target["encrypted_secrets_dir"] == str(secrets.resolve())
    with pytest.raises(release.ReleaseError, match="[Ee]ncrypted secret group.*prod"):
        release.resolve_environment("prod", config, repo_root=tmp_path)


def test_target_resolution_rejects_missing_or_implicit_environment():
    config = {"environments": {"preprod": {}}}
    with pytest.raises(release.ReleaseError, match="exactly 'preprod' or 'prod'"):
        release.resolve_environment("", config)
    with pytest.raises(release.ReleaseError, match="no explicit 'prod' environment"):
        release.resolve_environment("prod", config)


def test_root_cli_requires_environment_flag():
    with pytest.raises(SystemExit) as exc:
        release.make_parser().parse_args([])
    assert exc.value.code == 2


def test_deployment_config_loader_reads_yaml(tmp_path):
    config_path = tmp_path / "deployment.yaml"
    config_path.write_text("runtime_secrets_root: /run/sulocraft\nenvironments: {}\n", encoding="utf-8")

    config = release.load_deploy_config(config_path)

    assert config["runtime_secrets_root"] == "/run/sulocraft"
    assert config["environments"] == {}


def test_prod_promotion_fails_closed_when_prod_secrets_missing(tmp_path):
    secrets = tmp_path / "secrets" / "encrypted"
    secrets.mkdir(parents=True)
    (secrets / "backend.enc.env").write_text("encrypted", encoding="utf-8")
    (secrets / "postgres.enc.env").write_text("encrypted", encoding="utf-8")
    config = {
        "runtime_secrets_root": "/run/sulocraft",
        "environments": {
            "preprod": {
                "host": "root@example.invalid",
                "deploy_root": "/opt/sulocraft",
                "encrypted_secrets_dir": "secrets/encrypted",
                "app_env": "staging",
                "frontend_url": "https://dev.sulocraft.com",
                "public_api_url": "https://api-dev.sulocraft.com",
                "gateway_network_name": "sulocraft-gateway",
                "payment_provider": "cashfree",
                "cashfree_environment": "sandbox",
            },
            "prod": {
                "host": "root@example.invalid",
                "deploy_root": "/opt/sulocraft",
                "encrypted_secrets_dir": "secrets/encrypted/prod",
                "app_env": "production",
                "frontend_url": "https://sulocraft.com",
                "public_api_url": "https://api.sulocraft.com",
                "gateway_network_name": "sulocraft-gateway",
                "payment_provider": "cashfree",
                "cashfree_environment": "production",
            },
        },
    }
    with pytest.raises(release.ReleaseError, match="[Ee]ncrypted secret group.*prod"):
        release.resolve_environment("prod", config, repo_root=tmp_path)


def test_prod_promotion_reuses_exact_same_image_and_manifest(tmp_path):
    # Setup mock release directory
    release_id = "test-release-001"
    release_dir = tmp_path / ".deploy" / "releases" / release_id
    release_dir.mkdir(parents=True)
    artifact_tar = release_dir / "api-image.tar"
    artifact_tar.write_bytes(b"mock immutable tar")
    artifact_sha = hashlib.sha256(artifact_tar.read_bytes()).hexdigest()
    manifest = {
        "schema_version": 2,
        "commit": "a" * 40,
        "source_fingerprint": "b" * 40,
        "release_id": release_id,
        "image_ref": f"sulocraft-api:{release_id}",
        "image_id": "sha256:" + "c" * 64,
        "artifact": "api-image.tar",
        "artifact_sha256": artifact_sha,
    }
    (release_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    # Setup prod secrets
    prod_secrets = tmp_path / "secrets" / "encrypted" / "prod"
    prod_secrets.mkdir(parents=True)
    (prod_secrets / "backend.enc.env").write_text("prod backend enc", encoding="utf-8")
    (prod_secrets / "postgres.enc.env").write_text("prod postgres enc", encoding="utf-8")

    config = {
        "runtime_secrets_root": "/run/sulocraft",
        "environments": {
            "prod": {
                "host": "root@example.invalid",
                "deploy_root": "/opt/sulocraft",
                "encrypted_secrets_dir": "secrets/encrypted/prod",
                "app_env": "production",
                "frontend_url": "https://sulocraft.com",
                "public_api_url": "https://api.sulocraft.com",
                "gateway_network_name": "sulocraft-gateway",
                "api_gateway_alias": "api-prod",
                "payment_provider": "cashfree",
                "cashfree_environment": "production",
            },
        },
    }

    target = release.resolve_environment("prod", config, repo_root=tmp_path)
    runtime_env = release.render_runtime_environment(
        target,
        image_ref=manifest["image_ref"],
        destination=tmp_path / "runtime-prod.env",
    )
    env_content = runtime_env.read_text(encoding="utf-8")
    assert f"API_IMAGE=sulocraft-api:{release_id}" in env_content
    assert "TARGET_ENV=prod" in env_content
    assert "APP_ENV=production" in env_content
    assert "FRONTEND_URL=https://sulocraft.com" in env_content
    assert "PUBLIC_API_URL=https://api.sulocraft.com" in env_content
    assert "PAYMENT_PROVIDER=cashfree" in env_content
    assert "CASHFREE_ENVIRONMENT=production" in env_content
    assert "GOOGLE_CLIENT_ID_FILE=/run/sulocraft/prod/backend/google_client_id" in env_content
    assert "GOOGLE_CLIENT_SECRET_FILE=/run/sulocraft/prod/backend/google_client_secret" in env_content
    assert "CASHFREE_APP_ID_FILE=/run/sulocraft/prod/backend/cashfree_app_id" in env_content
    assert "CASHFREE_SECRET_KEY_FILE=/run/sulocraft/prod/backend/cashfree_secret_key" in env_content


def test_7_2_4_1_tc01_preprod_uses_cashfree_sandbox_explicitly(tmp_path):
    """7.2.4.1-TC01: Preprod config resolves and renders Cashfree sandbox selection and secret file paths."""
    example_cfg = release.load_deploy_config(REPO_ROOT / "deploy" / "vps-config.example.yaml")
    target = release.resolve_environment("preprod", example_cfg, repo_root=REPO_ROOT)

    assert target["payment_provider"] == "cashfree"
    assert target["cashfree_environment"] == "sandbox"
    assert target["runtime_secrets_dir"] == "/run/sulocraft/preprod"

    rendered = release.render_runtime_environment(
        target,
        image_ref="sulocraft-api:preprod-test",
        destination=tmp_path / "runtime-preprod.env",
    )
    text = rendered.read_text(encoding="utf-8")
    assert "PAYMENT_PROVIDER=cashfree\n" in text
    assert "CASHFREE_ENVIRONMENT=sandbox\n" in text
    assert "GOOGLE_CLIENT_ID_FILE=/run/sulocraft/preprod/backend/google_client_id\n" in text
    assert "GOOGLE_CLIENT_SECRET_FILE=/run/sulocraft/preprod/backend/google_client_secret\n" in text
    assert "CASHFREE_APP_ID_FILE=/run/sulocraft/preprod/backend/cashfree_app_id\n" in text
    assert "CASHFREE_SECRET_KEY_FILE=/run/sulocraft/preprod/backend/cashfree_secret_key\n" in text


def test_7_2_4_1_tc03_prod_cannot_inherit_preprod_or_sandbox_settings(tmp_path):
    """7.2.4.1-TC03: Prod fails closed on missing/sandbox/mock settings or preprod secret group."""
    preprod_secrets = tmp_path / "secrets" / "encrypted"
    preprod_secrets.mkdir(parents=True)
    (preprod_secrets / "backend.enc.env").write_text("enc", encoding="utf-8")
    (preprod_secrets / "postgres.enc.env").write_text("enc", encoding="utf-8")

    prod_secrets = tmp_path / "secrets" / "encrypted" / "prod"
    prod_secrets.mkdir(parents=True)
    (prod_secrets / "backend.enc.env").write_text("enc", encoding="utf-8")
    (prod_secrets / "postgres.enc.env").write_text("enc", encoding="utf-8")

    base_prod = {
        "host": "root@example.invalid",
        "deploy_root": "/opt/sulocraft",
        "encrypted_secrets_dir": "secrets/encrypted/prod",
        "app_env": "production",
        "frontend_url": "https://sulocraft.com",
        "public_api_url": "https://api.sulocraft.com",
        "gateway_network_name": "sulocraft-gateway",
        "payment_provider": "cashfree",
        "cashfree_environment": "production",
    }

    # 1. Missing payment_provider fails closed
    cfg_missing_provider = {"environments": {"prod": {**base_prod, "payment_provider": ""}}}
    with pytest.raises(release.ReleaseError, match="missing: payment_provider"):
        release.resolve_environment("prod", cfg_missing_provider, repo_root=tmp_path)

    # 2. Prod cannot select mock provider
    cfg_mock_prod = {"environments": {"prod": {**base_prod, "payment_provider": "mock"}}}
    with pytest.raises(release.ReleaseError, match="cannot use the 'mock' payment provider"):
        release.resolve_environment("prod", cfg_mock_prod, repo_root=tmp_path)

    # 3. Prod cannot select Cashfree sandbox or omit cashfree_environment
    cfg_sandbox_prod = {"environments": {"prod": {**base_prod, "cashfree_environment": "sandbox"}}}
    with pytest.raises(release.ReleaseError, match="explicitly select 'production'"):
        release.resolve_environment("prod", cfg_sandbox_prod, repo_root=tmp_path)

    cfg_missing_cf_env = {"environments": {"prod": {**base_prod, "cashfree_environment": ""}}}
    with pytest.raises(release.ReleaseError, match="missing: cashfree_environment"):
        release.resolve_environment("prod", cfg_missing_cf_env, repo_root=tmp_path)

    # 4. Prod cannot point encrypted_secrets_dir at preprod's secrets/encrypted
    cfg_shared_secrets = {"environments": {"prod": {**base_prod, "encrypted_secrets_dir": "secrets/encrypted"}}}
    with pytest.raises(release.ReleaseError, match="cannot use the preprod encrypted_secrets_dir"):
        release.resolve_environment("prod", cfg_shared_secrets, repo_root=tmp_path)


def test_7_2_4_4_tc01_prod_requires_explicit_live_settings(tmp_path):
    """7.2.4.4-TC01: Resolving prod with missing provider/environment or missing prod secret group fails closed."""
    example_cfg = release.load_deploy_config(REPO_ROOT / "deploy" / "vps-config.example.yaml")
    # Against repo root where secrets/encrypted/prod does not exist yet, prod must fail closed
    if not (REPO_ROOT / "secrets" / "encrypted" / "prod" / "backend.enc.env").is_file():
        with pytest.raises(release.ReleaseError, match="prod"):
            release.resolve_environment("prod", example_cfg, repo_root=REPO_ROOT)


def test_7_2_4_4_tc02_promotion_uses_same_artifact_and_architecture(tmp_path):
    """7.2.4.4-TC02: Preprod and prod render from the exact same artifact/image_ref and share identical Compose architecture."""
    for rel in ("secrets/encrypted", "secrets/encrypted/prod"):
        d = tmp_path / rel
        d.mkdir(parents=True)
        (d / "backend.enc.env").write_text("enc", encoding="utf-8")
        (d / "postgres.enc.env").write_text("enc", encoding="utf-8")

    cfg = release.load_deploy_config(REPO_ROOT / "deploy" / "vps-config.example.yaml")
    preprod_target = release.resolve_environment("preprod", cfg, repo_root=tmp_path)
    prod_target = release.resolve_environment("prod", cfg, repo_root=tmp_path)

    shared_image_ref = "sulocraft-api:20261031T000000Z-abcdef123456"
    preprod_env = release.render_runtime_environment(
        preprod_target, image_ref=shared_image_ref, destination=tmp_path / "preprod.env"
    ).read_text(encoding="utf-8")
    prod_env = release.render_runtime_environment(
        prod_target, image_ref=shared_image_ref, destination=tmp_path / "prod.env"
    ).read_text(encoding="utf-8")

    def parse_env(text: str) -> dict[str, str]:
        return dict(
            line.split("=", 1)
            for line in text.splitlines()
            if line.strip() and not line.startswith("#")
        )

    pre_map = parse_env(preprod_env)
    prod_map = parse_env(prod_env)

    # Identical key schema and immutable image artifact
    assert set(pre_map.keys()) == set(prod_map.keys())
    assert pre_map["API_IMAGE"] == prod_map["API_IMAGE"] == shared_image_ref
    assert pre_map["PAYMENT_PROVIDER"] == prod_map["PAYMENT_PROVIDER"] == "cashfree"
    # Only environment-scoped configuration and secret paths differ
    assert pre_map["CASHFREE_ENVIRONMENT"] == "sandbox"
    assert prod_map["CASHFREE_ENVIRONMENT"] == "production"
    assert pre_map["CASHFREE_APP_ID_FILE"] == "/run/sulocraft/preprod/backend/cashfree_app_id"
    assert prod_map["CASHFREE_APP_ID_FILE"] == "/run/sulocraft/prod/backend/cashfree_app_id"


def test_7_2_4_4_tc03_sandbox_values_cannot_reach_prod(tmp_path):
    """7.2.4.4-TC03: Prod secret-group resolution never reads preprod paths and Cashfree production uses live base URL."""
    for rel in ("secrets/encrypted", "secrets/encrypted/prod"):
        d = tmp_path / rel
        d.mkdir(parents=True)
        (d / "backend.enc.env").write_text("enc", encoding="utf-8")
        (d / "postgres.enc.env").write_text("enc", encoding="utf-8")

    cfg = release.load_deploy_config(REPO_ROOT / "deploy" / "vps-config.example.yaml")
    prod_target = release.resolve_environment("prod", cfg, repo_root=tmp_path)

    assert prod_target["encrypted_secrets_dir"].endswith("secrets/encrypted/prod")
    assert "preprod" not in prod_target["runtime_secrets_dir"]
    assert prod_target["runtime_secrets_dir"] == "/run/sulocraft/prod"

    from app.services.payment.cashfree import CashfreePaymentProvider
    from app.services.payment.base import PaymentGatewayConfigurationError
    from unittest.mock import patch
    from app.core.config import settings

    with patch.object(settings, "cashfree_environment", "production"), \
         patch.object(settings, "cashfree_app_id", "PROD_ID"), \
         patch.object(settings, "cashfree_secret_key", "PROD_SECRET"):
        provider = CashfreePaymentProvider()
        assert provider.environment == "production"
        assert provider._validate_config() == "https://api.cashfree.com/pg"

    with patch.object(settings, "cashfree_environment", "production"), \
         patch.object(settings, "cashfree_app_id", None), \
         patch.object(settings, "cashfree_secret_key", None):
        provider_missing = CashfreePaymentProvider()
        with pytest.raises(PaymentGatewayConfigurationError):
            provider_missing._validate_config()

