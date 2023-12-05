from tkinter import *
from TimeoutPopup import TimeoutPopup


class ClientWindow:
    def __init__(self):
        self.__window = Tk()
        self.__frame = Frame(self.__window)
        self.__idLabel = Label(
            self.__frame, text='ID: *', bg='black', fg='white')
        self.__entry = Entry(self.__frame)
        self.__button = Button(self.__frame, text='Send Request')

    def prepare(self):
        self.__idLabel.pack()
        self.__entry.pack()
        self.__button.pack()
        self.__frame.pack()
        self.__window.mainloop()

    def destroy(self):
        self.__window.destroy()

    def getEntryText(self):
        return self.__entry.get()

    def after(self, ms, function):
        self.__window.after(ms, function)

    def registerOnClick(self, function):
        self.__button.bind('<Button-1>', function)

    def popup(self, message, timeout):
        return TimeoutPopup(self.__window, 'Confirmation',
                            message, timeout).result()

    def setIdLabel(self, id):
        self.__idLabel.config(text=f'ID: {id}')
