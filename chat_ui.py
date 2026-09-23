"""Presentation only: terminal styling and prompts for the TCP chat client."""

import os
from datetime import datetime
from shutil import get_terminal_size

from prompt_toolkit import PromptSession, print_formatted_text
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.output import ColorDepth
from prompt_toolkit.styles import Style


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
        self.session = PromptSession(style=STYLE)
        self.user_name = ""
        self.endpoint = ""
        self.color = "NO_COLOR" not in os.environ

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

    def identity(self):
        self.user_name = self.session.prompt(
            FormattedText([("class:accent", "  alias "), ("class:prompt", "› ")])
        )
        return self.user_name

    def connected(self, host, port):
        self.endpoint = f"{host}:{port}"
        print()
        self.rule()
        self.write(("class:success", "  ● ONLINE  "),
                   ("class:text", self.endpoint),
                   ("class:muted", "  /  "),
                   ("class:accent", clean(self.user_name)))
        self.write(("class:muted", "  Type a message below. Press Enter to send."))
        self.rule()
        print()

    def toolbar(self):
        # Keep the toolbar readable even in a narrow terminal.
        if self.session.output.get_size().columns < 60:
            return FormattedText([("class:bottom-toolbar.key", " ● ONLINE "),
                                  ("", " Enter · send ")])
        return FormattedText([
            ("class:bottom-toolbar.key", " ● ONLINE "),
            ("", f" {self.endpoint}  │  "),
            ("class:bottom-toolbar.key", "ENTER"), ("", " send  │  "),
            ("class:bottom-toolbar.key", "↑ / ↓"), ("", " history"),
        ])

    def compose(self):
        # The server echo supplies the transcript entry; clear the composer.
        self.session.app.erase_when_done = True
        return self.session.prompt(
            FormattedText([("class:muted", "  you "), ("class:prompt", "❯ ")]),
            bottom_toolbar=self.toolbar if self.session.output.responds_to_cpr else None,
            prompt_continuation=lambda width, line, soft_wrap: " " * width,
        )

    def message(self, message):
        if not message:
            return  # Nothing to render; connection handling stays in the client.
        timestamp = datetime.now().strftime("%H:%M")
        sender, separator, body = clean(message).partition(" : ")
        prefix = [("class:muted", f"  {timestamp}  ")]
        if separator:
            own = sender == clean(self.user_name)
            self.write(*prefix,
                       ("class:accent" if own else "class:brand", sender),
                       ("class:muted", "  ›  "),
                       ("class:text", body.replace("\n", "\n         ")))
        else:
            self.write(*prefix, ("class:success", "◇  "),
                       ("class:muted", clean(message)))
