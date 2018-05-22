#!/usr/bin/python
# -*- coding: utf-8 -*-
from .leftframe import LeftFrame
from .rightframe import RightFrame
from gui.utils import utils

import ttk
from Tkinter import *
from ttk import *

import createjobs as cj


class JobCreator(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.geometry(utils.centerWindow(self, 1040, 750))

        self.job = cj.Jobs(1)

        self.leftFrame = LeftFrame(self)
        self.rightFrame = RightFrame(self)
        
        self.title("Job Creator")
        

def run():
    app = JobCreator()
    app.mainloop()