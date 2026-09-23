"""Code parsing, command routing, and certificate renewal guarantees."""
import argparse
import asyncio
import importlib.util
from pathlib import Path
import ssl
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import AsyncMock, patch

from neon_chat import cli
from room_codes import new_code, normalize_code, display_code


class CommandTests(unittest.TestCase):
    def test_codes(self):
        codes = {new_code() for _ in range(100)}
        self.assertEqual(len(codes), 100)
        for code in codes:
            self.assertEqual(normalize_code(display_code(code).lower()), code)
        for bad in (None, [], '', 'AAAA', 'IIII-IIII-IIII', 'A' * 100):
            with self.assertRaises(ValueError):
                normalize_code(bad)

    def test_commands_send_only_needed_fields(self):
        for command in ('host', 'join'):
            with self.subTest(command=command), patch.object(cli, 'ChatUI') as ui, \
                    patch.object(cli, 'authenticate', new_callable=AsyncMock) as auth, \
                    patch.object(cli, 'chat', new_callable=AsyncMock) as chat:
                auth.return_value = ('reader', 'writer', {'code': 'ABCD1234EFGH'})
                args = argparse.Namespace(command=command, name='Raven', code='abcd-1234-efgh')
                asyncio.run(cli.run(args, 'localhost', 5000, 'ca.crt'))
                expected = {'type': 'create' if command == 'host' else 'join', 'name': 'Raven'}
                if command == 'join':
                    expected['code'] = 'ABCD1234EFGH'
                auth.assert_awaited_once_with('localhost', 5000, expected, 'ca.crt')
                chat.assert_awaited_once_with('reader', 'writer', ui.return_value)

    def test_invalid_invitation_exits_before_network(self):
        with patch.object(sys, 'argv', ['neon-chat', 'join', 'invalid']), \
                patch.object(cli, 'authenticate', new_callable=AsyncMock) as auth:
            with self.assertRaises(SystemExit) as result:
                cli.main()
            self.assertEqual(result.exception.code, 1)
            auth.assert_not_called()


class AuthorityTests(unittest.TestCase):
    def test_renewal_preserves_trust_and_identity(self):
        script = Path(__file__).resolve().parents[1] / 'tools/issue_service_certificate.py'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            args = [sys.executable, str(script), '--host', '127.0.0.1',
                    '--authority', str(root / 'authority'), '--out', str(root / 'leaf')]
            subprocess.run(args, check=True, capture_output=True)
            ca = (root / 'authority/ca.crt').read_bytes()
            first_leaf = (root / 'leaf/server.crt').read_bytes()
            subprocess.run(args, check=True, capture_output=True)
            self.assertEqual(ca, (root / 'authority/ca.crt').read_bytes())
            self.assertNotEqual(first_leaf, (root / 'leaf/server.crt').read_bytes())
            subprocess.run(['openssl', 'verify', '-CAfile', str(root / 'authority/ca.crt'),
                            '-verify_ip', '127.0.0.1', str(root / 'leaf/server.crt')],
                           check=True, capture_output=True)
            wrong = subprocess.run(['openssl', 'verify', '-CAfile', str(root / 'authority/ca.crt'),
                                    '-verify_ip', '127.0.0.2', str(root / 'leaf/server.crt')],
                                   capture_output=True)
            self.assertNotEqual(wrong.returncode, 0)
            self.assertEqual((root / 'authority/ca.key').stat().st_mode & 0o777, 0o600)
