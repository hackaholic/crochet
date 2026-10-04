import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "decrypt_preprod_secrets.py"


class DecryptPreprodTests(unittest.TestCase):
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
        self.output = self.root / "backend" / ".secrets" / "preprod"

    def tearDown(self):
        self.temp.cleanup()

    def run_helper(self, *extra, fail=False):
        env = os.environ.copy()
        env["PATH"] = f"{self.bin}:{env['PATH']}"
        if fail:
            env["MOCK_DECRYPT_FAIL"] = "1"
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--key", str(self.key), "--encrypted-dir", str(self.encrypted), "--output-dir", str(self.output), *extra],
            env=env, text=True, capture_output=True, check=False,
        )

    def test_materializes_owner_only_secrets_and_local_database_url(self):
        result = self.run_helper()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.output / "backend" / "database_url").read_text(), "postgresql://localuser:test-pass@db:5432/localdb")
        self.assertNotIn("remote.example", (self.output / "backend" / "database_url").read_text())
        self.assertEqual((self.output / "backend" / "r2_secret_access_key").stat().st_mode & 0o777, 0o600)
        self.assertEqual((self.output / "backend").stat().st_mode & 0o777, 0o700)
        self.assertEqual((self.output / "postgres").stat().st_mode & 0o777, 0o700)
        compose_env = (self.output / "compose.env").read_text()
        self.assertIn(f"SULOCRAFT_PREPROD_BACKEND_DIR={self.output / 'backend'}", compose_env)
        self.assertNotIn("test-pass", compose_env)

    def test_decrypt_errors_do_not_echo_provider_output(self):
        result = self.run_helper(fail=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("test-only-secret-value", result.stderr)
        self.assertFalse(self.output.exists())

    def test_rejects_group_setting_outside_allowlist(self):
        self.docker.write_text(
            "#!/usr/bin/env python3\nimport pathlib,sys\n"
            "m=next(x for x in sys.argv if x.endswith(':/input:ro'))\n"
            "print('UNEXPECTED=not-allowed')\n",
            encoding="utf-8",
        )
        self.docker.chmod(0o700)
        result = self.run_helper()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unsupported setting name", result.stderr)
        self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()
