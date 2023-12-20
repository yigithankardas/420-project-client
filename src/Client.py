import socket
from threading import Thread
import atomics
import signal
from time import sleep
import random
import pickle
import sys

from ClientWindow import ClientWindow
from AESCipher import AESCipher
from tkinter import messagebox

SOCKET_TIMEOUT = 0.5
RECEIVER_THREAD_WAIT = 0.01


class Client:
    def __init__(self, host: str, port: int):
        self.__host = host
        self.__port = port
        self.__id = -1
        self.__p = -1
        self.__g = -1
        self.__privateKey = -1
        self.__sessionKey = -1
        self.__state = 'waiting-id'
        self.__mustQuit = atomics.atomic(width=1, atype=atomics.UINT)
        self.__isSendingPrevented = atomics.atomic(width=1, atype=atomics.UINT)
        self.__canRead = atomics.atomic(width=1, atype=atomics.UINT)
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__receiverThread = None
        self.__window = None

    def __signalHandler(self, sig, frame):
        print('\n[MAIN]: SIGINT received.')
        self.closeClient(informServer=True)

    def __generatePrivateKey(self):
        return random.randint(2, self.__p - 2)

    def __calculatePublicKey(self):
        return pow(self.__g, self.__privateKey, self.__p)

    def __calculateSharedSecret(self, gB):
        return pow(gB, self.__privateKey, self.__p)

    def process(self):
        signal.signal(signal.SIGINT, self.__signalHandler)
        self.__socket.connect((self.__host, self.__port))
        self.__socket.settimeout(SOCKET_TIMEOUT)
        self.__mustQuit.store(0)
        self.__isSendingPrevented.store(0)
        self.__canRead.store(1)
        self.__window = ClientWindow(self.__socket, self.__canRead)
        self.__window.registerOnClick(self.__onClick)
        self.__window.registerOnExit(self.__onExit)
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

    def __onExit(self):
        if messagebox.askyesno("Exit", "Do you want to quit the application?"):
            self.closeClient(informServer=True)

    def __onClick(self, event):
        if self.__isSendingPrevented.load() == 1:
            print(
                f'[WINDOW]: Sending is restricted. __isSendingPrevented: {self.__isSendingPrevented.load()}')
            return

        requestedId = self.__window.getEntryText()
        if requestedId == str(self.__id):
            print('[WINDOW]: Cannot make a request to itself')
            return

        if len(requestedId) == 0:
            return

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

            if self.__canRead.load() != 1:
                continue

            try:
                bytes = self.__socket.recv(4096)
                if len(bytes) == 0:
                    continue

                if self.__state == 'in-session':
                    if bytes == b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00':
                        self.__socket.send(
                            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
                        for _ in range(11):
                            messages.append(self.__socket.recv(20000))
                            self.__socket.send(
                                b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
                    else:
                        messages = bytes
                else:
                    messages += list(filter(None, bytes.decode().split('\0')))

                print(f'[RECEIVER]: Messages received.')
            except:
                if len(messages) == 0:
                    continue

            if self.__state == 'in-session':
                if type(messages) == list:
                    message = b''
                    for element in messages:
                        message += element
                else:
                    message = messages
            else:
                message = messages.pop(0)

            if message == 'quit':
                self.closeClient(informServer=False)
                break

            if self.__privateKey == -1 and self.__p != -1 and self.__g != -1:
                self.__privateKey = self.__generatePrivateKey()

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
                if 'G-' in message:
                    self.__g = int(message[message.index('-') + 1:])
                    print(f'[RECEIVER]: g has been received: {self.__g}')

                elif 'P-' in message:
                    self.__p = int(message[message.index('-') + 1:])
                    print(f'[RECEIVER]: p has been received: {self.__p}')

                elif message == '-1':
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

                elif message == '1':
                    # Other client said yes
                    # Send gA
                    self.__state = 'key-exchange'
                    try:
                        self.__socket.send(
                            str(self.__calculatePublicKey()).encode('utf-8'))
                    except:
                        self.closeClient(informServer=False)
                        break
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

            elif self.__state == 'key-exchange':
                # The message is gB
                gB = int(message[message.index('-') + 1:])
                self.__sessionKey = self.__calculateSharedSecret(gB).to_bytes(
                    length=512, signed=False, byteorder=sys.byteorder)
                print(f'[RECEIVER]: Session key has been generated.')
                self.__state = 'in-session'
                self.__window.setSessionKey(self.__sessionKey)
                self.__window.switchFrame()

            elif self.__state == 'in-session':
                if message == b'disconnected\x00':
                    self.__state = 'idle'
                    self.__sessionKey = -1
                    self.__window.switchFrame()
                    messages = []
                    self.__isSendingPrevented.store(0)
                    continue

                aes = AESCipher(self.__sessionKey)
                try:
                    messageObject = pickle.loads(message)
                except:
                    print(
                        '[RECEIVER]: pickle data was truncated. Could not load the image.')
                    messages = []
                    continue

                decryptedText = aes.decrypt(messageObject['text'])
                if messageObject['isImage']:
                    self.__window.renderReceivedImage(
                        decryptedText, messageObject['imageWidth'], messageObject['imageHeight'], messageObject['isPNG'])
                else:
                    self.__window.renderReceivedMessage(decryptedText.decode())
                messages = []
