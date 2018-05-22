#!/usr/bin/python
# -*- coding: utf-8 -*-
from .leftframe import LeftFrame
from .rightframe import RightFrame
from gui.utils import utils
from .images import Images

import ttk
from Tkinter import *
from ttk import *
from Tkinter import Label
import tkFileDialog
        

class ImageChecker(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.geometry(utils.centerWindow(self, 1100, 600))
        self.title("Trail Sorter")

        self.respath = "~/Desktop"
        self.imgpath = "~/Desktop"
              
        self.data = Images(self)
        
        self.leftframe = LeftFrame(self)
        self.rightframe = RightFrame(self)

        
        self.bind('<Left>', self.rightframe.bottomright.previmg)
        self.bind('<Right>', self.rightframe.bottomright.nextimg)
        self.bind("<Up>", self.rightframe.bottomright.true)
        self.bind("<Down>", self.rightframe.bottomright.false)
        
        self.initGUI()

    def initGUI(self):
        self.initImages()
        self.initImageData()
        self.update()

    def initImageData(self):
        path = tkFileDialog.askdirectory(parent=self,
                            title="Please select results folder...",
                            initialdir=self.respath)
        self.data.setResults(path)

    def initImages(self):
        path = tkFileDialog.askdirectory(parent=self,
                            title="Please select image folder...",
                            initialdir=self.imgpath)
        self.data.setImages(path)

    def update(self):
        self.leftframe.update()
        self.rightframe.update()
 
        
def run():
    app = ImageChecker()
    app.mainloop()
