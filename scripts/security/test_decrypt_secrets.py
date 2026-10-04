import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "decrypt_secrets.py"


class DecryptSecretsDynamicTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.encrypted = self.root / "encrypted"
        self.encrypted.mkdir()
        for group in ("postgres", "backend"):
            (self.encrypted / f"{group}.enc.env").write_text("ciphertext-only", encoding="utf-8")
        self.key = self.root / "age-key.txt"
        self.key.write_text("AGE-SECRET-KEY-test-only", encoding="utf-8")
        self.key.chmod(0o600)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.docker = self.bin / "docker"
        self.docker.write_text(
            "#!/usr/bin/env python3\n"
            "import os, pathlib, sys\n"
            "args=sys.argv[1:]\n"
            "if os.environ.get('MOCK_DECRYPT_FAIL'):\n"
            " print('test-only-secret-value', file=sys.stderr); sys.exit(2)\n"
            "mount=next(x for x in args if x.endswith(':/input:ro'))\n"
            "name=pathlib.Path(mount.split(':', 1)[0]).name\n"
            "data={'postgres.enc.env':'POSTGRES_DB=localdb\\nPOSTGRES_USER=localuser\\nPOSTGRES_PASSWORD=test-pass\\n',"
            "'backend.enc.env':'DATABASE_URL=postgresql://remote:secret@remote.example/db\\nR2_ACCESS_KEY_ID=key\\nR2_SECRET_ACCESS_KEY=secret\\nRESEND_API_KEY=\\n'}\n"
            "sys.stdout.write(data[name])\n",
            encoding="utf-8",
        )
        self.docker.chmod(0o700)

    def tearDown(self):
        self.temp.cleanup()

    def run_helper(self, *extra, env_vars=None):
        env = os.environ.copy()
        env["PATH"] = f"{self.bin}:{env['PATH']}"
        if env_vars:
            env.update(env_vars)
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--key", str(self.key), "--encrypted-dir", str(self.encrypted), *extra],
            env=env, text=True, capture_output=True, check=False,
        )

    def test_dynamic_env_flag_dev(self):
        dev_output = self.root / "backend" / ".secrets" / "dev"
        result = self.run_helper("--env", "dev", "--output-dir", str(dev_output))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(dev_output.exists())
        self.assertEqual((dev_output / "backend" / "database_url").read_text(), "postgresql://localuser:test-pass@db:5432/localdb")
        compose_env = (dev_output / "compose.env").read_text()
        self.assertIn(f"SULOCRAFT_DEV_BACKEND_DIR={dev_output / 'backend'}", compose_env)
        self.assertIn(f"SULOCRAFT_BACKEND_DIR={dev_output / 'backend'}", compose_env)

    def test_dynamic_env_from_config_env_var(self):
        preprod_output = self.root / "backend" / ".secrets" / "preprod"
        result = self.run_helper("--output-dir", str(preprod_output), env_vars={"APP_ENV": "preprod"})
        self.assertEqual(result.returncode, 0, result.stderr)
        compose_env = (preprod_output / "compose.env").read_text()
        self.assertIn(f"SULOCRAFT_PREPROD_BACKEND_DIR={preprod_output / 'backend'}", compose_env)

    def test_clean_flag(self):
        dev_output = self.root / "backend" / ".secrets" / "dev"
        self.run_helper("--env", "dev", "--output-dir", str(dev_output))
        self.assertTrue(dev_output.exists())
        clean_result = self.run_helper("--clean", "--env", "dev", "--output-dir", str(dev_output))
        self.assertEqual(clean_result.returncode, 0)
        self.assertFalse(dev_output.exists())

    def test_config_file_support(self):
        cfg = self.root / "deploy.conf"
        dev_output = self.root / "backend" / ".secrets" / "custom"
        cfg.write_text(
            f"TARGET_ENV=dev\n"
            f"RUNTIME_SECRETS_DIR={dev_output}\n"
            f"SECRETS_DIR={self.encrypted}\n"
            f"SOPS_AGE_KEY_FILE={self.key}\n",
            encoding="utf-8",
        )
        env = os.environ.copy()
        env["PATH"] = f"{self.bin}:{env['PATH']}"
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--config", str(cfg)],
            env=env, text=True, capture_output=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(dev_output.exists())
        self.assertTrue((dev_output / "backend" / "database_url").exists())

    def test_cross_environment_isolation_fails_closed(self):
        # Attempting prod without explicit prod encrypted directory must fail closed (DEC-003-5)
        env = os.environ.copy()
        env["PATH"] = f"{self.bin}:{env['PATH']}"
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--env", "prod", "--key", str(self.key)],
            env=env, text=True, capture_output=True, check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("encrypted secrets directory for environment 'prod' not found", result.stderr)


if __name__ == "__main__":
    unittest.main()
