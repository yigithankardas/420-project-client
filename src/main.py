import socket
import time
import signal
import os
import sys

HOST = '127.0.0.1'
PORT = 5555


def connectServer():
    while True:
        print(f'doing stuff with {uniqueId}')
        time.sleep(1)


if __name__ == "__main__":
    def signalHandler(signal, frame):
        clientSocket.close()
        sys.exit(1)

    signal.signal(signal.SIGINT, signalHandler)
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((HOST, PORT))

    clientSocket.settimeout(5)
    try:
        uniqueId = int(clientSocket.recv(1024).decode())
        print(f"Connected to the server. Assigned ID: {uniqueId}")
        connectServer()

    except socket.timeout:
        print("Timeout occurred. Connection to the server timed out.")

    finally:
        clientSocket.close()
