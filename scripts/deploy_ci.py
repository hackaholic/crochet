#!/usr/bin/env python3
"""Configure the shared VPS command and verify its public endpoint in CI."""

import argparse
import json
import os
from pathlib import Path
import re
import time
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import urlopen

import yaml

from deploy_vps import load_deploy_config, resolve_environment, ReleaseError


def configure(template: Path, destination: Path) -> None:
    host = os.environ.get("VPS_HOST", "")
    user = os.environ.get("VPS_USER", "")
    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9.-]*", host) or not re.fullmatch(r"[a-z_][a-z0-9_-]*", user):
        raise ReleaseError("Missing or invalid VPS_HOST/VPS_USER")
    config = load_deploy_config(template)
    # Retain every environment's explicit routing; SSH is the only CI override.
    for environment in config["environments"].values():
        environment["host"] = f"{user}@{host}"
    config["ssh_identity_file"] = str(Path.home() / ".ssh/id_ed25519")
    config["ssh_known_hosts_file"] = str(Path.home() / ".ssh/known_hosts")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(yaml.safe_dump(config), encoding="utf-8")
    destination.chmod(0o600)


def verify_health(config_path: Path, environment: str, *, attempts: int = 15,
                  interval: float = 4, opener=urlopen, sleeper=time.sleep) -> None:
    target = resolve_environment(environment, load_deploy_config(config_path))
    base = target["public_api_url"]
    url = urlsplit(base)
    if url.scheme != "https" or not url.hostname or url.username or url.password or url.query or url.fragment:
        raise ReleaseError("Public API URL must be an HTTPS URL without credentials/query/fragment")
    if attempts < 1 or interval < 0:
        raise ReleaseError("Invalid health retry configuration")
    for attempt in range(attempts):
        try:
            with opener(base.rstrip("/") + "/health", timeout=12) as response:
                body = json.loads(response.read(65536))
                if response.status == 200 and isinstance(body, dict) and body.get("status") == "ok":
                    print("Public API health verification passed.")
                    return
        except (URLError, OSError, ValueError):
            pass
        if attempt + 1 < attempts:
            sleeper(interval)
    raise ReleaseError("Public API health verification failed; deployment is not accepted")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("configure", "health"))
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--template", type=Path, default=Path("deploy/vps-config.example.yaml"))
    parser.add_argument("--env", choices=("preprod", "prod"), required=True)
    args = parser.parse_args()
    try:
        if args.action == "configure":
            configure(args.template, args.config)
        else:
            verify_health(args.config, args.env)
    except ReleaseError as exc:
        print(str(exc))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
