"""Launch several concurrent clients against the TCP chat server.

Run ``python server.py`` in one terminal, then run this file in another.
This is a manual integration test: client-side results appear here, while the
server terminal shows how the TCP byte stream was divided between recv() calls.
"""

import argparse
import socket
import threading
import time

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 5000


def run_test_client(
    client_id: int,
    host: str,
    port: int,
    message_count: int,
    delay: float,
    start_barrier: threading.Barrier,
) -> tuple[int, bool, str]:
    """Connect one client, wait for its peers, and send identified messages."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.settimeout(5)
            client.connect((host, port))
            print(f"Client {client_id}: connected")

            # All clients begin sending at approximately the same time.
            start_barrier.wait(timeout=5)

            for message_number in range(1, message_count + 1):
                message = f"client={client_id} message={message_number}\n"
                client.sendall(message.encode("utf-8"))
                time.sleep(delay)

        return client_id, True, f"sent {message_count} messages"
    except (OSError, threading.BrokenBarrierError) as error:
        return client_id, False, f"{type(error).__name__}: {error}"


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Connect multiple concurrent test clients to the server."
    )
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--clients", type=int, default=5)
    parser.add_argument("--messages", type=int, default=3)
    parser.add_argument("--delay", type=float, default=0.1)
    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()

    if arguments.clients < 1 or arguments.messages < 1:
        raise SystemExit("--clients and --messages must both be at least 1")
    if arguments.delay < 0:
        raise SystemExit("--delay cannot be negative")

    barrier = threading.Barrier(arguments.clients)
    results: list[tuple[int, bool, str]] = []
    results_lock = threading.Lock()

    def worker(client_id: int) -> None:
        result = run_test_client(
            client_id,
            arguments.host,
            arguments.port,
            arguments.messages,
            arguments.delay,
            barrier,
        )
        with results_lock:
            results.append(result)

    threads = [
        threading.Thread(target=worker, args=(client_id,))
        for client_id in range(1, arguments.clients + 1)
    ]

    print(
        f"Starting {arguments.clients} clients against "
        f"{arguments.host}:{arguments.port}"
    )
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    print("\nResults")
    for client_id, succeeded, detail in sorted(results):
        status = "PASS" if succeeded else "FAIL"
        print(f"{status} client {client_id}: {detail}")

    failures = sum(not succeeded for _, succeeded, _ in results)
    if failures:
        raise SystemExit(f"{failures} client(s) failed")

    print(f"All {arguments.clients} clients completed successfully")


if __name__ == "__main__":
    main()
