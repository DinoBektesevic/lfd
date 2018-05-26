from tkinter import *
from tkinter.ttk import *

from .topright import TopRight
from .botright import BottomRight

class RightFrame(Frame):
    def __init__(self, parent):
        Frame.__init__(self, relief=RAISED, borderwidth=1)
        self.pack(side=RIGHT, fill=BOTH, expand=1)
        self.root = parent

        self.topright = TopRight(self)
        self.bottomright = BottomRight(self)

    def update(self):
        self.topright.updateImageData()
