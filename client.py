"""NEON / CHAT client: verified TLS and shared room authentication."""

import argparse
import asyncio
import ssl

from prompt_toolkit.patch_stdout import patch_stdout

from chat_ui import ChatUI
from framing import ProtocolError, read_frame, send_frame, valid_alias, valid_text
from transport import AuthenticationError, close_writer, connect


async def receive_messages(reader, ui):
    while True:
        message = await read_frame(reader)
        if message is None:
            ui.notice("Connection closed. Run the client again to reconnect.")
            return
        kind = message["type"]
        if kind == "chat" and valid_alias(message.get("name")) and valid_text(message.get("text")):
            ui.message(message["name"], message["text"])
        elif kind in {"notice", "error", "room_closed"} and isinstance(message.get("message"), str):
            ui.notice(message["message"])
            if kind in {"error", "room_closed"}:
                return
        else:
            raise ProtocolError("The server sent an unexpected message.")


async def send_messages(writer, ui):
    while True:
        try:
            text = await ui.compose()
        except (EOFError, KeyboardInterrupt):
            return
        if text.strip() == "/quit":
            await asyncio.wait_for(send_frame(writer, {"type": "quit"}), timeout=5)
            return
        if text.strip() == "/invite" and getattr(ui, "room_code", ""):
            ui.invitation(ui.room_code, is_host=False)
            continue
        if not valid_text(text):
            ui.notice("Use 1–4000 UTF-8 bytes of text, without control characters.")
            continue
        await asyncio.wait_for(send_frame(writer, {"type": "chat", "text": text}), timeout=5)


async def run_client(arguments):
    ui = ChatUI()
    ui.welcome()
    name = await ui.identity()
    password = await ui.password()
    ui.notice("Connecting securely…")
    reader, writer = await connect(arguments.host, arguments.port, name, password, arguments.ca)
    del password
    ui.connected(arguments.host, arguments.port)
    await chat(reader, writer, ui)


async def chat(reader, writer, ui):
    """Run the composer and receiver together, closing both on either exit."""
    with patch_stdout():
        receiver = asyncio.create_task(receive_messages(reader, ui))
        sender = asyncio.create_task(send_messages(writer, ui))
        tasks = {receiver, sender}
        try:
            done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                task.result()
        finally:
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            await close_writer(writer)
    ui.notice("Disconnected. See you on the next signal.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="localhost", help="Server DNS name or IP matching its certificate")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--ca", help="Trusted PEM certificate; omit for a publicly trusted certificate")
    arguments = parser.parse_args()
    try:
        asyncio.run(run_client(arguments))
    except (KeyboardInterrupt, EOFError):
        print("\nDisconnected.")
    except ssl.SSLCertVerificationError:
        parser.exit(1, "Certificate verification failed. Check the server name, certificate expiry, and --ca file.\n")
    except (OSError, AuthenticationError, ProtocolError, ValueError) as error:
        # Server-provided error text must not inject terminal control sequences.
        from chat_ui import clean
        parser.exit(1, f"Could not join: {clean(str(error))}\n")


if __name__ == "__main__":
    main()
