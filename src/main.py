import socket
import time
import signal
import os
import sys
import threading
import atomics


HOST = '127.0.0.1'
PORT = 5555

control=atomics.atomic(width=4, atype=atomics.INT)
control.store(0)

myState="waiting-ID"

def connectServer(clientSocket, uniqueId):
    global control
    while True:
        if control.load()==0:
          requestedId = input('Enter ID: ')
          # send requested ID to the server
          clientSocket.send(requestedId.encode('utf-8'))
          control.store(1)
        else:
            time.sleep(0.1)

def waitingRequest(clientSocket, uniqueId):
     global control
     global myState
     while True:
        # receive server's response
        if control.load()==1:
          try:
            response = clientSocket.recv(1024).decode()
          except:
              continue
          if myState == "idle":
            print("kk")
            if response == "-1":
              print("Could not reach the client")
              control.store(0)
            else:
              answer = input(f'Do you want to connect {response}? (yes/no)')
              clientSocket.send(answer.encode('utf-8'))
        else:
           time.sleep(0.1)


def signalHandler(sig, frame):
    clientSocket.close()
    sys.exit(1)

signal.signal(signal.SIGINT, signalHandler)
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect((HOST, PORT))
clientSocket.settimeout(5)

while True:
    try:
        uniqueId = int(clientSocket.recv(1024).decode())
        myState = "idle"
        print(f"Connected to the server. Assigned ID: {uniqueId}")
        connectServerThread = threading.Thread(target=connectServer, args=(clientSocket, uniqueId))
        waitingRequestThread =threading.Thread(target=waitingRequest, args=(clientSocket, uniqueId))
        connectServerThread.start()
        waitingRequestThread.start()

        break
    except socket.timeout:
        print("Timeout occurred. Connection to the server timed out.")
        break
