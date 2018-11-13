from tkinter import *
from tkinter.ttk import *

from .topright import TopRight
from .botright import BottomRight

class RightFrame(Frame):
    def __init__(self, parent):
        Frame.__init__(self, relief=RAISED, borderwidth=1)
        self.pack(side=RIGHT, fill=BOTH, expand=1)
        self.root = parent

        self.topRight = TopRight(self)
        self.bottomRight = BottomRight(self)

    def update(self):
        self.topRight.updateImageData()

    def failedEventLoadScreen(self):
        Label(self.topRight, background="red2", font=("Helvetica", 20),
              text="NO IMAGE DATA\nFOUND").grid(row=0, columnspan=2, padx=50,
                                                pady=(50,0))

