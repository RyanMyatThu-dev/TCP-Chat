"""Protocol and real TLS integration checks; certificates live in a temp folder."""

import asyncio
import json
from pathlib import Path
import ssl
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from framing import MAX_FRAME_BYTES, ProtocolError, encode_frame, read_frame, send_frame
from server import ChatServer, LoginLimiter, Peer
from transport import AuthenticationError, client_context, close_writer, connect, server_context

PASSWORD = "a-long-test-room-password"


class FramingTests(unittest.IsolatedAsyncioTestCase):
    async def test_fragmented_and_coalesced_frames(self):
        reader = asyncio.StreamReader()
        messages = [{"type": "chat", "text": "hello 🌃"}, {"type": "quit"}]
        wire = b"".join(map(encode_frame, messages))
        async def feed():
            for byte in wire:
                reader.feed_data(bytes([byte]))
                await asyncio.sleep(0)
            reader.feed_eof()
        feeder = asyncio.create_task(feed())
        self.assertEqual(await read_frame(reader), messages[0])
        self.assertEqual(await read_frame(reader), messages[1])
        self.assertIsNone(await read_frame(reader))
        await feeder
        reader = asyncio.StreamReader()
        reader.feed_data(wire)
        reader.feed_eof()
        self.assertEqual(await read_frame(reader), messages[0])
        self.assertEqual(await read_frame(reader), messages[1])

    async def test_invalid_frames(self):
        cases = [b'\x00', struct.pack('!I', MAX_FRAME_BYTES + 1), b'\x00' * 4,
                 struct.pack('!I', 10) + b'{}', struct.pack('!I', 1) + b'\xff']
        for payload in [b'[]', b'{}', b'{bad json}', b'{"type": 1}']:
            cases.append(struct.pack('!I', len(payload)) + payload)
        for wire in cases:
            with self.subTest(wire=wire):
                reader = asyncio.StreamReader()
                reader.feed_data(wire)
                reader.feed_eof()
                with self.assertRaises(ProtocolError):
                    await read_frame(reader)

    def test_oversized_outgoing_frame(self):
        with self.assertRaises(ProtocolError):
            encode_frame({"type": "chat", "text": "x" * MAX_FRAME_BYTES})

    def test_limiter_window_and_memory_bound(self):
        limiter = LoginLimiter(attempts=2, window=60, max_ips=1)
        with patch('server.time.monotonic', return_value=0):
            self.assertTrue(limiter.allow('ip1'))
            self.assertTrue(limiter.allow('ip1'))
            self.assertFalse(limiter.allow('ip1'))
            self.assertFalse(limiter.allow('ip2'))
        with patch('server.time.monotonic', return_value=61):
            self.assertTrue(limiter.allow('ip2'))
            self.assertEqual(len(limiter.entries), 1)


class TLSTests(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cert_dir = Path(cls.temp.name) / 'certs'
        cls.cert = str(cert_dir / 'server.crt')
        cls.key = str(cert_dir / 'server.key')
        subprocess.run([
            sys.executable, str(Path(__file__).resolve().parents[1] / 'tools/generate_certificate.py'),
            '--host', 'localhost', '--out', str(cert_dir),
        ], check=True, capture_output=True)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    async def asyncSetUp(self):
        self.room = ChatServer(PASSWORD)
        self.server = await asyncio.start_server(
            self.room.handle_client, '127.0.0.1', 0,
            ssl=server_context(self.cert, self.key), ssl_handshake_timeout=1,
        )
        self.port = self.server.sockets[0].getsockname()[1]
        self.writers = []
        # Expected bad-certificate handshakes are reported by asyncio in debug mode.
        self.loop = asyncio.get_running_loop()
        self.old_handler = self.loop.get_exception_handler()
        self.unexpected_errors = []
        self.loop.set_exception_handler(self.capture_error)

    def capture_error(self, loop, context):
        if not isinstance(context.get('exception'), (ssl.SSLError, ConnectionResetError)):
            self.unexpected_errors.append(context)

    async def asyncTearDown(self):
        for writer in self.writers:
            await close_writer(writer)
        self.server.close()
        await self.server.wait_closed()
        await self.room.shutdown()
        self.loop.set_exception_handler(self.old_handler)
        self.assertEqual(self.unexpected_errors, [])

    async def login(self, name='Raven', password=PASSWORD):
        reader, writer = await connect('localhost', self.port, name, password, self.cert)
        self.writers.append(writer)
        return reader, writer

    async def raw(self):
        reader, writer = await asyncio.open_connection(
            '127.0.0.1', self.port, ssl=client_context(self.cert), server_hostname='localhost')
        self.writers.append(writer)
        return reader, writer

    async def receive(self, reader):
        return await asyncio.wait_for(read_frame(reader), 2)

    async def test_broadcast_identity_and_disconnect(self):
        alice, aw = await self.login('Alice')
        self.assertEqual((await self.receive(alice))['type'], 'notice')
        bob, bw = await self.login('Bob')
        await self.receive(alice)
        await self.receive(bob)
        await send_frame(aw, {'type': 'chat', 'name': 'Bob', 'text': 'hello 🌃\nnext line'})
        expected = {'type': 'chat', 'name': 'Alice', 'text': 'hello 🌃\nnext line'}
        self.assertEqual(await self.receive(alice), expected)
        self.assertEqual(await self.receive(bob), expected)
        await send_frame(bw, {'type': 'quit'})
        self.assertEqual((await self.receive(alice))['message'], 'Bob has left the chat')
        self.assertIsNone(await self.receive(bob))

    async def test_wrong_password_and_unauthenticated_chat(self):
        with self.assertRaises(AuthenticationError):
            await self.login(password='wrong-password')
        reader, writer = await self.raw()
        await send_frame(writer, {'type': 'chat', 'text': 'bypass'})
        self.assertEqual((await self.receive(reader))['type'], 'error')
        self.assertIsNone(await self.receive(reader))
        self.assertEqual(self.room.clients, {})

    async def test_unauthenticated_peer_receives_no_broadcast(self):
        reader, _ = await self.raw()
        alice, writer = await self.login('Alice')
        await self.receive(alice)
        await send_frame(writer, {'type': 'chat', 'text': 'private message'})
        await self.receive(alice)
        with self.assertRaises(TimeoutError):
            await asyncio.wait_for(read_frame(reader), .1)

    async def test_duplicate_and_invalid_aliases(self):
        await self.login('Raven')
        with self.assertRaises(AuthenticationError):
            await self.login('raven')
        with self.assertRaises(AuthenticationError):
            await self.login('bad : alias')

    async def test_untrusted_and_wrong_hostname_certificates(self):
        with self.assertRaises(ssl.SSLCertVerificationError):
            await connect('localhost', self.port, 'Raven', PASSWORD)
        with self.assertRaises(ssl.SSLCertVerificationError):
            await connect('127.0.0.1', self.port, 'Raven', PASSWORD, self.cert)
        self.assertEqual(self.room.clients, {})

    async def test_login_throttle(self):
        self.room.limiter = LoginLimiter(attempts=1)
        with self.assertRaises(AuthenticationError):
            await self.login(password='wrong')
        with self.assertRaisesRegex(AuthenticationError, 'Too many'):
            await self.login()

    async def test_login_timeout(self):
        with patch('server.AUTH_TIMEOUT', .05):
            reader, _ = await self.raw()
            self.assertEqual((await self.receive(reader))['type'], 'error')
            self.assertIsNone(await self.receive(reader))

    async def test_oversized_and_malformed_frames_disconnect(self):
        for data in [struct.pack('!I', MAX_FRAME_BYTES + 1), struct.pack('!I', 1) + b'{']:
            reader, writer = await self.raw()
            writer.write(data)
            await writer.drain()
            self.assertEqual((await self.receive(reader))['type'], 'error')
            self.assertIsNone(await self.receive(reader))

    async def test_message_limit(self):
        reader, writer = await self.login()
        await self.receive(reader)
        await send_frame(writer, {'type': 'chat', 'text': 'x' * 4001})
        self.assertEqual((await self.receive(reader))['type'], 'error')
        self.assertIsNone(await self.receive(reader))

    async def test_empty_and_control_character_messages(self):
        for name, text in [('Empty', ' '), ('Control', '\x1b[2J'), ('Surrogate', '\ud800')]:
            reader, writer = await self.login(name)
            await self.receive(reader)
            payload = json.dumps({'type': 'chat', 'text': text}).encode()
            writer.write(struct.pack('!I', len(payload)) + payload)
            await writer.drain()
            self.assertEqual((await self.receive(reader))['type'], 'error')
            self.assertIsNone(await self.receive(reader))

    async def test_room_capacity(self):
        with patch('server.MAX_CLIENTS', 1):
            await self.login('Alice')
            with self.assertRaisesRegex(AuthenticationError, 'full'):
                await self.login('Bob')

    async def test_message_rate_limit(self):
        reader, writer = await self.login()
        await self.receive(reader)
        for number in range(20):
            await send_frame(writer, {'type': 'chat', 'text': str(number)})
            self.assertEqual((await self.receive(reader))['type'], 'chat')
        await send_frame(writer, {'type': 'chat', 'text': 'too fast'})
        self.assertEqual((await self.receive(reader))['type'], 'error')
        self.assertIsNone(await self.receive(reader))

    async def test_bounded_slow_client_queue(self):
        from unittest.mock import Mock
        slow_writer = Mock()
        peer = Peer('slow', slow_writer, asyncio.Queue(maxsize=1))
        self.room.clients['slow'] = peer
        self.room.broadcast({'type': 'notice', 'message': 'one'})
        self.room.broadcast({'type': 'notice', 'message': 'two'})
        slow_writer.close.assert_called_once()
        self.assertEqual(peer.queue.qsize(), 1)
        self.room.clients.clear()

    async def test_multi_client_smoke_tool(self):
        from argparse import Namespace
        from test_clients import run
        await run(Namespace(host='localhost', port=self.port, ca=self.cert,
                            clients=5, messages=3, delay=.01), PASSWORD)

    async def test_plaintext_connection_is_rejected(self):
        reader, writer = await asyncio.open_connection('127.0.0.1', self.port)
        self.writers.append(writer)
        writer.write(encode_frame({'type': 'auth', 'name': 'Plain', 'password': PASSWORD}))
        await writer.drain()
        try:
            self.assertEqual(await asyncio.wait_for(reader.read(1), 2), b'')
        except ConnectionResetError:
            pass
        self.assertEqual(self.room.clients, {})

    async def test_server_shutdown_cancels_client_composer(self):
        from argparse import Namespace
        from unittest.mock import AsyncMock, Mock
        from client import run_client
        composing = asyncio.Event()
        cancelled = asyncio.Event()
        async def compose():
            composing.set()
            try:
                await asyncio.Event().wait()
            finally:
                cancelled.set()
        ui = Mock()
        ui.identity = AsyncMock(return_value='Raven')
        ui.password = AsyncMock(return_value=PASSWORD)
        ui.compose = compose
        with patch('client.ChatUI', return_value=ui):
            client = asyncio.create_task(run_client(Namespace(host='localhost', port=self.port, ca=self.cert)))
            try:
                await asyncio.wait_for(composing.wait(), 2)
                await self.room.shutdown()
                await asyncio.wait_for(client, 2)
                self.assertTrue(cancelled.is_set())
                self.assertEqual(self.room.clients, {})
            finally:
                client.cancel()
                await asyncio.gather(client, return_exceptions=True)


if __name__ == '__main__':
    unittest.main()
