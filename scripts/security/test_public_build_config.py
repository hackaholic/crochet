"""Regression tests for tracked public build config; no production files changed."""
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


class PublicBuildConfigTests(unittest.TestCase):
    def audit(self, text, filename=".env.preprod", git=True):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            script = root / "scripts/security/scan-config.sh"
            script.parent.mkdir(parents=True)
            shutil.copyfile(Path(__file__).with_name("scan-config.sh"), script)
            (root / filename).write_text(text)
            if git:
                subprocess.run(["git", "init", "-q", directory], check=True)
                subprocess.run(["git", "-C", directory, "add", filename], check=True)
            return subprocess.run(["bash", str(script)], capture_output=True, text=True)

    def test_named_public_settings_pass(self):
        result = self.audit("VITE_LAUNCH_MODE=full\nSEO_INDEXING_ENABLED=false\nSEO_PUBLIC_ORIGIN=https://dev.example.test\n")
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_unknown_or_private_settings_fail(self):
        for key in ["RESEND_API_KEY", "SEO_PRIVATE_KEY", "SEO_API_BASE_URL"]:
            with self.subTest(key=key):
                self.assertNotEqual(self.audit(f"{key}=not-a-secret-fixture\n").returncode, 0)

    def test_bad_origin_and_boolean_fail(self):
        for value in ["https://user:pass@example.test", "javascript:alert(1)", "https://example.test/path", "https://example.test?q=x"]:
            with self.subTest(value=value):
                self.assertNotEqual(self.audit(f"SEO_PUBLIC_ORIGIN={value}\n").returncode, 0)
        self.assertNotEqual(self.audit("SEO_INDEXING_ENABLED=yes\n").returncode, 0)
        self.assertNotEqual(self.audit("SEO_PUBLIC_ORIGIN=http://example.test\n", ".env.production").returncode, 0)

    def test_missing_git_inventory_fails_closed(self):
        self.assertNotEqual(self.audit("VITE_LAUNCH_MODE=full\n", git=False).returncode, 0)


if __name__ == "__main__":
    unittest.main()
