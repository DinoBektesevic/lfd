#!/usr/bin/python
# -*- coding: utf-8 -*-
from .leftframe import LeftFrame
from .rightframe import RightFrame
from lfd.gui import utils
from tkinter import *
from tkinter import ttk

from tkinter import Label
from tkinter import filedialog

import lfd.results as res
from .images import Images

class ImageChecker(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.geometry(utils.centerWindow(self, 1100, 600))
        self.title("Trail Sorter")

        self.respath = "~/Desktop"
        self.imgpath = "~/Desktop"

        self.data = Images(self)

        self.leftFrame = LeftFrame(self)
        self.rightFrame = RightFrame(self)

        self.bind('<Left>', self.rightFrame.bottomRight.previmg)
        self.bind('<Right>', self.rightFrame.bottomRight.nextimg)
        self.bind("<Up>", self.rightFrame.bottomRight.true)
        self.bind("<Down>", self.rightFrame.bottomRight.false)

        self.initGUI()

    def initGUI(self):
        self.initResults()
        self.initImages()
        self.update()

    def initResults(self):
        path = filedialog.askopenfilename(parent=self,
                                          title="Please select results database...",
                                          initialdir=self.respath)
        if path:
            try: self.data.initEvents(path)
            except OSError: self.rightFrame.failedEventLoadScreen()
        else:
            self.rightFrame.failedEventLoadScreen()

    def initImages(self):
        path = filedialog.askdirectory(parent=self,
                                       title="Please select image folder...",
                                       initialdir=self.imgpath)
        if path:
            try: self.data.initImages(path)
            except OSError: self.leftFrame.failedImageLoadScreen()
        else:
            self.leftFrame.failedImageLoadScreen()

    def update(self):
        self.leftFrame.update()
        self.rightFrame.update()


def run():
    app = ImageChecker()
    app.mainloop()
