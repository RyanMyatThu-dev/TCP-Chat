"""Presentation only: terminal styling and prompts for the TCP chat client."""

import os
from datetime import datetime
from shutil import get_terminal_size

from prompt_toolkit import PromptSession, print_formatted_text
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.history import DummyHistory
from prompt_toolkit.output import ColorDepth
from prompt_toolkit.styles import Style
from prompt_toolkit.validation import Validator

from framing import valid_alias


STYLE = Style.from_dict({
    "brand": "#00e5ff bold",
    "accent": "#ff5fd7 bold",
    "muted": "#8995ad",
    "text": "#e5eaf5",
    "success": "#8affc1",
    "prompt": "#00e5ff bold",
    "bottom-toolbar": "bg:#151c30 #a6b2cc",
    "bottom-toolbar.key": "bg:#151c30 #00e5ff bold",
})


def clean(text):
    """Keep terminal control characters out of displayed user content."""
    return "".join(c if c.isprintable() or c == "\n" else " " for c in text)


class ChatUI:
    def __init__(self):
        self.color = "NO_COLOR" not in os.environ
        self.session = PromptSession(
            style=STYLE, erase_when_done=True,
            color_depth=None if self.color else ColorDepth.DEPTH_1_BIT,
        )
        self.user_name = ""
        self.endpoint = ""

    def write(self, *fragments):
        print_formatted_text(
            FormattedText(list(fragments)), style=STYLE,
            color_depth=None if self.color else ColorDepth.DEPTH_1_BIT,
        )

    def rule(self):
        width = max(1, min(get_terminal_size().columns - 2, 76))
        self.write(("class:muted", "─" * width))

    def welcome(self):
        print()
        self.rule()
        self.write(("class:accent", "  ◈  "), ("class:brand", "NEON / CHAT"),
                   ("class:muted", "    TCP TERMINAL"))
        self.write(("class:muted", "     A little signal in the noise."))
        self.rule()
        print()
        self.write(("class:accent", "  01 / IDENTITY"))
        self.write(("class:muted", "  Choose the name others will see in chat.\n"))

    async def identity(self):
        identity_session = PromptSession(
            style=STYLE, history=DummyHistory(), erase_when_done=True,
            color_depth=None if self.color else ColorDepth.DEPTH_1_BIT,
        )
        self.user_name = await identity_session.prompt_async(
            FormattedText([("class:accent", "  alias "), ("class:prompt", "› ")]),
            validator=Validator.from_callable(
                valid_alias, error_message="Use 1–24 letters, numbers, underscores, or hyphens."
            ),
        )
        return self.user_name

    async def password(self):
        # A separate, history-free prompt prevents password recall in chat.
        password_session = PromptSession(
            style=STYLE, history=DummyHistory(), erase_when_done=True,
            color_depth=None if self.color else ColorDepth.DEPTH_1_BIT,
        )
        return await password_session.prompt_async(
            FormattedText([("class:accent", "  room password "), ("class:prompt", "› ")]),
            is_password=True,
        )

    def connected(self, host, port):
        self.endpoint = f"{host}:{port}"
        print()
        self.rule()
        self.write(("class:success", "  ● ONLINE / TLS  "),
                   ("class:text", self.endpoint),
                   ("class:muted", "  /  "),
                   ("class:accent", clean(self.user_name)))
        self.write(("class:muted", "  Enter to send · /quit or Ctrl+D to leave."))
        self.rule()
        print()

    def toolbar(self):
        # Keep the toolbar readable even in a narrow terminal.
        if self.session.output.get_size().columns < 60:
            return FormattedText([("class:bottom-toolbar.key", " ● TLS "),
                                  ("", " Enter · send ")])
        return FormattedText([
            ("class:bottom-toolbar.key", " ● TLS "),
            ("", f" {self.endpoint}  │  "),
            ("class:bottom-toolbar.key", "ENTER"), ("", " send  │  "),
            ("class:bottom-toolbar.key", "/quit"), ("", " leave"),
        ])

    async def compose(self):
        # The server echo supplies the transcript entry; clear the composer.
        self.session.app.erase_when_done = True
        return await self.session.prompt_async(
            FormattedText([("class:muted", "  you "), ("class:prompt", "❯ ")]),
            bottom_toolbar=self.toolbar if self.session.output.responds_to_cpr else None,
            prompt_continuation=lambda width, line, soft_wrap: " " * width,
            validator=None,
        )

    def message(self, sender, body):
        timestamp = datetime.now().strftime("%H:%M")
        own = sender == self.user_name
        self.write(("class:muted", f"  {timestamp}  "),
                   ("class:accent" if own else "class:brand", clean(sender)),
                   ("class:muted", "  ›  "),
                   ("class:text", clean(body).replace("\n", "\n         ")))

    def notice(self, message):
        timestamp = datetime.now().strftime("%H:%M")
        self.write(("class:muted", f"  {timestamp}  "),
                   ("class:success", "◇  "), ("class:muted", clean(message)))
