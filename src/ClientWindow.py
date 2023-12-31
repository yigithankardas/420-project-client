from tkinter import *
from TimeoutPopup import TimeoutPopup
from ChatWindow import ChatWindow


class ClientWindow:
    def __init__(self, socket, canClientRead):
        self.__currentFrame = 2
        self.__window = Tk()
        self.__window.geometry('1000x400')
        self.__window.configure(bg='#282828')

        self.__frame1 = Frame(self.__window, bg='#282828')
        self.__frame1.pack(expand=True, fill='both')

        self.__frame2 = Frame(self.__window, bg='#282828')
        self.__frame2.pack(expand=True, fill='both')
        self.__chatWindow = ChatWindow(self.__frame2, socket, canClientRead)

        self.__idLabel = Label(
            self.__frame1, text='ID: *', bg='#282828', fg='white', font=('Helvetica', 16))
        self.__idLabel.pack(pady=20)

        self.__entry = Entry(self.__frame1, bg='#141414', fg='white',
                             bd=2, relief='solid')
        self.__entry.pack(pady=10, padx=20, ipady=5, fill='both')

        self.__button = Button(
            self.__frame1, text='Send Request', bg='#141414', fg='white', font=('Helvetica', 16))
        self.__button.pack(pady=10)
        self.switchFrame()

    def switchFrame(self):
        if self.__currentFrame == 1:
            self.__frame1.pack_forget()
        else:
            self.__frame2.pack_forget()

        self.__currentFrame = 3 - self.__currentFrame

        if self.__currentFrame == 1:
            self.__frame1.pack(expand=True, fill='both')
        else:
            self.__frame2.pack(expand=True, fill='both')
        self.__chatWindow.resetChatAreas()

    def renderReceivedMessage(self, message):
        self.__chatWindow.receiveMessage(message)

    def renderReceivedImage(self, image, witdh, height, isPNG):
        self.__chatWindow.receiveImage(image, witdh, height, isPNG)

    def mainloop(self):
        self.__window.mainloop()

    def destroy(self):
        self.__window.destroy()

    def quit(self):
        self.__window.quit()

    def getEntryText(self):
        return self.__entry.get()

    def after(self, ms, function):
        self.__window.after(ms, function)

    def registerOnClick(self, function):
        self.__button.bind('<Button-1>', function)

    def registerOnExit(self, function):
        self.__window.wm_protocol("WM_DELETE_WINDOW", function)

    def popup(self, message, timeout):
        popup = TimeoutPopup('Confirmation',
                             message, timeout)
        popup.mainloop()
        return popup.result()

    def setIdLabel(self, id):
        self.__idLabel.config(text=f'ID: {id}')
        self.__chatWindow.setID(id)

    def setSessionKey(self, sessionKey):
        self.__chatWindow.setSessionKey(sessionKey)
