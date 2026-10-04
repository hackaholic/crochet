#!/usr/bin/env python3
"""Prepare and validate an immutable Sulocraft VPS deployment release."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

try:
    import yaml
except ImportError as exc:  # pragma: no cover - exercised by the CLI environment
    raise SystemExit("PyYAML is required. Run `cd backend && uv sync` to install project tools.") from exc


REPO_ROOT = Path(__file__).resolve().parents[1]
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
SUPPORTED_ENVIRONMENTS = ("preprod", "prod")


class ReleaseError(RuntimeError):
    pass


def load_deploy_config(config_path: Path) -> dict:
    if not config_path.is_file():
        raise ReleaseError(
            f"Deployment config not found: {config_path}. Copy deploy/vps-config.example.yaml "
            "to .deploy/vps-config.yaml and fill in the host and SSH settings."
        )
    try:
        config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ReleaseError(f"Cannot read deployment config {config_path}: {exc}") from exc
    if not isinstance(config, dict) or not isinstance(config.get("environments"), dict):
        raise ReleaseError("Deployment config must contain an 'environments' object")
    return config


def resolve_environment(target_env: str, config: dict, *, repo_root: Path = REPO_ROOT) -> dict:
    """Resolve and validate one environment without allowing config fallback."""
    if target_env not in SUPPORTED_ENVIRONMENTS:
        raise ReleaseError("--env must be exactly 'preprod' or 'prod'")
    environments = config.get("environments")
    if not isinstance(environments, dict) or target_env not in environments:
        raise ReleaseError(f"Deployment config has no explicit '{target_env}' environment")
    selected = environments[target_env]
    if not isinstance(selected, dict):
        raise ReleaseError(f"Deployment config entry for '{target_env}' must be an object")
    required = (
        "host",
        "deploy_root",
        "encrypted_secrets_dir",
        "app_env",
        "frontend_url",
        "public_api_url",
        "gateway_network_name",
    )
    missing = [name for name in required if not isinstance(selected.get(name), str) or not selected[name].strip()]
    if missing:
        raise ReleaseError(f"Deployment config for '{target_env}' is missing: {', '.join(missing)}")
    if not selected["deploy_root"].startswith("/"):
        raise ReleaseError(f"Deployment root for '{target_env}' must be an absolute path")
    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_.-]*", selected["gateway_network_name"]):
        raise ReleaseError(f"Invalid gateway network name for '{target_env}'")
    secrets_dir = (repo_root / selected["encrypted_secrets_dir"]).resolve()
    if not secrets_dir.is_dir():
        raise ReleaseError(f"Encrypted secret group for '{target_env}' is missing: {selected['encrypted_secrets_dir']}")
    for group in ("backend.enc.env", "postgres.enc.env"):
        if not (secrets_dir / group).is_file():
            raise ReleaseError(f"Required '{target_env}' encrypted secret group is missing: {selected['encrypted_secrets_dir']}/{group}")
    return {
        **selected,
        "target_env": target_env,
        "compose_project": f"sulocraft-{target_env}",
        "runtime_secrets_dir": f"{str(config.get('runtime_secrets_root', '/run/sulocraft')).rstrip('/')}/{target_env}",
        "encrypted_secrets_dir": str(secrets_dir),
        "ssh_identity_file": str(config.get("ssh_identity_file", "")),
        "ssh_known_hosts_file": str(config.get("ssh_known_hosts_file", "")),
        "compose_file": str(config.get("compose_file", "backend/docker-compose.yml")),
    }


def render_runtime_environment(target: dict, *, image_ref: str, destination: Path) -> Path:
    runtime_dir = target["runtime_secrets_dir"]
    values = {
        "APP_ENV": target["app_env"],
        "TARGET_ENV": target["target_env"],
        "API_IMAGE": image_ref,
        "FRONTEND_URL": target["frontend_url"],
        "PUBLIC_API_URL": target["public_api_url"],
        "GATEWAY_NETWORK_NAME": target.get("gateway_network_name", "sulocraft-gateway"),
        "API_GATEWAY_ALIAS": target.get("api_gateway_alias", f"api-{target['target_env']}"),
        "POSTGRES_DB_FILE": f"{runtime_dir}/postgres/postgres_db",
        "POSTGRES_USER_FILE": f"{runtime_dir}/postgres/postgres_user",
        "POSTGRES_PASSWORD_FILE": f"{runtime_dir}/postgres/postgres_password",
        "DATABASE_URL_FILE": f"{runtime_dir}/backend/database_url",
    }
    for name, value in values.items():
        if "\n" in str(value) or "\r" in str(value):
            raise ReleaseError(f"Invalid newline in non-secret deployment setting: {name}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("".join(f"{name}={value}\n" for name, value in values.items()), encoding="utf-8")
    destination.chmod(0o600)
    return destination


def verify_local_backend(repo_root: Path, target: dict, runtime_env: Path) -> None:
    python = repo_root / "backend" / ".venv" / "bin" / "python"
    python_bin = str(python) if python.is_file() else sys.executable
    compose = shutil.which("docker-compose")
    if not compose:
        raise ReleaseError("docker-compose is required for local target validation")
    # Keep the deployment gate focused on the release, isolation, and secret
    # bootstrap paths. The full application suite remains a CI responsibility;
    # its account integration module currently blocks in local TestClient setup.
    subprocess.run(
        [
            python_bin, "-m", "pytest", "-q",
            "backend/tests/test_vps_release_artifact.py",
            "backend/tests/test_vps_database_isolation.py",
            "backend/tests/test_vault_deploy.py",
        ],
        cwd=repo_root,
        check=True,
    )
    subprocess.run(
        [compose, "-p", target["compose_project"], "--env-file", str(runtime_env), "-f", target["compose_file"], "config", "--quiet"],
        cwd=repo_root,
        check=True,
    )


def deploy_prepared_release(target: dict, release_id: str, image_ref: str, runtime_env: Path) -> None:
    script = REPO_ROOT / "scripts" / "deploy_vps_remote.sh"
    command = [
        "bash", str(script), "--env", target["target_env"], "--host", target["host"],
        "--root", target["deploy_root"], "--release-id", release_id,
        "--runtime-secrets-root", str(Path(target["runtime_secrets_dir"]).parent),
        "--gateway-network", target["gateway_network_name"],
        "--image-ref", image_ref,
    ]
    identity = target.get("ssh_identity_file", "")
    known_hosts = target.get("ssh_known_hosts_file", "")
    if identity:
        command.extend(["--identity", str(Path(identity).expanduser())])
    if known_hosts:
        command.extend(["--known-hosts", str(Path(known_hosts).expanduser())])
    subprocess.run(command, cwd=REPO_ROOT, check=True)


def run(command: list[str], *, cwd: Path = REPO_ROOT) -> str:
    stream_output = command[:2] == ["docker", "build"]
    result = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        capture_output=not stream_output,
    )
    if result.returncode:
        detail = (result.stderr or "").strip() or (result.stdout or "").strip() or f"exit {result.returncode}"
        raise ReleaseError(f"Command failed ({command[0]}): {detail}")
    return (result.stdout or "").strip()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as artifact:
        for block in iter(lambda: artifact.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _source_fingerprint(repo_root: Path, runner: Callable[..., str]) -> tuple[str, bool]:
    status = runner(["git", "status", "--porcelain", "--untracked-files=all"], cwd=repo_root)
    diff = runner(["git", "diff", "HEAD", "--binary"], cwd=repo_root)
    untracked = runner(["git", "ls-files", "--others", "--exclude-standard", "-z"], cwd=repo_root)
    digest = hashlib.sha256()
    digest.update(status.encode("utf-8"))
    digest.update(diff.encode("utf-8"))
    for relative in sorted(filter(None, untracked.split("\0"))):
        path = repo_root / relative
        if path.is_file():
            digest.update(relative.encode("utf-8"))
            digest.update(path.read_bytes())
    return digest.hexdigest(), bool(status)


def _validate_existing_release(release_dir: Path, commit: str, source_fingerprint: str) -> dict:
    manifest_path = release_dir / "manifest.json"
    artifact_path = release_dir / "api-image.tar"
    if not manifest_path.is_file() or not artifact_path.is_file():
        raise ReleaseError(f"Incomplete existing release directory: {release_dir}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if (
        manifest.get("schema_version") != 2
        or manifest.get("commit") != commit
        or manifest.get("source_fingerprint") != source_fingerprint
        or manifest.get("image_ref") != f"sulocraft-api:{commit[:12]}-{source_fingerprint[:12]}"
        or manifest.get("artifact") != artifact_path.name
        or manifest.get("artifact_sha256") != _sha256(artifact_path)
    ):
        raise ReleaseError(f"Existing release artifact failed integrity validation: {release_dir}")
    return manifest


def prepare_release(
    *,
    repo_root: Path,
    verified_commit: str,
    platform: str = "linux/amd64",
    runner: Callable[..., str] = run,
    created_at: str | None = None,
) -> tuple[Path, dict]:
    if not SHA_RE.fullmatch(verified_commit):
        raise ReleaseError("--verified-commit must be the full 40-character Git commit SHA")

    head = runner(["git", "rev-parse", "HEAD"], cwd=repo_root)
    if head != verified_commit:
        raise ReleaseError(f"Verified commit {verified_commit} does not match checked-out HEAD {head}")

    source_fingerprint, dirty_worktree = _source_fingerprint(repo_root, runner)

    release_id = f"{head[:12]}-{source_fingerprint[:12]}"
    release_dir = repo_root / ".deploy" / "releases" / release_id
    if release_dir.exists():
        return release_dir, _validate_existing_release(release_dir, head, source_fingerprint)

    image_ref = f"sulocraft-api:{release_id}"
    runner(
        [
            "docker", "build", "--platform", platform,
            "--label", f"org.opencontainers.image.revision={head}",
            "--label", f"com.sulocraft.source-fingerprint={source_fingerprint}",
            "--label", "org.opencontainers.image.title=Sulocraft API",
            "--file", "backend/Dockerfile", "--tag", image_ref, ".",
        ],
        cwd=repo_root,
    )
    image_id = runner(
        ["docker", "image", "inspect", "--format", "{{.Id}}", image_ref], cwd=repo_root
    )
    if not image_id.startswith("sha256:"):
        raise ReleaseError("Docker returned an invalid image ID; refusing to write a release manifest")

    release_dir.mkdir(parents=True, exist_ok=False)
    artifact_path = release_dir / "api-image.tar"
    temp_artifact: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(prefix="api-image-", suffix=".tar.part", dir=release_dir, delete=False) as tmp:
            temp_artifact = Path(tmp.name)
        runner(["docker", "save", "--output", str(temp_artifact), image_ref], cwd=repo_root)
        if not temp_artifact.is_file() or temp_artifact.stat().st_size == 0:
            raise ReleaseError("Docker produced an empty release archive")
        temp_artifact.replace(artifact_path)
        manifest = {
            "schema_version": 2,
            "commit": head,
            "source_fingerprint": source_fingerprint,
            "dirty_worktree": dirty_worktree,
            "release_id": release_id,
            "image_ref": image_ref,
            "image_id": image_id,
            "platform": platform,
            "artifact": "api-image.tar",
            "artifact_sha256": _sha256(artifact_path),
            "created_at": created_at or datetime.now(timezone.utc).isoformat(),
        }
        manifest_tmp = release_dir / "manifest.json.part"
        manifest_tmp.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        manifest_tmp.replace(release_dir / "manifest.json")
        return release_dir, manifest
    except Exception:
        if temp_artifact and temp_artifact.exists():
            temp_artifact.unlink()
        # Keep no partial release that could be mistaken for a complete artifact.
        for path in release_dir.iterdir():
            path.unlink()
        release_dir.rmdir()
        raise


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="./deploy_vps.sh",
        description="Deploy or promote Sulocraft using an explicit isolated VPS environment.",
    )
    parser.add_argument("--env", required=True, choices=SUPPORTED_ENVIRONMENTS, help="required target environment")
    parser.add_argument("--config", type=Path, default=REPO_ROOT / ".deploy" / "vps-config.yaml", help="non-secret YAML deployment config")
    parser.add_argument("--preflight", action="store_true", help="validate target/config/secrets and print a safe deployment plan")
    parser.add_argument("--verified-commit", help=argparse.SUPPRESS)
    parser.add_argument("--platform", default="linux/amd64", help=argparse.SUPPRESS)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = make_parser().parse_args(argv)
    try:
        config = load_deploy_config(args.config)
        target = resolve_environment(args.env, config)
        if args.preflight:
            print(f"Target: {target['target_env']}")
            print(f"Compose project: {target['compose_project']}")
            print(f"VPS: {target['host']}:{target['deploy_root']}")
            print(f"Runtime secrets: {target['runtime_secrets_dir']}")
            print(f"Encrypted secret groups: {target['encrypted_secrets_dir']}")
            print("Preflight passed. No VPS changes were made.")
            return 0
        if args.verified_commit:
            release_dir, manifest = prepare_release(
                repo_root=REPO_ROOT,
                verified_commit=args.verified_commit,
                platform=args.platform,
            )
            print(f"Release artifact ready: {release_dir}")
            print(f"Commit: {manifest['commit']}")
            print(f"Image: {manifest['image_ref']} ({manifest['image_id']})")
            print(f"Archive SHA-256: {manifest['artifact_sha256']}")
            return 0
        if args.env != "preprod":
            raise ReleaseError("PROD promotion is not enabled until its encrypted secret groups and accepted PREPROD release are present")
        commit = run(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT)
        runtime_env = render_runtime_environment(target, image_ref="pending", destination=REPO_ROOT / ".deploy" / f"runtime-{args.env}.env")
        verify_local_backend(REPO_ROOT, target, runtime_env)
        release_dir, manifest = prepare_release(
            repo_root=REPO_ROOT,
            verified_commit=commit,
            platform=args.platform,
        )
        runtime_env = render_runtime_environment(target, image_ref=manifest["image_ref"], destination=runtime_env)
        deploy_prepared_release(target, manifest["release_id"], manifest["image_ref"], runtime_env)
        print(f"PREPROD deployment complete: {manifest['release_id']}")
        print(f"Image: {manifest['image_ref']}")
        print(f"Archive SHA-256: {manifest['artifact_sha256']}")
        return 0
    except (ReleaseError, OSError, json.JSONDecodeError, subprocess.CalledProcessError) as exc:
        print(f"VPS deployment preflight failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
