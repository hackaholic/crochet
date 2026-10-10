"""Exercise the actual Actions shell and configured health failure boundary."""
import importlib.util
import io
import os
from pathlib import Path
import subprocess
import sys
from urllib.error import URLError

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / 'scripts'))
import deploy_ci


def workflow():
    return yaml.safe_load((REPO_ROOT / '.github/workflows/deploy-dev-backend.yml').read_text())


def test_preprod_deploy_step_uses_shared_config_and_entry_point(tmp_path):
    step = next(s for s in workflow()['jobs']['deploy']['steps'] if s.get('name') == 'Deploy isolated preprod release')
    (tmp_path / 'scripts').mkdir()
    (tmp_path / 'deploy').mkdir()
    (tmp_path / 'scripts/deploy_ci.py').write_text((REPO_ROOT / 'scripts/deploy_ci.py').read_text())
    (tmp_path / 'scripts/deploy_vps.py').write_text((REPO_ROOT / 'scripts/deploy_vps.py').read_text())
    (tmp_path / 'deploy/vps-config.example.yaml').write_text((REPO_ROOT / 'deploy/vps-config.example.yaml').read_text())
    (tmp_path / 'deploy_vps.sh').write_text('printf "%s\\n" "$@"\n')
    env = dict(os.environ, VPS_USER='deploy-user', VPS_HOST='192.0.2.10', SULOCRAFT_PYTHON=sys.executable)
    result = subprocess.run(['bash', '-e', '-c', step['run']], cwd=tmp_path, env=env, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == ['--env', 'preprod', '--config', '.deploy/vps-config.yaml']
    config = yaml.safe_load((tmp_path / '.deploy/vps-config.yaml').read_text())
    assert config['environments']['preprod']['host'] == 'deploy-user@192.0.2.10'
    assert config['environments']['preprod']['public_api_url'] == 'https://api-dev.sulocraft.com'
    assert config['environments']['prod']['encrypted_secrets_dir'] == 'secrets/encrypted/prod'


@pytest.mark.parametrize('host,user', [('', 'root'), ('example.com;echo BAD', 'root'), ('example.com', '-root')])
def test_invalid_ssh_input_creates_no_config(tmp_path, monkeypatch, host, user):
    monkeypatch.setenv('VPS_HOST', host)
    monkeypatch.setenv('VPS_USER', user)
    dest = tmp_path / 'config.yaml'
    with pytest.raises(deploy_ci.ReleaseError):
        deploy_ci.configure(REPO_ROOT / 'deploy/vps-config.example.yaml', dest)
    assert not dest.exists()


@pytest.fixture
def health_config(tmp_path):
    config = yaml.safe_load((REPO_ROOT / 'deploy/vps-config.example.yaml').read_text())
    dest = tmp_path / 'config.yaml'
    dest.write_text(yaml.safe_dump(config))
    return dest


class Response(io.BytesIO):
    status = 200


@pytest.mark.parametrize('body', [b'{"status": "ok"}', b'{"status":"ok"}'])
def test_health_accepts_json_not_exact_whitespace(health_config, body):
    calls = []
    def opener(url, timeout):
        calls.append((url, timeout))
        return Response(body)
    deploy_ci.verify_health(health_config, 'preprod', opener=opener)
    assert calls == [('https://api-dev.sulocraft.com/health', 12)]


@pytest.mark.parametrize('body', [b'bad json', b'{"status":"down"}', b'[]'])
def test_unhealthy_response_exhaustion_fails(health_config, body):
    sleeps = []
    with pytest.raises(deploy_ci.ReleaseError, match='not accepted'):
        deploy_ci.verify_health(health_config, 'preprod', attempts=2, opener=lambda *a, **k: Response(body), sleeper=sleeps.append)
    assert sleeps == [4]


def test_network_failure_is_not_success(health_config):
    def offline(*a, **k):
        raise URLError('offline')
    with pytest.raises(deploy_ci.ReleaseError, match='not accepted'):
        deploy_ci.verify_health(health_config, 'preprod', attempts=1, opener=offline)


def test_missing_prod_config_never_falls_back(health_config):
    config = yaml.safe_load(health_config.read_text())
    del config['environments']['prod']
    health_config.write_text(yaml.safe_dump(config))
    with pytest.raises(deploy_ci.ReleaseError, match="no explicit 'prod'"):
        deploy_ci.verify_health(health_config, 'prod', opener=lambda *a, **k: pytest.fail('must not send request'))


def test_ci_gates_and_deployment_paths():
    data = workflow()
    trigger = data.get('on', data.get(True))
    paths = trigger['push']['paths']
    assert {'deploy/**', 'deploy_vps.sh', 'scripts/deploy*', 'backend/**', 'secrets/encrypted/**'} <= set(paths)
    assert data['jobs']['deploy']['needs'] == 'test'
    assert data['jobs']['deploy']['environment'] == 'development'
    health = next(s for s in data['jobs']['deploy']['steps'] if s.get('name') == 'Verify preprod API health')
    assert 'deploy_ci.py health --env preprod --config .deploy/vps-config.yaml' in health['run']
