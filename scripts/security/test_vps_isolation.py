"""Automated tests for Work 012 VPS PROD/PREPROD Container & Network Isolation."""

import os
import shutil
import subprocess
from pathlib import Path
import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
COMPOSE_APP = REPO_ROOT / "backend" / "docker-compose.yml"
COMPOSE_PROXY = REPO_ROOT / "docker" / "compose.proxy.yaml"
CADDYFILE = REPO_ROOT / "docker" / "Caddyfile"


def get_rendered_compose(project_name: str, target_env: str) -> dict:
    """Render Compose specification with project and target_env parameters."""
    env = os.environ.copy()
    env["TARGET_ENV"] = target_env
    env["POSTGRES_DB_FILE"] = f"/run/sulocraft/{target_env}/postgres/postgres_db"
    env["POSTGRES_USER_FILE"] = f"/run/sulocraft/{target_env}/postgres/postgres_user"
    env["POSTGRES_PASSWORD_FILE"] = f"/run/sulocraft/{target_env}/postgres/postgres_password"
    env["DATABASE_URL_FILE"] = f"/run/sulocraft/{target_env}/backend/database_url"
    cmd = [
        "docker-compose",
        "-p", project_name,
        "-f", str(COMPOSE_APP),
        "config"
    ]
    res = subprocess.run(cmd, cwd=str(REPO_ROOT), env=env, capture_output=True, text=True, check=True)
    return yaml.safe_load(res.stdout)


def test_proxy_compose_syntax_and_ports():
    """Verify standalone reverse proxy Compose defines ports 80 and 443 on the gateway network."""
    cmd = [
        "docker-compose",
        "-p", "sulocraft-gateway",
        "-f", str(COMPOSE_PROXY),
        "config"
    ]
    res = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True, check=True)
    config = yaml.safe_load(res.stdout)

    assert "services" in config
    assert "reverse-proxy" in config["services"]
    proxy = config["services"]["reverse-proxy"]

    # Verify ports 80 and 443 are mapped
    published_ports = {str(p["published"]) for p in proxy.get("ports", [])}
    assert "80" in published_ports
    assert "443" in published_ports

    # Verify gateway network
    assert "networks" in config
    assert "sulocraft-gateway" in config["networks"]


def test_app_compose_preprod_prod_syntax():
    """Verify backend Compose renders cleanly for both preprod and prod without syntax errors."""
    preprod = get_rendered_compose("sulocraft-preprod", "preprod")
    prod = get_rendered_compose("sulocraft-prod", "prod")

    assert preprod["name"] == "sulocraft-preprod"
    assert prod["name"] == "sulocraft-prod"


def test_no_hardcoded_container_names():
    """Ensure no static container_name is defined to allow Compose namespacing (DEC-012-005)."""
    for env in ("preprod", "prod"):
        config = get_rendered_compose(f"sulocraft-{env}", env)
        for svc_name, svc in config.get("services", {}).items():
            assert "container_name" not in svc, f"Service '{svc_name}' in {env} has hardcoded container_name!"


def test_no_public_host_ports_on_app_services():
    """Ensure per-environment API and PostgreSQL stacks NEVER bind host ports."""
    for env in ("preprod", "prod"):
        config = get_rendered_compose(f"sulocraft-{env}", env)
        for svc_name, svc in config.get("services", {}).items():
            ports = svc.get("ports", [])
            assert not ports, f"Service '{svc_name}' in {env} exposes host ports: {ports}"


def test_postgres_isolated_from_gateway_network():
    """Ensure PostgreSQL is attached ONLY to the private internal network, never the gateway."""
    for env in ("preprod", "prod"):
        config = get_rendered_compose(f"sulocraft-{env}", env)
        pg = config["services"]["postgres"]
        networks = pg.get("networks", {})
        assert "internal" in networks, f"PostgreSQL in {env} missing internal network"
        assert "gateway" not in networks, f"Security Violation: PostgreSQL in {env} attached to gateway network!"
        assert "sulocraft-gateway" not in networks, f"Security Violation: PostgreSQL in {env} attached to gateway network!"


def test_api_gateway_alias_namespacing():
    """Ensure API has environment-scoped network alias on the gateway network for reverse proxy routing."""
    preprod = get_rendered_compose("sulocraft-preprod", "preprod")
    preprod_aliases = preprod["services"]["api"]["networks"]["gateway"]["aliases"]
    assert "api-preprod" in preprod_aliases

    prod = get_rendered_compose("sulocraft-prod", "prod")
    prod_aliases = prod["services"]["api"]["networks"]["gateway"]["aliases"]
    assert "api-prod" in prod_aliases


def test_named_volumes_namespaced():
    """Ensure persistent database named volumes are distinct and do not collide."""
    preprod = get_rendered_compose("sulocraft-preprod", "preprod")
    prod = get_rendered_compose("sulocraft-prod", "prod")

    preprod_vol = preprod["volumes"]["postgres_data"]["name"]
    prod_vol = prod["volumes"]["postgres_data"]["name"]

    assert preprod_vol != prod_vol
    assert "preprod" in preprod_vol
    assert "prod" in prod_vol


def test_caddyfile_routing_configuration():
    """Ensure Caddyfile routes to the correct isolated backend aliases."""
    content = CADDYFILE.read_text(encoding="utf-8")
    assert "api.sulocraft.com" in content
    assert "api-dev.sulocraft.com" in content
    assert "api-prod:8000" in content
    assert "api-preprod:8000" in content


def test_caddyfile_validation_with_caddy_cli():
    """Run caddy validate in container to verify formal Caddyfile grammar and token validity."""
    if not shutil.which("docker"):
        pytest.skip("Docker CLI not available")

    cmd = [
        "docker", "run", "--rm",
        "-v", f"{CADDYFILE}:/etc/caddy/Caddyfile:ro",
        "-e", "PROD_API_DOMAIN=api.sulocraft.com",
        "-e", "PREPROD_API_DOMAIN=api-dev.sulocraft.com",
        "caddy:2-alpine",
        "caddy", "validate", "--config", "/etc/caddy/Caddyfile"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, f"Caddyfile validation failed:\n{res.stderr}\n{res.stdout}"
    assert "Valid configuration" in res.stdout or "Valid configuration" in res.stderr


def test_caddyfile_security_headers_and_db_unreachable():
    """Ensure Caddyfile injects security headers and has zero routes to postgres."""
    content = CADDYFILE.read_text(encoding="utf-8")
    assert "X-Content-Type-Options nosniff" in content
    assert "X-Frame-Options DENY" in content
    assert "Referrer-Policy strict-origin-when-cross-origin" in content

    # Proxy must never have upstream or references to postgres
    assert "5432" not in content
    assert "postgres" not in content


def test_network_least_privilege_isolation():
    """Verify that reverse-proxy and app services observe least-privilege network attachments."""
    cmd = [
        "docker-compose",
        "-p", "sulocraft-gateway",
        "-f", str(COMPOSE_PROXY),
        "config"
    ]
    res = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True, check=True)
    proxy_config = yaml.safe_load(res.stdout)
    proxy_service = proxy_config["services"]["reverse-proxy"]

    # Proxy should only connect to sulocraft-gateway
    proxy_networks = list(proxy_service.get("networks", {}).keys())
    assert proxy_networks == ["sulocraft-gateway"], f"Proxy attached to unexpected networks: {proxy_networks}"

    # In both app environments, api connects to internal & gateway, but postgres connects ONLY to internal
    for env in ("preprod", "prod"):
        app_config = get_rendered_compose(f"sulocraft-{env}", env)
        api_networks = set(app_config["services"]["api"]["networks"].keys())
        pg_networks = set(app_config["services"]["postgres"]["networks"].keys())

        assert api_networks == {"internal", "gateway"}, f"API in {env} has unexpected networks: {api_networks}"
        assert pg_networks == {"internal"}, f"PostgreSQL in {env} has unexpected networks: {pg_networks}"


def test_runtime_secret_paths_isolated():
    """Verify that runtime secret paths default to isolated /run/sulocraft/<env>/ directories."""
    preprod = get_rendered_compose("sulocraft-preprod", "preprod")
    prod = get_rendered_compose("sulocraft-prod", "prod")

    preprod_db_secret = preprod["secrets"]["database_url"]["file"]
    prod_db_secret = prod["secrets"]["database_url"]["file"]

    assert "/run/sulocraft/preprod/" in preprod_db_secret
    assert "/run/sulocraft/prod/" in prod_db_secret
    assert preprod_db_secret != prod_db_secret

    preprod_pg_secret = preprod["secrets"]["postgres_db"]["file"]
    prod_pg_secret = prod["secrets"]["postgres_db"]["file"]

    assert "/run/sulocraft/preprod/" in preprod_pg_secret
    assert "/run/sulocraft/prod/" in prod_pg_secret
    assert preprod_pg_secret != prod_pg_secret


def test_bootstrap_secrets_fails_closed_without_prod_directory():
    """Verify that bootstrap_secrets.sh exits with non-zero code when targeting prod without dedicated secrets."""
    cmd = ["bash", str(REPO_ROOT / "backend" / "scripts" / "bootstrap_secrets.sh"), "--env", "prod"]
    res = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
    assert res.returncode != 0
    assert "cannot fall back across environments" in res.stderr


def test_r2_storage_bucket_isolation():
    """Verify that R2 public and backup buckets default to environment-specific names."""
    preprod = get_rendered_compose("sulocraft-preprod", "preprod")
    prod = get_rendered_compose("sulocraft-prod", "prod")

    preprod_env = preprod["services"]["api"]["environment"]
    prod_env = prod["services"]["api"]["environment"]

    assert preprod_env["R2_PUBLIC_BUCKET"] == "sulocraft-products-preprod"
    assert prod_env["R2_PUBLIC_BUCKET"] == "sulocraft-products-prod"
    assert preprod_env["R2_PUBLIC_BUCKET"] != prod_env["R2_PUBLIC_BUCKET"]

    assert preprod_env["R2_PRIVATE_BACKUP_BUCKET"] == "sulocraft-backups-preprod"
    assert prod_env["R2_PRIVATE_BACKUP_BUCKET"] == "sulocraft-backups-prod"
    assert preprod_env["R2_PRIVATE_BACKUP_BUCKET"] != prod_env["R2_PRIVATE_BACKUP_BUCKET"]


def test_backup_script_environment_aware():
    """Verify that database backup script isolates backup buckets and object prefixes by environment."""
    backup_script = (REPO_ROOT / "backend" / "scripts" / "backup_db.sh").read_text(encoding="utf-8")
    assert 'TARGET_ENV="${TARGET_ENV:-${SULOCRAFT_ENV:-${APP_ENV:-preprod}}}"' in backup_script
    assert 'DEFAULT_BACKUP_BUCKET="sulocraft-backups-${TARGET_ENV}"' in backup_script
    assert 'BACKUP_OBJECT_NAME="database/${TARGET_ENV}/sulocraft_db_${TIMESTAMP}.sql.gz"' in backup_script


def test_compose_email_sandbox_environment():
    """Verify Compose exposes email sandbox parameters with fail-closed preprod defaults."""
    preprod = get_rendered_compose("sulocraft-preprod", "preprod")
    api_env = preprod["services"]["api"]["environment"]

    assert "EMAIL_SANDBOX_ENABLED" in api_env
    assert api_env["EMAIL_SANDBOX_ENABLED"] in ("true", "True", True)
    assert "EMAIL_ALLOWLIST" in api_env
    assert "@sulocraft.com" in api_env["EMAIL_ALLOWLIST"]
    assert "EMAIL_SANDBOX_REDIRECT" in api_env


def test_email_allowlist_filtering():
    """Verify email recipient validation allows sulocraft domain and blocks customer addresses."""
    import sys
    sys.path.insert(0, str(REPO_ROOT / "backend"))
    from app.core.config import Settings
    from app.services.notification.email import is_recipient_allowed, resolve_delivery_recipient

    s = Settings(
        email_sandbox_enabled=True,
        email_allowlist_raw="@sulocraft.com,qa-team@example.com",
        email_sandbox_redirect="",
    )

    # Allowlisted domain and explicit address
    from unittest.mock import patch
    with patch("app.services.notification.email.settings", s):
        assert is_recipient_allowed("orders@sulocraft.com") is True
        assert is_recipient_allowed("anupama@sulocraft.com") is True
        assert is_recipient_allowed("qa-team@example.com") is True

        # Non-allowlisted external recipients
        assert is_recipient_allowed("real-customer@gmail.com") is False
        assert is_recipient_allowed("buyer@yahoo.in") is False

        # Resolution when suppressed
        to_email, subj, suppressed = resolve_delivery_recipient("real-customer@gmail.com", "Your Order SLC-100")
        assert suppressed is True
        assert to_email is None

        # Resolution when permitted
        to_email, subj, suppressed = resolve_delivery_recipient("anupama@sulocraft.com", "Your Order SLC-100")
        assert suppressed is False
        assert to_email == "anupama@sulocraft.com"


def test_email_sandbox_redirection():
    """Verify non-allowlisted email is redirected to sink mailbox when configured."""
    from unittest.mock import patch
    from app.core.config import Settings
    from app.services.notification.email import resolve_delivery_recipient

    s = Settings(
        email_sandbox_enabled=True,
        email_allowlist_raw="@sulocraft.com",
        email_sandbox_redirect="sink@sulocraft.com",
    )
    with patch("app.services.notification.email.settings", s):
        to_email, subj, suppressed = resolve_delivery_recipient("customer@example.com", "Order Update")
        assert suppressed is False
        assert to_email == "sink@sulocraft.com"
        assert "[SANDBOX -> customer@example.com]" in subj


def test_email_sandbox_disabled_in_production():
    """Verify that when sandbox is disabled, emails pass through unaffected."""
    from unittest.mock import patch
    from app.core.config import Settings
    from app.services.notification.email import resolve_delivery_recipient

    s = Settings(
        email_sandbox_enabled=False,
        email_allowlist_raw="@sulocraft.com",
        email_sandbox_redirect=None,
    )
    with patch("app.services.notification.email.settings", s):
        to_email, subj, suppressed = resolve_delivery_recipient("customer@gmail.com", "Production Order")
        assert suppressed is False
        assert to_email == "customer@gmail.com"
        assert subj == "Production Order"


def test_provider_suppression_mock_smtp_resend():
    """Verify Mock, SMTP, and Resend email providers suppress non-allowlisted sends without errors."""
    from unittest.mock import patch, MagicMock
    from app.core.config import Settings
    from app.services.notification.email import MockEmailProvider, SmtpEmailProvider, ResendEmailProvider

    s = Settings(
        email_sandbox_enabled=True,
        email_allowlist_raw="@sulocraft.com",
        email_sandbox_redirect=None,
        smtp_host="smtp.example.com",
        smtp_user="user",
        smtp_password="password",
        resend_api_key="re_test_key",
    )

    with patch("app.services.notification.email.settings", s):
        # 1. MockEmailProvider records suppression
        mock_p = MockEmailProvider()
        ok, err = mock_p.send_email("customer@gmail.com", "Test Subject", "<p>Hello</p>")
        assert ok is True
        assert err is None
        assert len(mock_p.sent_emails) == 1
        assert mock_p.sent_emails[0]["suppressed"] is True
        assert mock_p.sent_emails[0]["original_to"] == "customer@gmail.com"

        # 2. SmtpEmailProvider suppresses without opening network socket
        with patch("smtplib.SMTP") as mock_smtp:
            smtp_p = SmtpEmailProvider()
            ok, err = smtp_p.send_email("customer@gmail.com", "Test Subject", "<p>Hello</p>")
            assert ok is True
            assert err is None
            mock_smtp.assert_not_called()

        # 3. ResendEmailProvider suppresses without making HTTP API request
        with patch("httpx.Client") as mock_http:
            resend_p = ResendEmailProvider()
            ok, err = resend_p.send_email("customer@gmail.com", "Test Subject", "<p>Hello</p>")
            assert ok is True
            assert err is None
            mock_http.assert_not_called()


def test_environment_domain_and_callback_urls():
    """Verify environment-specific domain and public API URL resolution for OAuth and magic links."""
    from app.core.config import _default_frontend_url, _default_public_api_url

    # Preproduction resolution
    assert _default_frontend_url("preprod") == "https://dev.sulocraft.com"
    assert _default_public_api_url("preprod") == "https://api-dev.sulocraft.com"

    # Production resolution
    assert _default_frontend_url("production") == "https://sulocraft.com"
    assert _default_public_api_url("production") == "https://api.sulocraft.com"


def test_compose_resource_limits_defined():
    """Verify backend Compose defines CPU, memory, and PIDs limits and reservations for all services."""
    preprod = get_rendered_compose("sulocraft-preprod", "preprod")

    for svc_name in ("api", "postgres"):
        svc = preprod["services"][svc_name]
        assert "deploy" in svc, f"Service '{svc_name}' missing deploy configuration"
        assert "resources" in svc["deploy"], f"Service '{svc_name}' missing resources configuration"

        resources = svc["deploy"]["resources"]
        assert "limits" in resources, f"Service '{svc_name}' missing resource limits"
        limits = resources["limits"]
        assert "cpus" in limits, f"Service '{svc_name}' missing CPU limit"
        assert "memory" in limits, f"Service '{svc_name}' missing memory limit"
        assert "pids" in limits, f"Service '{svc_name}' missing PIDs limit"
        assert int(limits["pids"]) > 0

        assert "reservations" in resources, f"Service '{svc_name}' missing resource reservations"
        reservations = resources["reservations"]
        assert "cpus" in reservations, f"Service '{svc_name}' missing CPU reservation"
        assert "memory" in reservations, f"Service '{svc_name}' missing memory reservation"


def test_compose_log_rotation_configured():
    """Verify backend Compose and Proxy define json-file log rotation with file size and count caps."""
    preprod = get_rendered_compose("sulocraft-preprod", "preprod")

    for svc_name in ("api", "postgres"):
        svc = preprod["services"][svc_name]
        assert "logging" in svc, f"Service '{svc_name}' missing logging configuration"
        log_cfg = svc["logging"]
        assert log_cfg["driver"] == "json-file"
        assert "options" in log_cfg
        assert log_cfg["options"].get("max-size") in ("10m", "10M")
        assert str(log_cfg["options"].get("max-file")) == "3"

    # Verify proxy logging
    cmd = [
        "docker-compose",
        "-p", "sulocraft-gateway",
        "-f", str(COMPOSE_PROXY),
        "config"
    ]
    res = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True, check=True)
    proxy_config = yaml.safe_load(res.stdout)
    proxy_svc = proxy_config["services"]["reverse-proxy"]
    assert "logging" in proxy_svc
    assert proxy_svc["logging"]["driver"] == "json-file"
    assert proxy_svc["logging"]["options"].get("max-size") in ("10m", "10M")
    assert str(proxy_svc["logging"]["options"].get("max-file")) == "3"


def test_proxy_compose_resource_limits():
    """Verify reverse-proxy Compose defines bounded CPU and memory limits."""
    cmd = [
        "docker-compose",
        "-p", "sulocraft-gateway",
        "-f", str(COMPOSE_PROXY),
        "config"
    ]
    res = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True, check=True)
    proxy_config = yaml.safe_load(res.stdout)
    proxy = proxy_config["services"]["reverse-proxy"]

    assert "deploy" in proxy
    resources = proxy["deploy"]["resources"]
    assert "limits" in resources
    assert resources["limits"]["cpus"] == "0.50"
    # 256MB in bytes is 268435456
    assert int(resources["limits"]["memory"]) <= 300000000
    assert resources["limits"]["pids"] == 100
    assert "reservations" in resources


def test_cross_environment_comprehensive_isolation_audit():
    """Verify complete isolation matrix between preprod and prod across networks, volumes, secrets, buckets, and email."""
    preprod = get_rendered_compose("sulocraft-preprod", "preprod")
    prod = get_rendered_compose("sulocraft-prod", "prod")

    # 1. Project Namespacing
    assert preprod["name"] == "sulocraft-preprod"
    assert prod["name"] == "sulocraft-prod"

    # 2. Volumes
    preprod_vol = preprod["volumes"]["postgres_data"]["name"]
    prod_vol = prod["volumes"]["postgres_data"]["name"]
    assert preprod_vol != prod_vol
    assert "preprod" in preprod_vol and "prod" in prod_vol

    # 3. Networks: Postgres isolated from gateway and peer environment
    preprod_pg_net = preprod["services"]["postgres"]["networks"]
    prod_pg_net = prod["services"]["postgres"]["networks"]
    assert "internal" in preprod_pg_net and "gateway" not in preprod_pg_net
    assert "internal" in prod_pg_net and "gateway" not in prod_pg_net
    assert preprod["networks"]["internal"]["name"] != prod["networks"]["internal"]["name"]

    # 4. Zero public host ports on databases and APIs
    for env_cfg in (preprod, prod):
        assert not env_cfg["services"]["api"].get("ports", [])
        assert not env_cfg["services"]["postgres"].get("ports", [])

    # 5. Secrets: Disjoint directories
    preprod_secrets = {s["file"] for s in preprod["secrets"].values()}
    prod_secrets = {s["file"] for s in prod["secrets"].values()}
    assert preprod_secrets.isdisjoint(prod_secrets)
    assert all("/preprod/" in path for path in preprod_secrets)
    assert all("/prod/" in path for path in prod_secrets)

    # 6. Storage: Disjoint R2 buckets
    pre_env = preprod["services"]["api"]["environment"]
    prod_env = prod["services"]["api"]["environment"]
    assert pre_env["R2_PUBLIC_BUCKET"] != prod_env["R2_PUBLIC_BUCKET"]
    assert pre_env["R2_PRIVATE_BACKUP_BUCKET"] != prod_env["R2_PRIVATE_BACKUP_BUCKET"]

    # 7. Email Sandbox: Fail-closed in preprod
    assert pre_env["EMAIL_SANDBOX_ENABLED"] in ("true", "True", True)
    assert "@sulocraft.com" in pre_env["EMAIL_ALLOWLIST"]
