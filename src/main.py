import socket
import time

# Server ayarları
HOST = '127.0.0.1'
PORT = 5555

def connect_to_server():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    # Timeout'u 5 saniye olarak ayarla.
    # Client'a ID server tarafından 5 saniye içinde atılmalı. 
    client_socket.settimeout(5)

    try:
        # Server tarafından atanan ID'yi al
        unique_id = int(client_socket.recv(1024).decode())
        print(f"Connected to the server. Assigned ID: {unique_id}")

        while True:
            # Burada bağlı kalındığı sürece işlemleri gerçekleştirebilirsiniz
            pass

    except socket.timeout:
        # timeout içerisinde ID atanmamışsa error mesajı bastır.
        print("Timeout occurred. Connection to the server timed out.")
    except KeyboardInterrupt:
        print("Client is exiting...")
    finally:
        # Bağlantıyı kapat
        client_socket.close()

if __name__ == "__main__":
    connect_to_server()
