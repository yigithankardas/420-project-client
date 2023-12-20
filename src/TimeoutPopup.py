from tkinter import *


class TimeoutPopup(Tk):
    def __init__(self, title, message, timeout):
        Tk.__init__(self)
        self.title(title)

        self.__result = None

        self.__frame = Frame(self)
        self.__label = Label(self.__frame, text=message,
                             font=("Helvetica", 14))
        self.__label.pack(padx=10, pady=10)

        button_style_yes = {"font": (
            "Helvetica", 14), "bg": "#4CAF50", "fg": "white", "bd": 0, "relief": FLAT}
        button_style_no = {"font": (
            "Helvetica", 14), "bg": "#ff0000", "fg": "white", "bd": 0, "relief": FLAT}

        self.__yesButton = Button(
            self.__frame, text="Yes", command=self.__onYes, **button_style_yes)
        self.__yesButton.pack(side=LEFT, padx=10, pady=5)

        self.__noButton = Button(
            self.__frame, text="No", command=self.__onNo, **button_style_no)
        self.__noButton.pack(side=RIGHT, padx=10, pady=5)

        self.__frame.pack()

        self.__after = self.after(timeout, self.__onTimeout)

    def __onYes(self):
        self.__result = 'yes'
        self.after_cancel(self.__after)
        self.destroy()

    def __onNo(self):
        self.__result = 'no'
        self.after_cancel(self.__after)
        self.destroy()

    def __onTimeout(self):
        self.__result = None
        self.after_cancel(self.__after)
        self.destroy()

    def result(self):
        return self.__result
