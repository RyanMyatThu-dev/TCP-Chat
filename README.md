# NEON / CHAT

A Python TCP chat app with a neo-cyberpunk terminal interface. Connect multiple
clients, choose an alias, and chat in a shared room with cyan and magenta accents.

```text
  ◈  NEON / CHAT    TCP TERMINAL
     A little signal in the noise.
────────────────────────────────────────────────────────
  ● ONLINE  127.0.0.1:5000  /  Raven

  21:31  ◇  Nova has joined the chat
  21:31  Raven  ›  Anyone out there?
  21:31  Nova   ›  Loud and clear.

  you ❯
```

*Illustrative terminal preview; colors depend on your terminal.*

## Features

- **Shared chat:** the server broadcasts messages to connected clients, including
  the sender.
- **User aliases:** choose a display name before entering the room.
- **Presence notices:** see when someone joins or when the server detects a
  closed connection.
- **Neon interface:** styled welcome screen, highlighted senders, local receive
  timestamps, and a compact status bar on compatible terminals.
- **Live input:** incoming messages appear above the composer while you type.
  Submitted input clears so the server echo supplies a single transcript entry.
- **Input history:** use Up/Down to recall earlier input and Enter to send.
- **Monochrome option:** launch with `NO_COLOR=1 python client.py`.

## Run locally

You need Python 3 and `prompt_toolkit`. From the project directory:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install prompt_toolkit
python server.py
```

In another terminal, activate the same environment and start a client:

```bash
source .venv/bin/activate
python client.py
```

Repeat in additional terminals to chat between clients. Both server and client
currently use `127.0.0.1:5000`, so this setup runs on one machine.

## Our development process

We are building the app in small steps, starting with the networking fundamentals
and then improving the experience around them.

| Stage | What we built | Progress |
| --- | --- | --- |
| TCP foundation | Socket connection, sending bytes, and receiving text | Implemented |
| Multiple clients | Server threads, a shared client registry, and broadcast messages | Implemented |
| Room identity | Aliases and join/leave notices | Implemented |
| Terminal design | Separate UI module, neon theme, timestamps, and message composer | Implemented |
| Visual refinement | Clear submitted input to avoid showing it twice | Implemented |
| Protocol reliability | Message framing and more robust connection handling | Still to build |

The interface lives in `chat_ui.py`, keeping presentation separate from the
socket operations in `client.py`. The visual updates and duplicate-input fix
preserved the existing socket and threading calls. Prompt/rendering smoke checks
and Python compilation were used to check those changes.

We keep supporting learning notes in [learning/lessons](learning/lessons), with a
[development log](learning/progress/learning-log.md) and a
[knowledge tracker](learning/progress/knowledge-tree.md).

## Current limitations

This is an early local chat prototype. TCP message framing is not implemented:
messages can be split or combined across reads, particularly with long or rapid
messages. Graceful client shutdown, reconnection, and network-error handling
also need work. Aliases are display names; there is no account authentication,
transport encryption, or saved chat history.

## Project layout

```text
client.py        Connection setup, sending, and background receiving
server.py        Client registry, threaded handlers, and broadcasting
chat_ui.py       Terminal theme, prompts, and message rendering
framing.py       Placeholder for future message framing
learning/        Networking lessons and progress notes
tools/           Learning-guide generation scripts
```

For a quick syntax check:

```bash
python -m py_compile server.py client.py chat_ui.py
```
