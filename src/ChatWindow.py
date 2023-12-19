import tkinter as tk
from tkinter import scrolledtext, filedialog
from tkinter import font as tkfont
from PIL import Image, ImageTk


class ChatWindow:
    def __init__(self, master):
        self.master = master

        self.font = tkfont.Font(family="Helvetica", size=12)
        self.chat_area = scrolledtext.ScrolledText(
            master, state='disabled', wrap=tk.WORD, font=self.font, bg="#282828")
        self.chat_area.tag_configure(
            "left", justify="left", background="#3c3c3c", lmargin1=20, lmargin2=20, rmargin=60)
        self.chat_area.tag_configure(
            "right", justify="right", background="#128C7E", lmargin1=60, lmargin2=20, rmargin=20)

        self.chat_area.grid(row=0, column=0, columnspan=3, sticky="nsew")

        self.entry = tk.Entry(master, font=self.font, bg='#141414', fg='white')
        # Enter tuşuna basınca mesaj gönder
        self.entry.bind("<Return>", self.send_message)
        self.entry.grid(row=1, column=0, sticky="ew")

        self.send_button = tk.Button(
            master, text="Gönder", command=lambda: self.send_message(None), bg='#141414', fg='white')
        self.send_button.grid(row=1, column=1)

        self.photo_button = tk.Button(
            master, text="Fotoğraf Gönder", command=self.send_photo, bg='#141414', fg='white')
        self.photo_button.grid(row=1, column=2)

        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

    def send_message(self, event):
        message = self.entry.get()
        if message:
            self.update_chat_area(message, "right")
            self.entry.delete(0, tk.END)
            # Burada mesajı şifreleyip gönderme fonksiyonunu çağırabilirsiniz

    def send_photo(self):
        file_path = filedialog.askopenfilename()
        if not file_path:
            return
        # Fotoğraf önizlemesini göster
        self.display_photo(file_path, "right")
        # Burada fotoğrafı şifreleyip gönderme fonksiyonunu çağırabilirsiniz

    def display_photo(self, file_path, side):
        image = Image.open(file_path)
        image.thumbnail((200, 200))  # Resmi küçült
        photo = ImageTk.PhotoImage(image)

        self.chat_area.configure(state='normal')

        # Sağa yatırma etkisi için boşluk ekleyin
        if side == "right":
            padding = " " * 10  # Sağa yatırma için boşluk miktarını ayarlayın
            self.chat_area.insert(tk.END, padding, side)

        self.chat_area.image_create(tk.END, image=photo, padx=10, pady=10)
        self.chat_area.insert(tk.END, "\n", side)
        self.chat_area.configure(state='disabled')
        self.chat_area.yview(tk.END)
        self.chat_area.image = photo  # Referansı saklayın

    def update_chat_area(self, message, side):
        self.chat_area.configure(state='normal')
        self.chat_area.insert(tk.END, message + "\n", side)
        self.chat_area.configure(state='disabled')
        self.chat_area.yview(tk.END)

    def receive_message(self, message):
        self.update_chat_area(message, "left")
