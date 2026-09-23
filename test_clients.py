"""Manual TLS room smoke test: all clients must receive every test message."""

import argparse
import asyncio
import getpass

from framing import ProtocolError, read_frame, send_frame
from transport import AuthenticationError, close_writer, connect


async def run(arguments, password):
    clients = []
    expected = {
        (f"test_{client}", f"message_{message}")
        for client in range(1, arguments.clients + 1)
        for message in range(1, arguments.messages + 1)
    }

    async def send(writer):
        for number in range(1, arguments.messages + 1):
            await send_frame(writer, {"type": "chat", "text": f"message_{number}"})
            await asyncio.sleep(arguments.delay)

    async def receive(reader):
        remaining = set(expected)
        while remaining:
            message = await read_frame(reader)
            if message is None:
                raise RuntimeError("Connection closed before all broadcasts arrived.")
            if message['type'] == 'error':
                raise RuntimeError(message.get('message', 'Server error'))
            if message['type'] == 'chat':
                remaining.discard((message.get('name'), message.get('text')))

    tasks = []
    try:
        for number in range(1, arguments.clients + 1):
            clients.append(await connect(
                arguments.host, arguments.port, f"test_{number}", password, arguments.ca))
        for reader, writer in clients:
            tasks.extend([asyncio.create_task(send(writer)), asyncio.create_task(receive(reader))])
        await asyncio.wait_for(asyncio.gather(*tasks), timeout=30 + arguments.messages * arguments.delay)
        print(f"PASS: all {arguments.clients} clients received all {len(expected)} chat messages over TLS.")
    finally:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        await asyncio.gather(*(close_writer(writer) for _, writer in clients))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', type=int, default=5000)
    parser.add_argument('--ca', help='Trusted server certificate')
    parser.add_argument('--clients', type=int, default=5)
    parser.add_argument('--messages', type=int, default=3)
    parser.add_argument('--delay', type=float, default=.1)
    arguments = parser.parse_args()
    if not 1 <= arguments.clients <= 10 or arguments.messages < 1 or arguments.delay < 0:
        parser.error('Use 1–10 clients, at least one message, and a nonnegative delay.')
    try:
        password = getpass.getpass('Room password: ')
        asyncio.run(run(arguments, password))
    except (OSError, AuthenticationError, ProtocolError, RuntimeError) as error:
        from chat_ui import clean
        parser.exit(1, f"FAIL: {clean(str(error))}\n")
    except (KeyboardInterrupt, EOFError):
        parser.exit(1, '\nCancelled.\n')


if __name__ == '__main__':
    main()
