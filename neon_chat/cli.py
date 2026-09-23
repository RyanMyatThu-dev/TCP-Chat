"""Create or join a temporary room through the bundled service configuration."""

import argparse
import asyncio
from importlib.resources import as_file, files
import json
import ssl

from chat_ui import ChatUI, clean
from client import chat
from framing import ProtocolError, valid_alias
from room_codes import display_code, normalize_code
from transport import AuthenticationError, authenticate, close_writer
from . import __version__


async def run(arguments, host, port, ca):
    ui = ChatUI()
    ui.welcome()
    name = arguments.name or await ui.identity()
    if not valid_alias(name):
        raise ValueError('Use an alias of 1–24 letters, numbers, underscores, or hyphens.')
    ui.user_name = name
    if arguments.command == 'host':
        request = {'type': 'create', 'name': name}
    else:
        request = {'type': 'join', 'name': name, 'code': normalize_code(arguments.code)}
    ui.notice('Creating your room…' if arguments.command == 'host' else 'Joining your room…')
    reader, writer, response = await authenticate(host, port, request, ca)
    try:
        code = display_code(response.get('code'))
    except ValueError:
        await close_writer(writer)
        raise ProtocolError('The server did not provide a valid room invitation.') from None
    ui.invitation(code, is_host=arguments.command == 'host')
    await chat(reader, writer, ui)


def main():
    parser = argparse.ArgumentParser(
        prog='neon-chat', description='Private terminal rooms. Create one, share its code, and chat.')
    parser.add_argument('--version', action='version', version=f'neon-chat {__version__}')
    commands = parser.add_subparsers(dest='command', required=True)
    for command, help_text in [('host', 'Create a room and receive an invitation code'),
                               ('join', 'Join a room using its invitation code')]:
        sub = commands.add_parser(command, help=help_text)
        if command == 'join':
            sub.add_argument('code', help='Room code, for example XXXX-XXXX-XXXX')
        sub.add_argument('--name', help='Your display name; prompted when omitted')
        sub.add_argument('--server', help=argparse.SUPPRESS)
        sub.add_argument('--port', type=int, help=argparse.SUPPRESS)
        sub.add_argument('--ca', help=argparse.SUPPRESS)
    arguments = parser.parse_args()
    try:
        if arguments.command == 'join':
            arguments.code = normalize_code(arguments.code)
        settings = json.loads(files('neon_chat').joinpath('service.json').read_text())
        host = arguments.server or settings['host']
        port = arguments.port or settings['port']
        if not host:
            raise ValueError('This build has no service configured. Contact the server operator.')
        # Trust travels with the installed package; never disable TLS verification.
        with as_file(files('neon_chat').joinpath('service-ca.crt')) as bundled_ca:
            asyncio.run(run(arguments, host, port, arguments.ca or str(bundled_ca)))
    except (KeyboardInterrupt, EOFError):
        print('\nDisconnected.')
    except ssl.SSLCertVerificationError:
        parser.exit(1, 'Could not verify the chat server. Update neon-chat or contact the host.\n')
    except (ConnectionError, TimeoutError):
        parser.exit(1, 'The chat server is offline or unreachable. Ask the operator to start it, then retry.\n')
    except (OSError, AuthenticationError, ProtocolError, ValueError) as error:
        parser.exit(1, f'Could not join: {clean(str(error))}\n')
