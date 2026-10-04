#!/usr/bin/env python3
"""Decrypt SOPS encrypted secret groups dynamically into ignored, owner-only local Docker secrets."""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_KEY = Path.home() / ".config" / "sops" / "age" / "keys.txt"
DEFAULT_IMAGE = "ghcr.io/getsops/sops:v3.13.3"
KEY_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

GROUP_KEYS = {
    "postgres": {"POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD"},
    "backend": {
        "DATABASE_URL", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY", "RESEND_API_KEY",
        "GOOGLE_CLIENT_SECRET", "FACEBOOK_APP_SECRET", "FAST2SMS_API_KEY",
        "TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "SMTP_USER", "SMTP_PASSWORD",
        "RAZORPAY_KEY_SECRET", "RAZORPAY_WEBHOOK_SECRET",
    },
}


def fail(message: str) -> "NoReturn":
    print(f"decrypt_secrets: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_env(data: bytes, allowed: set[str], group: str) -> dict[str, str]:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        fail(f"{group} group is not valid UTF-8 dotenv data")
    parsed: dict[str, str] = {}
    for line_number, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        key, separator, value = line.partition("=")
        key = key.strip()
        if not separator or not KEY_RE.fullmatch(key):
            fail(f"invalid dotenv syntax in {group} group at line {line_number}")
        if key not in allowed:
            fail(f"unsupported setting name in {group} group: {key}")
        if key in parsed:
            fail(f"duplicate setting name in {group} group: {key}")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        parsed[key] = value
    return parsed


def decrypt(path: Path, key: Path, image: str) -> bytes:
    if not path.is_file():
        fail(f"encrypted group is missing: {path.name}")
    # Keep the private identity and ciphertext mounts read-only; the decrypting
    # container has no network and cannot persist a writable filesystem.
    command = [
        "docker", "run", "--rm", "--network", "none", "--read-only",
        "--security-opt", "no-new-privileges", "-v", f"{path.resolve()}:/input:ro",
        "-v", f"{key.resolve()}:/keys/age-key:ro", "-e",
        "SOPS_AGE_KEY_FILE=/keys/age-key", image,
        "--input-type", "dotenv", "--output-type", "dotenv", "-d", "/input",
    ]
    try:
        result = subprocess.run(command, capture_output=True, check=False)
    except FileNotFoundError:
        fail("Docker CLI is unavailable; use the pinned SOPS image or install SOPS")
    if result.returncode:
        # Do not relay stderr from the decryption process; it can contain sensitive context.
        fail(f"could not decrypt {path.name}; check the age identity and encrypted input")
    return result.stdout


def write_secret(directory: Path, key: str, value: str) -> None:
    target = directory / key.lower()
    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as output:
        output.write(value)
    os.chmod(target, 0o600)


def local_database_url(values: dict[str, str]) -> str:
    """Point local API at its local Compose database, never at the VPS DB."""
    user = quote(values["POSTGRES_USER"], safe="")
    password = quote(values["POSTGRES_PASSWORD"], safe="")
    database = quote(values["POSTGRES_DB"], safe="")
    return f"postgresql://{user}:{password}@db:5432/{database}"


def resolve_encrypted_dir(env: str, explicit: Path | None) -> Path:
    if explicit:
        if not explicit.is_dir():
            fail(f"specified encrypted directory does not exist: {explicit}")
        return explicit
    candidates = [
        ROOT / "secrets" / env / "encrypted",
        ROOT / "secrets" / "encrypted" / env,
    ]
    for c in candidates:
        if c.is_dir() and (c / "postgres.enc.env").exists():
            return c
    # Only preprod is permitted to fall back to the root secrets/encrypted directory.
    # Production and other environments must have their own explicit encrypted groups (DEC-003-5).
    if env == "preprod" and (ROOT / "secrets" / "encrypted").is_dir() and (ROOT / "secrets" / "encrypted" / "postgres.enc.env").exists():
        return ROOT / "secrets" / "encrypted"
    fail(f"encrypted secrets directory for environment '{env}' not found; cannot fall back across environments")


def load_config_file(config_path: Path) -> dict[str, str]:
    if not config_path.is_file():
        fail(f"specified config file does not exist: {config_path}")
    config: dict[str, str] = {}
    for line in config_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, sep, val = line.partition("=")
        if sep:
            val = val.strip().strip("'\"")
            config[key.strip()] = val
    return config


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=None, help="optional path to deployment/environment config file")
    parser.add_argument(
        "--env",
        choices=["preprod", "dev", "prod"],
        default=None,
        help="target environment (preprod, dev, prod)",
    )
    parser.add_argument("--key", type=Path, default=None, help="age private key path (never copied)")
    parser.add_argument("--encrypted-dir", type=Path, default=None, help="SOPS ciphertext directory")
    parser.add_argument("--output-dir", type=Path, default=None, help="ignored local secret output directory")
    parser.add_argument("--sops-image", default=None, help="pinned SOPS container image")
    parser.add_argument("--clean", action="store_true", help="remove generated local secret files")
    args = parser.parse_args(argv)

    file_config: dict[str, str] = {}
    if args.config:
        file_config = load_config_file(args.config)
    elif os.environ.get("DEPLOY_CONFIG_FILE"):
        file_config = load_config_file(Path(os.environ["DEPLOY_CONFIG_FILE"]))

    # Resolution hierarchy: CLI arg > config file > environment variable > default
    env = (
        args.env
        or file_config.get("TARGET_ENV")
        or file_config.get("SULOCRAFT_ENV")
        or file_config.get("APP_ENV")
        or os.environ.get("SULOCRAFT_ENV")
        or os.environ.get("APP_ENV")
        or "preprod"
    ).lower()

    if env not in {"preprod", "dev", "prod"}:
        fail(f"unsupported target environment: {env}")

    key_path = (
        args.key
        or (Path(file_config["SOPS_AGE_KEY_FILE"]) if "SOPS_AGE_KEY_FILE" in file_config else None)
        or (Path(os.environ["SOPS_AGE_KEY_FILE"]) if "SOPS_AGE_KEY_FILE" in os.environ else None)
        or DEFAULT_KEY
    )
    enc_dir_explicit = (
        args.encrypted_dir
        or (Path(file_config["SECRETS_DIR"]) if "SECRETS_DIR" in file_config else None)
        or (Path(os.environ["SECRETS_DIR"]) if "SECRETS_DIR" in os.environ else None)
    )
    encrypted_dir = resolve_encrypted_dir(env, enc_dir_explicit)

    out_dir_explicit = (
        args.output_dir
        or (Path(file_config["RUNTIME_SECRETS_DIR"]) if "RUNTIME_SECRETS_DIR" in file_config else None)
        or (Path(os.environ["RUNTIME_SECRETS_DIR"]) if "RUNTIME_SECRETS_DIR" in os.environ else None)
    )
    output_dir = out_dir_explicit if out_dir_explicit else (ROOT / "backend" / ".secrets" / env)
    sops_image = (
        args.sops_image
        or file_config.get("SOPS_IMAGE")
        or os.environ.get("SOPS_IMAGE")
        or DEFAULT_IMAGE
    )

    if args.clean:
        if output_dir.exists():
            shutil.rmtree(output_dir)
        print(f"Removed local {env} secret files from {output_dir}.")
        return 0

    key = key_path.expanduser()
    if not key.is_file():
        fail("age identity file is missing")
    mode = key.stat().st_mode & 0o777
    if mode & 0o077:
        fail("age identity permissions must be owner-only (0600 or stricter)")
    if not Path("/var/run/docker.sock").exists():
        fail("Docker daemon is not available")

    output = output_dir.resolve()
    output.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(output.parent, 0o700)
    temp_parent = output.parent
    temp_path = Path(tempfile.mkdtemp(prefix=f".{env}-secrets-", dir=temp_parent))
    os.chmod(temp_path, 0o700)
    try:
        decrypted_groups: dict[str, dict[str, str]] = {}
        for group, allowed in GROUP_KEYS.items():
            enc_file = encrypted_dir / f"{group}.enc.env"
            plaintext = decrypt(enc_file, key, sops_image)
            values = parse_env(plaintext, allowed, group)
            required = {"POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD"} if group == "postgres" else {"DATABASE_URL"}
            if not required.issubset(values) or any(not values[name] for name in required):
                fail(f"required setting is missing or empty in {group} group")
            decrypted_groups[group] = values

        service_dir = temp_path / "postgres"
        service_dir.mkdir(mode=0o700)
        for key_name in ("POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD"):
            write_secret(service_dir, key_name, decrypted_groups["postgres"][key_name])

        service_dir = temp_path / "backend"
        service_dir.mkdir(mode=0o700)
        write_secret(service_dir, "DATABASE_URL", local_database_url(decrypted_groups["postgres"]))
        for key_name in GROUP_KEYS["backend"] - {"DATABASE_URL"}:
            values = decrypted_groups["backend"]
            write_secret(service_dir, key_name, values.get(key_name, ""))

        # Compose interpolation contains filesystem paths only. Secret values are
        # mounted as files and are not placed in the Compose environment.
        compose_env = temp_path / "compose.env"
        env_upper = env.upper()
        compose_env_content = (
            f"SULOCRAFT_BACKEND_DIR={output / 'backend'}\n"
            f"SULOCRAFT_POSTGRES_DIR={output / 'postgres'}\n"
            f"SULOCRAFT_{env_upper}_BACKEND_DIR={output / 'backend'}\n"
            f"SULOCRAFT_{env_upper}_POSTGRES_DIR={output / 'postgres'}\n"
        )
        if env != "preprod":
            # For backward compatibility if preprod overlay is reused
            compose_env_content += (
                f"SULOCRAFT_PREPROD_BACKEND_DIR={output / 'backend'}\n"
                f"SULOCRAFT_PREPROD_POSTGRES_DIR={output / 'postgres'}\n"
            )
        compose_env.write_text(compose_env_content, encoding="utf-8")
        os.chmod(compose_env, 0o600)

        if output.exists():
            shutil.rmtree(output)
        os.replace(temp_path, output)
    except BaseException:
        if temp_path.exists():
            shutil.rmtree(temp_path)
        raise

    print(f"Local {env} secrets are ready in {output} (owner-only permissions).")
    overlay_arg = f"-f docker/compose.{env}.yaml" if (ROOT / "docker" / f"compose.{env}.yaml").exists() else "-f docker/compose.preprod.yaml"
    print(f"Start local services with: docker compose --env-file backend/.secrets/{env}/compose.env -f docker/compose.yaml {overlay_arg} up --build")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
