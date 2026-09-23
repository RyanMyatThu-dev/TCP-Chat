"""Verified TLS connections and the room authentication handshake."""

import asyncio
import ssl

from framing import ProtocolError, read_frame, send_frame

CONNECT_TIMEOUT = 15


class AuthenticationError(Exception):
    """The server rejected room access."""


def client_context(cafile=None):
    context = ssl.create_default_context(cafile=cafile)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    return context


def server_context(certfile, keyfile):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.load_cert_chain(certfile, keyfile)
    return context


async def close_writer(writer):
    writer.close()
    try:
        await asyncio.wait_for(writer.wait_closed(), timeout=2)
    except (OSError, TimeoutError):
        pass


async def connect(host, port, name, password, cafile=None):
    """Never send credentials until certificate and hostname verification pass."""
    reader, writer, _ = await authenticate(
        host, port, {"type": "auth", "name": name, "password": password}, cafile
    )
    return reader, writer


async def authenticate(host, port, request, cafile=None):
    """Open a verified TLS connection and authenticate a legacy or room request."""
    reader, writer = await asyncio.wait_for(
        asyncio.open_connection(
            host, port, ssl=client_context(cafile), server_hostname=host,
            ssl_handshake_timeout=CONNECT_TIMEOUT,
        ), timeout=CONNECT_TIMEOUT,
    )
    try:
        await asyncio.wait_for(
            send_frame(writer, request),
            timeout=CONNECT_TIMEOUT,
        )
        response = await asyncio.wait_for(read_frame(reader), timeout=CONNECT_TIMEOUT)
        if response is None:
            raise AuthenticationError("Server closed the connection before login completed.")
        if response["type"] == "error":
            detail = response.get("message", "Room access denied.")
            raise AuthenticationError(detail if isinstance(detail, str) else "Room access denied.")
        if response["type"] != "auth_ok":
            raise ProtocolError("Unexpected authentication response.")
        return reader, writer, response
    except BaseException:
        await close_writer(writer)
        raise
