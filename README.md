# TCP Chat Learning Project

This repository is both a Python project and a personal networking course. The
goal is to understand every line, type the implementation yourself in Vim, and
keep evidence of what you can explain and demonstrate.

## Start here

1. Read `learning/lessons/01-sockets.md`.
2. Open `server.py` and `client.py` side by side.
3. Complete one TODO at a time and test after every small change.
4. Update `learning/progress/knowledge-tree.md` only when you meet its evidence
   requirement.
5. Record bugs and discoveries in `learning/progress/learning-log.md`.

## Repository map

```text
.
|-- server.py                         learner-owned implementation
|-- client.py                         learner-owned implementation
|-- learning/
|   |-- lessons/                      editable source notes
|   |-- progress/knowledge-tree.md    mastery map
|   `-- progress/learning-log.md      dated learning evidence
|-- output/pdf/                       generated handbook
`-- tools/build_learning_guide.py     rebuilds the PDF from Markdown
```

## Useful commands

```bash
vim server.py
python server.py
python client.py
python -m py_compile server.py client.py
python tools/build_learning_guide.py
```

Run the server in one terminal and clients in other terminals. Use
`127.0.0.1`, not `0.0.0.0`, as the client destination during local testing.

## Client appearance

The client uses a neon cyan and magenta terminal theme with an alias prompt,
local receive timestamps, highlighted senders, and a compact status bar on
compatible terminals. Enter sends a message; Up/Down recalls input history.
Incoming messages redraw above the active prompt so you can keep typing.

Presentation lives in `chat_ui.py` and uses the existing `prompt_toolkit`
dependency (`python -m pip install prompt_toolkit` if needed). Set `NO_COLOR=1`
for monochrome output. Socket behavior and the wire format are unchanged.

## Learning agreement

- Attempt each milestone before asking for a full solution.
- Ask for hints, explanations, debugging, or code review freely.
- Never mark a skill complete solely because the program happened to run.
- Prefer small working changes over a large untested rewrite.
- Explain your code aloud after each milestone.
