# Lesson 2: One thread per client

## Learning outcomes

After this lesson, you should be able to separate connection acceptance from
connection handling, start a worker with arguments, and reason about ownership,
blocking, cleanup, and shared state.

## 1. Why the single-client server stops scaling

`accept()` blocks until a connection arrives. `recv()` blocks until bytes arrive
or the connection ends. If the main server calls `recv()` for client A, it cannot
return to `accept()` while A is idle. New clients wait unnecessarily.

The first concurrency design is:

```text
main thread:    accept -> start worker -> accept -> start worker -> ...
worker thread:  recv from exactly one client until it disconnects
```

This model is easy to understand and suitable for a learning project. It is not
the only model; later you can compare it with `asyncio` and thread pools.

## 2. Functions are values

A thread needs a callable to run later:

```python
worker = threading.Thread(target=handle_client, args=(connection, address))
worker.start()
```

`target=handle_client` passes the function. `target=handle_client()` calls the
function immediately in the current thread and passes its return value, which
is a common beginner mistake.

## 3. Separation of responsibilities

The main thread should:

- own the listening socket;
- accept connections;
- create and start workers;
- eventually coordinate shutdown.

Each worker should:

- own one connected client socket;
- receive until that client disconnects;
- decode and process complete protocol messages;
- catch expected connection errors;
- remove the client from shared state later;
- close its socket exactly once.

This separation keeps the accept loop responsive.

## 4. The handler loop

Write a function with this shape, filling the body yourself:

```python
def handle_client(connection, address):
    with connection:
        while True:
            # receive bytes
            # detect disconnect
            # decode and process data
            ...
```

The function must return when `recv()` yields `b""`. A loop that ignores this
condition can spin forever, consuming CPU.

## 5. Starting threads

After every successful `accept()`:

1. Store both returned values using precise names.
2. Construct a `Thread` whose target is the handler.
3. Pass the connected socket and address through `args`.
4. Call `start()`, not `run()`.
5. Immediately let the main loop call `accept()` again.

Calling `run()` directly executes synchronously in the current thread. Calling
`start()` asks Python to create the new thread, which then invokes your target.

## 6. Daemon versus non-daemon

Non-daemon threads keep the Python process alive until they finish. Daemon
threads are stopped abruptly when only daemon threads remain. Abrupt stopping
can skip cleanup, so begin with non-daemon threads and learn explicit shutdown
later.

Pressing Ctrl-C raises `KeyboardInterrupt` in the main thread. A polished server
will stop accepting, signal workers, close sockets, and join threads. That is a
later milestone; first make connection handling correct.

## 7. Shared state and races

Broadcasting requires a shared collection of connected clients. Multiple
threads may add, remove, or iterate over it. A sequence that looks like one idea
in Python can consist of several operations that interleave with another
thread.

A `threading.Lock` protects an invariant:

```text
acquire lock -> inspect/change shared state -> release lock
```

Do not hold the lock while performing slow network sends if you can first take
a safe snapshot. Otherwise one slow client can delay connection management.

The Global Interpreter Lock does not make your application-level invariants
automatically safe. It is an implementation mechanism, not a replacement for
reasoning about shared mutable state.

## 8. Milestone B: concurrent connections

Starting from the working single-client server:

1. Extract the connected-client code into `handle_client()`.
2. Put `accept()` inside an infinite loop.
3. Start a new thread after every acceptance.
4. Let each client send multiple messages before disconnecting.
5. Test with at least three terminals.

Evidence of completion:

- One idle client does not prevent another client from connecting and sending.
- Disconnecting one client does not stop the server.
- You can explain which thread owns each socket.
- You can explain the difference between `start()` and `run()`.

## 9. Debugging concurrency

Include the client address and current thread name in temporary debug messages.
Reproduce bugs with a written sequence such as "A connects, B connects, A
disconnects while B sends." Random repeated testing is less informative.

Useful questions:

- Which thread is blocked, and on what operation?
- Which object is shared?
- Who owns and closes this socket?
- Can another thread mutate this collection during iteration?
- Does every exit path perform cleanup?

## Self-check

1. Why must the main thread avoid handling the whole client conversation?
2. What is wrong with `target=handle_client()`?
3. Who should close an accepted client socket?
4. Why can a shared list of clients need a lock?
5. Why should a broadcast avoid holding a lock during slow I/O?
