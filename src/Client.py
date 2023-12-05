import socket
from threading import Thread, Lock
import atomics
import signal
from time import sleep
import select
import sys

from ClientWindow import ClientWindow

SOCKET_TIMEOUT = 5
RECEIVER_THREAD_WAIT = 0.01


class Client:
    def __init__(self, host: str, port: int):
        self.__host = host
        self.__port = port
        self.__id = -1
        self.__state = 'waiting-id'
        self.__mustQuit = atomics.atomic(width=1, atype=atomics.UINT)
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__receiverThread = None
        self.__lock = None
        self.__window = None
        self.__start()

    def __signalHandler(self, sig, frame):
        print('SIGINT received.')
        self.closeClient()

    def __start(self):
        signal.signal(signal.SIGINT, self.__signalHandler)
        self.__socket.connect((self.__host, self.__port))
        self.__socket.settimeout(SOCKET_TIMEOUT)
        self.__mustQuit.store(0)
        self.__window = None
        self.__lock = Lock()
        self.__window = ClientWindow()
        self.__window.registerOnClick(lambda event: self.__onClick())
        self.__window.after(500, self.__check)
        self.__receiverThread = Thread(target=self.__receiver, args=())
        self.__receiverThread.start()
        self.__window.prepare()

    def closeClient(self):
        print(f'[SIGNAL]: Closing the client.')
        for _ in range(3):
            try:
                self.__socket.send('quit'.encode(encoding='utf-8'))
                print(f'[SIGNAL]: Server has been notified.')
                break
            except:
                print(f'Try: {_}')
                if _ == 2:
                    print(f'[SIGNAL]: Error, Server could not be notified.')
                    break

        self.__mustQuit.store(1)
        self.__window.destroy()
        self.__receiverThread.join()
        self.__socket.close()
        exit(0)

    def __check(self):
        self.__window.after(500, self.__check)

    def __onClick(self):
        print(f'[WINDOW]: Hello World')

    def __receiver(self):
        while self.__mustQuit.load() == 0:
            sleep(RECEIVER_THREAD_WAIT)

            try:
                message = self.__socket.recv(1024).decode()
                print(f'[RECEIVER]: Message received: {message}')
            except:
                continue

            if message == 'quit':
                self.__mustQuit.store(1)
                break

            if self.__state == 'waiting-id':
                try:
                    self.__id = int(message)

                except:
                    print('[RECEIVER]: Received ID is invalid. Closing the client')
                    self.closeClient()

                self.__state = 'idle'
                print(
                    f'[RECEIVER]: Connected to the server. Assigned ID: {self.__id}')
                self.__window.setIdLabel(self.__id)

            elif self.__state == 'idle':
                if message == '-1':
                    print('Could not reach the client')

                elif message == '0':
                    pass

                else:
                    print(
                        f'[RECEIVER]: Currently waiting for pop-up to be answered...')
                    answer = self.__window.popup(
                        f'Do you want to connect {message}? (yes/no)', 5)
                    print(f'[RECEIVER]: Pop-up has been answered -> {answer}')
                    if answer == None:
                        self.__socket.send('no'.encode('utf-8'))
                    else:
                        self.__socket.send(answer.encode('utf-8'))
