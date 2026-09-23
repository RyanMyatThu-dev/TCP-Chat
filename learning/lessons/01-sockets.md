# Lesson 1: TCP and Python sockets

## Learning outcomes

After this lesson, you should be able to explain the client-server relationship,
build a one-client TCP exchange, and diagnose common address and byte/string
mistakes.

## 1. The mental model

A network application has two endpoints. The server owns a known address and
waits. The client starts a connection to that address. Once connected, both
sides possess a socket representing one endpoint of a full-duplex byte stream.

TCP provides:

- reliable, ordered delivery of bytes;
- duplicate suppression;
- flow and congestion control;
- a connection with a beginning and an end.

TCP does not provide messages. If one side calls `sendall()` twice, the other
side might receive those bytes in one `recv()` call or several calls. Message
boundaries must eventually be designed by your application protocol.

## 2. Addresses and ports

An IPv4 endpoint is commonly represented as `(host, port)`.

- `127.0.0.1` is loopback: only this computer can reach it.
- `0.0.0.0` is a server bind address meaning all local interfaces. It is not a
  useful destination for a client.
- A port identifies the receiving application on a host.
- Ports below 1024 commonly require elevated privileges; use 5000 while
  learning.

The server binds. The client connects. These are different roles.

## 3. Socket vocabulary

`socket.AF_INET` selects IPv4. `socket.SOCK_STREAM` selects a reliable byte
stream, which normally means TCP.

Server lifecycle:

```text
socket -> bind -> listen -> accept -> recv/send -> close
```

Client lifecycle:

```text
socket -> connect -> send/recv -> close
```

`accept()` does not reuse the listening socket for conversation. It returns a
new connected socket and the client's address. The listening socket remains
available to accept future connections.

## 4. Bytes versus text

Sockets carry bytes. Python's `input()` returns text (`str`). Convert at the
boundary:

```python
outgoing_bytes = message.encode("utf-8")
incoming_text = data.decode("utf-8")
```

Keep data as bytes while transporting it and decode only when the application
needs text. UTF-8 should be explicit when you first learn the conversion.

`sendall(data)` continues sending until all bytes have been handed to the
operating system or an error occurs. `send(data)` may send only part of a large
buffer.

`recv(1024)` means "receive up to 1024 bytes." It may return fewer. When it
returns `b""`, the peer has closed its sending side and the receive loop should
end.

## 5. Resource ownership

Sockets consume operating-system resources. A context manager closes a socket
even when an exception occurs:

```python
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    # use sock
    ...
```

The code that accepts a connected socket must decide who owns and closes it.
Once worker threads are introduced, the worker should normally own that client
socket.

## 6. Milestone A: one exchange

Implement this without threads:

1. Server creates, binds, and listens.
2. Client connects.
3. Client reads one line from the user and sends its UTF-8 bytes.
4. Server accepts once, receives once, decodes, and prints.
5. Both programs close cleanly.

Evidence of completion:

- You can run the server and client from separate terminals.
- You can explain why the socket passed to `recv()` is not the listening socket.
- You can explain why `decode()` belongs after `recv()`.

## 7. Experiments

Change one thing at a time and predict the result before running it:

1. Start the client while the server is stopped.
2. Run two clients when the server accepts only once.
3. Bind the server to a different port without changing the client.
4. Send an empty string.
5. Remove the server's `decode()` and inspect the printed value.

Record the exception names and explanations in the learning log.

## 8. Common failures

- `ConnectionRefusedError`: nothing is listening at the requested endpoint.
- `OSError: address already in use`: another process owns the port, or a recent
  connection is still being cleaned up.
- Program appears frozen: blocking calls such as `accept()` and `recv()` are
  waiting; determine which event would allow progress.
- Garbled or failed decoding: sender and receiver disagree about the encoding,
  or a future protocol split a multi-byte character incorrectly.

## Self-check

Answer without looking:

1. What does `listen()` change about a socket?
2. Why does `accept()` return another socket?
3. What exactly is guaranteed by TCP?
4. Is one `sendall()` guaranteed to equal one `recv()`?
5. What does `b""` from `recv()` mean?
