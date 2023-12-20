import tkinter as tk
from tkinter import scrolledtext, filedialog, font as tkfont
from PIL import Image, ImageTk
import socket
from AESCipher import AESCipher
import pickle
from datetime import datetime
import os


class ChatWindow:
    def __init__(self, master, socket: socket.socket):
        self.__master = master
        self.__socket = socket
        self.__id = -1
        self.__sessionKey = None
        self.__images = []
        self.__aes = None

        self.__font = tkfont.Font(family="Helvetica", size=12)
        self.__chatArea = scrolledtext.ScrolledText(
            master, state='disabled', wrap=tk.WORD, font=self.__font, bg="#282828")
        self.__chatArea.tag_configure(
            "left", justify="left", background="#C5D8A5", lmargin1=20, lmargin2=20, rmargin=60)
        self.__chatArea.tag_configure(
            "right", justify="right", background="#3EC7B7", lmargin1=60, lmargin2=20, rmargin=20)

        self.__chatArea.grid(row=0, column=0, columnspan=3, sticky="nsew")

        self.__entry = tk.Entry(master, font=self.__font,
                                bg='#141414', fg='white')
        self.__entry.bind("<Return>", self.__sendMessage)
        self.__entry.grid(row=1, column=0, sticky="ew")

        self.__sendButton = tk.Button(
            master, text="Send", command=lambda: self.__sendMessage(None), bg='#0052cc', fg='white')  # Mavi renk
        self.__sendButton.grid(row=1, column=1)

        self.__photoButton = tk.Button(
            master, text="Send Image", command=self.__sendImage, bg='#4CAF50', fg='white')  # Yeşil renk
        self.__photoButton.grid(row=1, column=2)

        self.__master.grid_rowconfigure(0, weight=1)
        self.__master.grid_columnconfigure(0, weight=1)

    def setSessionKey(self, sessionKey):
        self.__sessionKey = sessionKey
        self.__aes = AESCipher(self.__sessionKey)

    def resetChatAreas(self):
        self.__chatArea.configure(state='normal')
        self.__chatArea.delete("1.0", tk.END)
        self.__chatArea.configure(state='disabled')

    def setID(self, id):
        self.__id = id

    def __sendMessage(self, event):
        if self.__aes == None:
            print('[GUI]: Session key is not set.')
            return

        plainText = self.__entry.get()
        if len(plainText) == 0:
            return

        cipherText = self.__aes.encrypt(plainText)
        messageObject = {
            'text': cipherText,
            'isImage': False,
            'imageWidth': 0,
            'imageHeight': 0,
            'isPNG': False,
            'date': datetime.now(),
            'id': self.__id
        }
        serializedMessage = pickle.dumps(messageObject)
        try:
            self.__socket.send(serializedMessage)
        except:
            print('[GUI]: Could not send the message.')
            return

        self.__updateChatArea(plainText, "right")
        self.__entry.delete(0, tk.END)

    def __sendImage(self):
        if self.__aes == None:
            print('[GUI]: Session key is not set.')
            return

        file_path = filedialog.askopenfilename()
        if not file_path:
            return

        image = Image.open(file_path)
        image.thumbnail((200, 200))
        imageBytes = image.tobytes()
        cipherText = self.__aes.encrypt(imageBytes)
        messageObject = {
            'text': cipherText,
            'isImage': True,
            'imageWidth': image.width,
            'imageHeight': image.height,
            'isPNG': True if os.path.splitext(file_path)[1] == '.png' else False,
            'date': datetime.now(),
            'id': self.__id
        }
        serializedMessage = pickle.dumps(messageObject)
        try:
            self.__socket.send(serializedMessage)
        except:
            print('[GUI]: Could not send the image.')
            return

        self.__displayImage(image, "right")

    def __displayImage(self, image, side):
        photo = ImageTk.PhotoImage(image)

        self.__chatArea.configure(state='normal')

        if side == "right":
            padding = " " * 10
            self.__chatArea.insert(tk.END, padding, side)

        self.__chatArea.image_create(tk.END, image=photo)
        self.__chatArea.insert(tk.END, "\n", side)
        self.__chatArea.configure(state='disabled')
        self.__chatArea.yview(tk.END)
        self.__images.append(photo)

    def __updateChatArea(self, message, side):
        self.__chatArea.configure(state='normal')
        self.__chatArea.insert(tk.END, message + "\n", side)
        self.__chatArea.configure(state='disabled')
        self.__chatArea.yview(tk.END)

    def receiveMessage(self, message):
        self.__updateChatArea(message, "left")

    def receiveImage(self, imageBytes, width, height, isPNG):
        if isPNG:
            image = Image.frombytes('RGBA', (width, height), imageBytes)
        else:
            image = Image.frombytes('RGB', (width, height), imageBytes)
        self.__displayImage(image, 'left')
