from tkinter import *


class TimeoutPopup(Toplevel):
    def __init__(self, parent, title, message, timeout):
        Toplevel.__init__(self, parent)
        self.title(title)

        self.__result = None

        __label = Label(self, text=message)
        __label.pack(padx=10, pady=10)

        self.__yesButton = Button(self, text="Yes", command=self.__onYes)
        self.__yesButton.pack(side=LEFT, padx=10)

        self.__noButton = Button(self, text="No", command=self.__onNo)
        self.__noButton.pack(side=LEFT, padx=10)

        self.after(timeout, self.__onTimeout)

    def __onYes(self):
        self.__result = 'yes'
        self.destroy()

    def __onNo(self):
        self.__result = 'no'
        self.destroy()

    def __onTimeout(self):
        self.__result = None
        self.destroy()

    def result(self):
        return self.__result
