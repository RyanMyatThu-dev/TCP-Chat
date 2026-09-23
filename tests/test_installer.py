"""Installer output must reflect the actual package-manager outcome."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'web/public/install.sh'


class InstallerTests(unittest.TestCase):
    def run_installer(self, status):
        with tempfile.TemporaryDirectory() as directory:
            uv = Path(directory) / 'uv'
            uv.write_text(f'#!/bin/sh\nexit {status}\n')
            uv.chmod(0o755)
            return subprocess.run(['/bin/sh', str(SCRIPT)], text=True, capture_output=True,
                                  env={**os.environ, 'PATH': f'{directory}:/usr/bin:/bin', 'NO_COLOR': '1'})

    def test_success_includes_logo_and_next_steps(self):
        result = self.run_installer(0)
        self.assertEqual(result.returncode, 0)
        self.assertIn('C H A T  /  T E R M I N A L', result.stdout)
        self.assertIn('Installation complete.', result.stdout)
        self.assertIn('neon-chat host', result.stdout)
        self.assertNotIn('\x1b', result.stdout)

    def test_failure_never_claims_success(self):
        result = self.run_installer(1)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('Installation complete.', result.stdout)
        self.assertIn('Installation failed.', result.stderr)
