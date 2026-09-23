import socket
import threading
HOST = "127.0.0.1"
PORT = 5000
BUFFER_SIZE = 1024

connected_clients = {}
lock = threading.Lock()

def broadcast(message):
    lock.acquire()
    for client, name in connected_clients.items():
        client.sendall(message.encode())
    lock.release()

def handle_client(connection, address):
    with connection:
        while True:
            message = connection.recv(BUFFER_SIZE).decode()
            if not message:
                lock.acquire()
                disconnected_user = connected_clients[connection]
                connected_clients.pop(connection)
                lock.release()
                broadcast(f"{disconnected_user} has left the chat")
                break
            lock.acquire()
            from_user = connected_clients[connection]
            print(f"Message received from {from_user}")
            lock.release()
            broadcast(f"{from_user} : {message}")


def run_server() :
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen(5)
        while True:
            (newConnection, address) = server.accept()
            lock.acquire()
            name = newConnection.recv(BUFFER_SIZE).decode()
            connected_clients[newConnection] = name
            lock.release()
            broadcast(f"{name} has joined the chat")
            thread = threading.Thread(target=handle_client, args=(newConnection,address,))
            thread.start()
            
if __name__ == "__main__":
    run_server()
