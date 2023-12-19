import tkinter as tk
from tkinter import scrolledtext, filedialog, font as tkfont
from PIL import Image, ImageTk
import socket


class ChatWindow:
    def __init__(self, master, socket: socket.socket):
        self.__master = master

        self.__font = tkfont.Font(family="Helvetica", size=12)
        self.__chatArea = scrolledtext.ScrolledText(
            master, state='disabled', wrap=tk.WORD, font=self.__font, bg="#282828")
        self.__chatArea.tag_configure(
            "left", justify="left", background="#3c3c3c", lmargin1=20, lmargin2=20, rmargin=60)
        self.__chatArea.tag_configure(
            "right", justify="right", background="#128C7E", lmargin1=60, lmargin2=20, rmargin=20)

        self.__chatArea.grid(row=0, column=0, columnspan=3, sticky="nsew")

        self.__entry = tk.Entry(master, font=self.__font,
                                bg='#141414', fg='white')
        self.__entry.bind("<Return>", self.__sendMessage)
        self.__entry.grid(row=1, column=0, sticky="ew")

        self.__sendButton = tk.Button(
            master, text="Gönder", command=lambda: self.__sendMessage(None), bg='#141414', fg='white')
        self.__sendButton.grid(row=1, column=1)

        self.__photoButton = tk.Button(
            master, text="Fotoğraf Gönder", command=self.__sendPhoto, bg='#141414', fg='white')
        self.__photoButton.grid(row=1, column=2)

        self.__master.grid_rowconfigure(0, weight=1)
        self.__master.grid_columnconfigure(0, weight=1)

    def __sendMessage(self, event):
        message = self.__entry.get()
        if len(message) == 0:
            return

        if message:
            self.__updateChatArea(message, "right")
            self.__entry.delete(0, tk.END)
        # Encrypt the message and send it

    def __sendPhoto(self):
        file_path = filedialog.askopenfilename()
        if not file_path:
            return
        self.__displayPhoto(file_path, "right")
        # Encrypt the photo and send it

    def __displayPhoto(self, file_path, side):
        image = Image.open(file_path)
        image.thumbnail((200, 200))
        photo = ImageTk.PhotoImage(image)

        self.__chatArea.configure(state='normal')

        if side == "right":
            padding = " " * 10
            self.__chatArea.insert(tk.END, padding, side)

        self.__chatArea.image_create(tk.END, image=photo, padx=10, pady=10)
        self.__chatArea.insert(tk.END, "\n", side)
        self.__chatArea.configure(state='disabled')
        self.__chatArea.yview(tk.END)
        self.__chatArea.image = photo

    def __updateChatArea(self, message, side):
        self.__chatArea.configure(state='normal')
        self.__chatArea.insert(tk.END, message + "\n", side)
        self.__chatArea.configure(state='disabled')
        self.__chatArea.yview(tk.END)

    def receiveMessage(self, message):
        self.__updateChatArea(message, "left")
