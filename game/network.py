import socket
import threading

class NetworkClient:
    def __init__(self, host='127.0.0.1', port=5555):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))
        threading.Thread(target=self.receive).start()

    def send(self, data):
        self.client.send(data.encode())

    def receive(self):
        while True:
            data = self.client.recv(1024)
            print("Received:", data.decode())
