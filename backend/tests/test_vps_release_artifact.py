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
            },
            "prod": {
                "host": "root@example.invalid",
                "deploy_root": "/opt/sulocraft",
                "encrypted_secrets_dir": "secrets/encrypted/prod",
                "app_env": "production",
                "frontend_url": "https://sulocraft.com",
                "public_api_url": "https://api.sulocraft.com",
                "gateway_network_name": "sulocraft-gateway",
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
            },
            "prod": {
                "host": "root@example.invalid",
                "deploy_root": "/opt/sulocraft",
                "encrypted_secrets_dir": "secrets/encrypted/prod",
                "app_env": "production",
                "frontend_url": "https://sulocraft.com",
                "public_api_url": "https://api.sulocraft.com",
                "gateway_network_name": "sulocraft-gateway",
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

