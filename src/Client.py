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
        self.__isSendingPrevented = atomics.atomic(width=1, atype=atomics.UINT)
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__receiverThread = None
        self.__window = None

    def __signalHandler(self, sig, frame):
        print('\n[MAIN]: SIGINT received.')
        self.closeClient(informServer=True)

    def process(self):
        signal.signal(signal.SIGINT, self.__signalHandler)
        self.__socket.connect((self.__host, self.__port))
        self.__socket.settimeout(SOCKET_TIMEOUT)
        self.__mustQuit.store(0)
        self.__isSendingPrevented.store(0)
        self.__window = None
        self.__window = ClientWindow()
        self.__window.registerOnClick(lambda event: self.__onClick())
        self.__window.after(500, self.__check)
        self.__receiverThread = Thread(target=self.__receiver, args=())
        self.__receiverThread.start()
        self.__window.mainloop()
        self.__window.destroy()
        self.__receiverThread.join()
        self.__socket.close()
        exit(0)

    def closeClient(self, informServer):
        print(f'[SIGNAL]: Closing the client.')
        self.__mustQuit.store(1)
        if informServer:
            for _ in range(3):
                try:
                    self.__socket.send('quit'.encode(encoding='utf-8'))
                    print(f'[SIGNAL]: Server has been notified.')
                    break
                except:
                    print(f'Try: {_}')
                    if _ == 2:
                        print(
                            f'[SIGNAL]: Error, Server could not be notified. Force shutting down.')
                        break

        self.__window.quit()

    def __check(self):
        self.__window.after(500, self.__check)

    def __onClick(self):
        if self.__isSendingPrevented.load() == 1:
            print(
                f'[WINDOW]: Sending is restricted. __isSendingPrevented: {self.__isSendingPrevented.load()}')
            return

        requestedId = self.__window.getEntryText()
        try:
            self.__socket.send(requestedId.encode('utf-8'))
            print('[WINDOW]: Message has been successfuly sent.')
            self.__isSendingPrevented.store(1)
        except:
            print('[WINDOW]: Message could not be sent.')

    def __receiver(self):
        messages = []
        while self.__mustQuit.load() == 0:
            sleep(RECEIVER_THREAD_WAIT)
            print(f'[RECEIVER]: Receiver thread is idle.')

            try:
                bytes = self.__socket.recv(1024).decode()
                if bytes == '':
                    continue

                messages += list(filter(None, bytes.split('\0')))

                print(f'[RECEIVER]: Messages received: {messages}')
            except:
                if len(messages) == 0:
                    continue

            message = messages.pop(0)

            if message == 'quit':
                self.closeClient(informServer=False)
                break

            if self.__state == 'waiting-id':
                try:
                    self.__id = int(message)
                except:
                    print(
                        '[RECEIVER]: Received ID is invalid. Closing the client')
                    self.closeClient(informServer=True)
                    break

                self.__state = 'idle'
                print(
                    f'[RECEIVER]: Connected to the server. Assigned ID: {self.__id}')
                self.__window.setIdLabel(self.__id)

            elif self.__state == 'idle':
                if message == '-1':
                    print('[RECEIVER]: Could not reach the client')
                    self.__isSendingPrevented.store(0)

                elif message == '-2':
                    print(
                        f'[RECEIVER]: Server did not accept the format of the ID.')
                    self.__isSendingPrevented.store(0)

                elif "newID" in message:
                    newId = message[message.index('-') + 1:]
                    print(f'[RECEIVER]: ID has been replaced by {newId}')
                    self.__id = newId
                    self.__window.setIdLabel(self.__id)

                else:
                    print(
                        f'[RECEIVER]: Currently waiting for pop-up to be answered...')
                    answer = self.__window.popup(
                        f'Do you want to connect {message}? (yes/no)', 5000)
                    print(
                        f'[RECEIVER]: Pop-up has been answered -> {answer}')

                    if answer == None:
                        self.__socket.send('no'.encode('utf-8'))

                    else:
                        self.__socket.send(answer.encode('utf-8'))

                    self.__isSendingPrevented.store(0)
