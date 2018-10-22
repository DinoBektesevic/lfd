#!/usr/bin/python
# -*- coding: utf-8 -*-
from .leftframe import LeftFrame
from .rightframe import RightFrame
from lfd.gui.utils import utils

from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog
from tkinter import messagebox

import lfd.createjobs as cj

class JobCreator(Tk):
    """Class for the GUI that interfaces createjobs package. Not all options
    are seamlessly supported. To execute it instantiate the class and run its
    mainloop method:

    >>> app = JobCreator()
    >>> app.mainloop()
    
    Consists two frames - left and right.
    leftFrame contains most of the adjustable parameters for the jobs.
    rightFrame contains the used template from which dqs files will be created.

    Contains the Job object from the createjobs module so that all Frames can
    inherit and access it and actually change the settings. 
    """
    def __init__(self):
        Tk.__init__(self)
        self.geometry(utils.centerWindow(self, 1040, 750))

        try:
            self.job = cj.Jobs(1)
        except FileExistsError:
            messagebox.showerror("Directory exists!", "To avoid overriding " +
                                 "existing jobs select a different directory.")
            foldername = filedialog.askdirectory()
            self.job = cj.Jobs(1, save_path=foldername)
                 
        self.leftFrame = LeftFrame(self)
        self.rightFrame = RightFrame(self)

        self.title("Job Creator")

def run():
    """Run the JobCreator GUI."""
    app = JobCreator()
    app.mainloop()
