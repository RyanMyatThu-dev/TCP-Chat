"""Ephemeral, password-protected TCP chat room over TLS."""

import argparse
import asyncio
from collections import OrderedDict
from dataclasses import dataclass, field
import getpass
import hashlib
import hmac
import os
from pathlib import Path
import time

from framing import ProtocolError, read_frame, send_frame, valid_alias, valid_text
from transport import close_writer, server_context

AUTH_TIMEOUT = 10
WRITE_TIMEOUT = 5
MAX_CLIENTS = 32
MAX_PENDING_MESSAGES = 64


class LoginLimiter:
    """Bounded per-IP authentication budget, including successful logins."""

    def __init__(self, attempts=10, window=60, max_ips=4096):
        self.attempts, self.window, self.max_ips = attempts, window, max_ips
        self.entries = OrderedDict()

    def allow(self, ip):
        now = time.monotonic()
        while self.entries and next(iter(self.entries.values()))[0] <= now:
            self.entries.popitem(last=False)
        if ip not in self.entries:
            if len(self.entries) >= self.max_ips:
                return False
            self.entries[ip] = (now + self.window, 0)
        deadline, count = self.entries[ip]
        if count >= self.attempts:
            return False
        self.entries[ip] = (deadline, count + 1)
        return True


@dataclass(eq=False)
class Peer:
    name: str
    writer: asyncio.StreamWriter
    queue: asyncio.Queue = field(default_factory=lambda: asyncio.Queue(MAX_PENDING_MESSAGES))


class ChatServer:
    def __init__(self, password):
        if len(password) < 16 or len(password.encode("utf-8")) > 1024:
            raise ValueError("Use a room password of at least 16 characters (at most 1024 UTF-8 bytes).")
        # Compare fixed-size digests in constant time; no password database.
        self.password_digest = hashlib.sha256(password.encode("utf-8")).digest()
        self.clients = {}
        self.connections = set()
        self.tasks = set()
        self.limiter = LoginLimiter()

    def broadcast(self, message):
        for peer in tuple(self.clients.values()):
            try:
                peer.queue.put_nowait(message)
            except asyncio.QueueFull:
                # A slow client must not stall the room or grow memory unboundedly.
                peer.writer.close()

    async def deliver(self, peer):
        try:
            while True:
                message = await peer.queue.get()
                await asyncio.wait_for(send_frame(peer.writer, message), WRITE_TIMEOUT)
        except (OSError, TimeoutError):
            peer.writer.close()

    async def reject(self, writer, message):
        await asyncio.wait_for(send_frame(writer, {"type": "error", "message": message}), WRITE_TIMEOUT)

    async def handle_client(self, reader, writer):
        task = asyncio.current_task()
        self.tasks.add(task)
        peer = None
        sender = None
        try:
            if len(self.connections) >= MAX_CLIENTS:
                await self.reject(writer, "Room is full. Try again later.")
                return
            self.connections.add(writer)
            ip = writer.get_extra_info("peername")[0]
            if not self.limiter.allow(ip):
                await self.reject(writer, "Too many login attempts. Wait one minute and try again.")
                return
            auth = await asyncio.wait_for(read_frame(reader), AUTH_TIMEOUT)
            if auth is None:
                return
            if auth["type"] != "auth":
                await self.reject(writer, "Authenticate before sending chat messages.")
                return
            password = auth.get("password")
            if not isinstance(password, str):
                await self.reject(writer, "Room access denied.")
                return
            try:
                encoded_password = password.encode("utf-8")
            except UnicodeError:
                await self.reject(writer, "Room access denied.")
                return
            if len(encoded_password) > 1024 or not hmac.compare_digest(
                hashlib.sha256(encoded_password).digest(), self.password_digest
            ):
                await self.reject(writer, "Room access denied.")
                return
            name = auth.get("name")
            # Do not retain the plaintext password after authentication.
            del auth, password, encoded_password
            if not valid_alias(name):
                await self.reject(writer, "Alias must be 1–24 letters, numbers, underscores, or hyphens.")
                return
            key = name.casefold()
            if key in self.clients:
                await self.reject(writer, "That alias is already in use. Choose another.")
                return
            peer = Peer(name, writer)
            # Reserve the alias before yielding to another connection.
            self.clients[key] = peer
            await asyncio.wait_for(send_frame(writer, {"type": "auth_ok"}), WRITE_TIMEOUT)
            sender = asyncio.create_task(self.deliver(peer))
            self.broadcast({"type": "notice", "message": f"{name} has joined the chat"})
            recent_messages = []
            while True:
                message = await read_frame(reader)
                if message is None or message["type"] == "quit":
                    break
                if message["type"] != "chat" or not valid_text(message.get("text")):
                    await self.reject(writer, "Send nonempty text of at most 4000 UTF-8 bytes, without control characters.")
                    break
                now = time.monotonic()
                recent_messages = [stamp for stamp in recent_messages if now - stamp < 10]
                if len(recent_messages) >= 20:
                    await self.reject(writer, "Message limit reached (20 per 10 seconds). Please reconnect later.")
                    break
                recent_messages.append(now)
                # Sender identity always comes from authentication, never chat payloads.
                self.broadcast({"type": "chat", "name": name, "text": message["text"]})
        except (ProtocolError, TimeoutError):
            try:
                await self.reject(writer, "Invalid message or login timed out.")
            except (OSError, TimeoutError):
                pass
        except OSError:
            pass
        finally:
            if peer is not None:
                self.clients.pop(peer.name.casefold(), None)
                self.broadcast({"type": "notice", "message": f"{peer.name} has left the chat"})
            if sender is not None:
                sender.cancel()
                await asyncio.gather(sender, return_exceptions=True)
            self.connections.discard(writer)
            await close_writer(writer)
            self.tasks.discard(task)

    async def shutdown(self):
        for task in tuple(self.tasks):
            task.cancel()
        await asyncio.gather(*tuple(self.tasks), return_exceptions=True)


async def serve(arguments, password):
    room = ChatServer(password)
    del password
    context = server_context(arguments.cert, arguments.key)
    listener = await asyncio.start_server(
        room.handle_client, arguments.host, arguments.port, ssl=context,
        ssl_handshake_timeout=AUTH_TIMEOUT,
    )
    print(f"NEON / CHAT listening on {arguments.host}:{arguments.port} · TLS · password required", flush=True)
    try:
        async with listener:
            await listener.serve_forever()
    finally:
        await room.shutdown()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1", help="Use 0.0.0.0 on your AWS instance")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--cert", required=True, help="PEM server certificate / chain")
    parser.add_argument("--key", required=True, help="PEM private key (server only)")
    parser.add_argument("--password-file", type=Path, help="Read the room password from a private file")
    arguments = parser.parse_args()
    try:
        if arguments.password_file:
            password = arguments.password_file.read_text().rstrip("\r\n")
        else:
            password = os.environ.pop("CHAT_ROOM_PASSWORD", None) or getpass.getpass("Room password (16+ characters): ")
        asyncio.run(serve(arguments, password))
    except KeyboardInterrupt:
        print("\nRoom closed.")
    except (OSError, ValueError) as error:
        parser.exit(1, f"Server could not start: {error}\n")


if __name__ == "__main__":
    main()
