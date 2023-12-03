if __name__ != '__main__':
    raise ImportError('This module cannot be imported from outside.')

import socket
from time import sleep
import signal
import sys
from threading import Thread, Lock
import atomics
import select

HOST = '127.0.0.1'
PORT = 5555

lockSender = atomics.atomic(width=1, atype=atomics.UINT)
lockSender.store(0)
cancelSender = atomics.atomic(width=1, atype=atomics.UINT)
cancelSender.store(0)
mustQuit = atomics.atomic(width=1, atype=atomics.UINT)
mustQuit.store(0)

state = 'waiting-id'


def sender(clientSocket, uniqueId):
    global lockSender
    global cancelSender

    while True:
        sleep(0.01)

        if mustQuit.load() == 1:
            break

        if lockSender.load() == 1:
            continue

        print('Enter ID: ', end='')
        requestedId = input()
        if cancelSender.load() == 0:
            clientSocket.send(requestedId.encode('utf-8'))
        lockSender.store(1)


def receiver(clientSocket, uniqueId):
    global lockSender
    global cancelSender
    global state

    while True:
        sleep(0.01)

        if mustQuit.load() == 1:
            lockSender.store(0)
            cancelSender.store(0)
            break

        try:
            response = clientSocket.recv(1024).decode()
            lockSender.store(1)
            cancelSender.store(1)
            print('--> (WILL BE CANCELED)')
        except:
            continue

        if response == 'quit':
            mustQuit.store(1)
            continue

        if state == 'idle':
            if response == '-1':
                print('Could not reach the client')
                lockSender.store(0)

            elif response == '0':
                lockSender.store(0)

            else:
                print(f'Do you want to connect {response}? (yes/no)')
                answer = input()
                clientSocket.send(answer.encode('utf-8'))
                if answer == 'no':
                    lockSender.store(0)


def signalHandler(sig, frame):
    try:
        senderThread.join(2)
        receiverThread.join(2)
        clientSocket.close()
    except:
        clientSocket.close()

    exit(1)


signal.signal(signal.SIGINT, signalHandler)

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect((HOST, PORT))
clientSocket.settimeout(5)

try:
    uniqueId = int(clientSocket.recv(1024).decode())
except socket.timeout:
    print('Timeout occurred. Connection to the server timed out.')
    exit(1)

state = 'idle'
print(f'Connected to the server. Assigned ID: {uniqueId}')

args = (clientSocket, uniqueId)
senderThread = Thread(target=receiver, args=args)
senderThread.start()
receiverThread = Thread(target=sender, args=args)
receiverThread.start()

while True:
    sleep(1)
