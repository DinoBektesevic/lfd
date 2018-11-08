#!/usr/bin/python
# -*- coding: utf-8 -*-
import tempfile

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

    or invoke run function located in this module.

    Consists two frames - left and right.
    leftFrame contains most of the adjustable parameters for the jobs.
    rightFrame contains the used template from which dqs files will be created.

    Contains the Job object from the createjobs module so that all Frames that
    belong to the same appication can access its settings.
    """
    def __init__(self):
        Tk.__init__(self)
        self.geometry(utils.centerWindow(self, 1040, 750))

        # we create a default Job instance so that we could take advantage of
        # all the defaults defined in the createjobs module. It's state is NOT
        # changed anywhere in the code nor is the job itself used to create the
        # files - we use a different job for that. In fact the temporary dir
        # used to instantiate this job will not exists to force devs to use
        # a different dir.
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

    def create(self):
        """Changes the state of the Job instance of the application to write
        the new settings, read from the values in the right and left frames,
        and creates the jobs.
        """
        conf = self.leftFrame.getConf()
        tmplt = self.rightFrame.getTemplate()

        job = cj.Jobs(conf.n, runs=conf.runs, queue=conf.q, ppn=conf.ppn,
                       command=conf.cmd, wallclock=conf.wallt, cputime=conf.cput, 
                       template=tmplt, save_path=conf.savepath,
                       res_path=conf.respath)

        job.create()
        

def run():
    """Run the JobCreator GUI."""
    app = JobCreator()
    app.mainloop()
