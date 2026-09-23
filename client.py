"""TCP chat client - learner starter."""

import socket
import threading
from prompt_toolkit.patch_stdout import patch_stdout
from chat_ui import ChatUI

HOST = "127.0.0.1"
PORT = 5000
BUFFER_SIZE = 1024
ui = ChatUI()
user_name = ""

def receive_message(connection):
    with connection:
        while True:
            message = connection.recv(BUFFER_SIZE).decode()
            ui.message(message)


def run_client():
    ui.welcome()
    user_name = ui.identity()
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((HOST, PORT))
        ui.connected(HOST, PORT)
        client.sendall(user_name.encode())
        receiver_thread = threading.Thread(target=receive_message, args=(client,))
        receiver_thread.start()
        with patch_stdout():
            while True:
                user_input = ui.compose()
                client.sendall(user_input.encode())
if __name__ == "__main__":
    run_client()
