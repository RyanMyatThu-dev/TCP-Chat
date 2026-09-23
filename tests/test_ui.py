"""Input privacy and composer lifecycle checks without a live terminal."""

import asyncio
import unittest
from unittest.mock import patch

from prompt_toolkit.application import create_app_session
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.output import DummyOutput

from chat_ui import ChatUI
from framing import MAX_MESSAGE_BYTES, valid_text


class RecordingOutput(DummyOutput):
    def __init__(self):
        self.text = []

    def write(self, data):
        self.text.append(data)

    def write_raw(self, data):
        self.text.append(data)


class UITests(unittest.IsolatedAsyncioTestCase):
    async def test_masked_password_history_and_single_submission(self):
        output = RecordingOutput()
        with create_pipe_input() as pipe, create_app_session(input=pipe, output=output):
            ui = ChatUI()
            loop = asyncio.get_running_loop()
            loop.call_later(.02, pipe.send_text, 'Raven\n')
            self.assertEqual(await ui.identity(), 'Raven')
            loop.call_later(.02, pipe.send_text, 'a-secret-room-password\n')
            self.assertEqual(await ui.password(), 'a-secret-room-password')
            loop.call_later(.02, pipe.send_text, 'hello world\n')
            self.assertEqual(await ui.compose(), 'hello world')
            self.assertEqual(ui.session.history.get_strings(), ['hello world'])
            self.assertTrue(ui.session.app.erase_when_done)
            self.assertNotIn('a-secret-room-password', ''.join(output.text))
            with patch('chat_ui.print_formatted_text') as render:
                ui.message('Raven', 'hello world')
                self.assertEqual(render.call_count, 1)
                rendered = ''.join(text for _, text in render.call_args.args[0])
                self.assertEqual(rendered.count('hello world'), 1)

    async def test_cancel_active_composer(self):
        with create_pipe_input() as pipe, create_app_session(input=pipe, output=DummyOutput()):
            ui = ChatUI()
            task = asyncio.create_task(ui.compose())
            await asyncio.sleep(.02)
            task.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await task
            self.assertFalse(ui.session.app.is_running)

    def test_utf8_byte_limit(self):
        self.assertTrue(valid_text('🌃' * (MAX_MESSAGE_BYTES // 4)))
        self.assertFalse(valid_text('🌃' * (MAX_MESSAGE_BYTES // 4 + 1)))
