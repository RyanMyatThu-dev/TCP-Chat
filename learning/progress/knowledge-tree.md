# TCP Chat Knowledge Tree

Updated: 2026-09-22

## How to use this tree

Check a box only after producing the stated evidence. Use `[~]` for in progress,
`[x]` for demonstrated, and `[ ]` for not started. Add links to commits, terminal
transcripts, tests, or learning-log entries where useful.

## 0. Tooling foundations

- [~] Terminal workflow
  - [x] Run Python files from the shell
  - [ ] Manage two or more terminal sessions for server/client testing
  - [ ] Explain exit status and read a traceback from bottom to top
- [~] Vim workflow
  - [x] Open, edit, save, and quit a file
  - [ ] Navigate and edit comfortably without arrow-key dependence
  - [ ] Search, replace, undo, copy, paste, and use splits
- [ ] Git workflow
  - [ ] Initialize repository and make an intentional first commit
  - [ ] Inspect diffs before committing
  - [ ] Use small milestone commits with meaningful messages

## 1. Python foundations

- [~] Functions and control flow
  - [x] Define and call a function
  - [ ] Explain `if __name__ == "__main__"`
  - [ ] Use loops with clear termination conditions
- [~] Data representation
  - [ ] Explain `str` versus `bytes`
  - [ ] Encode and decode UTF-8 at system boundaries
  - [ ] Explain tuples and argument unpacking
- [ ] Resource management
  - [ ] Use `with` to guarantee socket cleanup
  - [ ] Explain exception propagation and `try/finally`

## 2. Networking foundations

- [~] TCP mental model
  - [ ] Explain client, server, host, port, and endpoint
  - [ ] Explain what TCP guarantees and what it does not
  - [ ] Explain why TCP is a byte stream without message boundaries
- [~] Socket lifecycle
  - [ ] Implement `socket -> bind -> listen -> accept`
  - [ ] Implement `socket -> connect`
  - [ ] Send with `sendall()` and receive with `recv()`
  - [ ] Detect orderly disconnect through `b""`
- [ ] Failure diagnosis
  - [ ] Reproduce and explain `ConnectionRefusedError`
  - [ ] Reproduce and explain address/port mismatch
  - [ ] Identify which blocking call is waiting

## 3. Concurrency foundations

- [ ] Thread model
  - [ ] Explain process versus thread
  - [ ] Pass a callable and arguments to `Thread`
  - [ ] Explain `start()` versus `run()`
- [ ] Thread-per-client server
  - [ ] Keep acceptance in the main thread
  - [ ] Handle each connected socket in one worker
  - [ ] Demonstrate three simultaneous connections
  - [ ] Disconnect one client without affecting others
- [ ] Shared-state safety
  - [ ] Identify the shared client collection
  - [ ] State the invariant protected by a lock
  - [ ] Broadcast from a safe snapshot
  - [ ] Explain one possible race condition

## 4. Chat protocol

- [ ] Framing
  - [ ] Demonstrate that `sendall()` and `recv()` boundaries can differ
  - [ ] Implement newline-delimited or length-prefixed messages
  - [ ] Buffer incomplete frames correctly
- [ ] Message semantics
  - [ ] Design join, chat, leave, and error messages
  - [ ] Validate malformed input without crashing the server
  - [ ] Document encoding and maximum message size
- [ ] Identity
  - [ ] Accept and validate usernames
  - [ ] Handle duplicate usernames deliberately

## 5. Reliability and testing

- [ ] Error handling and cleanup
  - [ ] Handle abrupt client disconnects
  - [ ] Remove dead sockets from shared state
  - [ ] Shut down server and workers deliberately
- [ ] Automated tests
  - [ ] Unit-test protocol encoding and parsing
  - [ ] Integration-test server/client communication
  - [ ] Test two concurrent clients without manual typing
- [ ] Observability
  - [ ] Replace temporary prints with structured logging
  - [ ] Include useful connection context without leaking message contents

## 6. CLI and packaging

- [ ] Command-line interface
  - [ ] Parse server host and port
  - [ ] Parse client host, port, and username
  - [ ] Provide helpful `--help` output and validation
- [ ] Package structure
  - [ ] Move code into `src/tcp_chat/`
  - [ ] Create `pyproject.toml`
  - [ ] Expose a `tcp-chat` console command
- [ ] Installation and release
  - [ ] Install locally in an isolated environment
  - [ ] Build wheel and source distribution
  - [ ] Install and smoke-test the built wheel

## 7. Stretch branches

- [ ] Compare thread-per-client with `asyncio`
- [ ] Add chat rooms and private messages
- [ ] Add TLS and explain authentication versus encryption
- [ ] Measure behavior with many idle connections

## Current focus

Milestone A: implement and explain a one-client TCP exchange. Do not begin the
threaded implementation until the three evidence items in Lesson 1 are met.
