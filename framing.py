"""Length-prefixed JSON messages over an asyncio byte stream."""

import asyncio
import json
import re
import struct

MAX_FRAME_BYTES = 16_384
MAX_MESSAGE_BYTES = 4_000
ALIAS = re.compile(r"[A-Za-z0-9_-]{1,24}\Z")


class ProtocolError(ValueError):
    """A peer sent an invalid or oversized message."""


def encode_frame(message):
    payload = json.dumps(message, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    if not 0 < len(payload) <= MAX_FRAME_BYTES:
        raise ProtocolError("Message exceeds the frame size limit.")
    return struct.pack("!I", len(payload)) + payload


async def read_frame(reader):
    """Return one object, or None for EOF between complete frames."""
    try:
        header = await reader.readexactly(4)
    except asyncio.IncompleteReadError as error:
        if not error.partial:
            return None
        raise ProtocolError("Incomplete message header.") from error
    size = struct.unpack("!I", header)[0]
    if not 0 < size <= MAX_FRAME_BYTES:
        raise ProtocolError("Invalid frame size.")
    try:
        payload = await reader.readexactly(size)
        message = json.loads(payload.decode("utf-8"))
    except (asyncio.IncompleteReadError, UnicodeError, ValueError, RecursionError) as error:
        raise ProtocolError("Invalid message body.") from error
    if not isinstance(message, dict) or not isinstance(message.get("type"), str):
        raise ProtocolError("Expected a message object with a type.")
    return message


async def send_frame(writer, message):
    # One write keeps frames together even when multiple tasks share a writer.
    writer.write(encode_frame(message))
    await writer.drain()


def valid_alias(name):
    return isinstance(name, str) and ALIAS.fullmatch(name) is not None


def valid_text(text):
    if not isinstance(text, str) or not text.strip():
        return False
    try:
        return len(text.encode("utf-8")) <= MAX_MESSAGE_BYTES and all(
            char.isprintable() or char in "\n\t" for char in text
        )
    except UnicodeError:
        return False
