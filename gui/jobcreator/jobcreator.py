#!/usr/bin/python
# -*- coding: utf-8 -*-
import os

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

        self.check_setup()

        # we create a default Job instance so that we could take advantage of
        # all the defaults defined in the createjobs module. Its state is NOT
        # changed anywhere in the code nor is the Job itself used to create the
        # files - we create a new Job instance for that. In fact the temporary
        # dir used to instantiate this job will not exists to force devs to use
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

    def  check_setup(self):
        """Checks if the required environment variables are set so that
        createjobs module can work properly. If $BOSS is set up then default
        $PHOTO_REDUX path is assumed, if not $PHOTO_REDUX path is prompted for.
        """
        if "BOSS" in os.environ:
            cj.setup()

        if not("BOSS" in os.environ) or not ("PHOTO_REDUX" in os.environ):
            t = Toplevel(self)
            t.wm_title("Environment is not set up properly!")
            txt = ("Environment is missing BOSS and/or PHOTO_REDUX env variables.\n"
                   "Please provide the PHOTO_REDUX path. "
                   "See help(createjobs.setup.) for more details.")
            l = Label(t, text=txt)
            l.pack(side=TOP, fill="both")
            photoredux = StringVar()
            e = Entry(t, textvariable=photoredux, width=50)
            e.pack(side=TOP)
            
        def setup_callback():
            cj.setup(photoredux.get())
            t.destroy()

        b = Button(t, text="OK", width=15, command=setup_callback)
        b.pack()


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
