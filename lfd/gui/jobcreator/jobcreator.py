#!/usr/bin/python
# -*- coding: utf-8 -*-
import os

from  lfd.gui.jobcreator.leftframe import LeftFrame
from  lfd.gui.jobcreator.rightframe import RightFrame
from lfd.gui.utils import utils

from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog
from tkinter import messagebox

import lfd.createjobs as cj


class SetupPopUp:
    """A TopLevel popup that will lock the main App and allow users to set up
    the required environmental paths to the SDSS data before unlocking the App
    again.

    Without those paths the createjobs module will likely not be able to create
    jobs.
    """
    def __init__(self, parent):
        self.top = Toplevel(parent)
        self.top.wm_title("Envionment not set up properly!")
        txt = ("Environment is missing BOSS and/or PHOTO_REDUX env variables.\n"
               "Please provide the PHOTO_REDUX path. See"
               "help(createjobs.setup.) for details.")

        self.explainLabel = Label(self.top, text=txt)
        self.explainLabel.pack()

        self.photoreduxSV = StringVar()
        self.pathEntry = Entry(self.top)
        self.pathEntry.pack(padx=5)

        self.okButton = Button(self.top, text="OK", command=self.ok)
        self.okButton.pack(pady=5)
        self.top.grab_set()

    def ok(self):
        """A callback function that will call the createjobs setup function,
        unlock the main app and destroy the popup.
        """
        cj.setup(self.photoreduxSV.get())
        self.top.grab_release()
        self.top.destroy()


class JobCreator(Tk):
    """GUI interface to createjobs package. Not all options are seamlessly
    supported. To execute it instantiate the class and run its mainloop method
    or invoke run function located in this module. At startup time app will
    verify if the minimal environment for job creation is in place and if not
    it will allow user to set the required environmental variable.

    Consists two frames:

    * LeftFrame contains most of the adjustable parameters for the jobs.
    * RightFrame contains the used template from which dqs files will be
      created.

    Contains the Job object from the createjobs module so that all Frames that
    belong to the same appication can access its settings.
    """
    def __init__(self):
        Tk.__init__(self)
        self.geometry(utils.centerWindow(self, 1040, 750))

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

        self.check_setup()


    def check_setup(self):
        """If BOSS or PHOTO_REDUX environemntal paths to the SDSS data were not
        set up before launching the app spawns a popup that will let users
        set the required minimal path to data.
        If the toplevel directory $BOSS variable is set up and $PHOTO_REDUX is
        not it is assumed that the SDSS convention is followed and $PHOTO_REDUX
        is set to $BOSS/photo/redux.

        """
        if ("BOSS" in os.environ) and not ("PHOTO_REDUX" in os.environ):
            cj.setup()

        if not ("BOSS" in os.environ) or not ("PHOTO_REDUX" in os.environ):
            tplvl = SetupPopUp(self)

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
