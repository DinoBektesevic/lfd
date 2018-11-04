#!/usr/bin/python
# -*- coding: utf-8 -*-
from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox

from .lefttopframe import TopFrame
from .leftmidframe import MidFrame
from .leftbotframe import BotFrame

import lfd.createjobs as cj

class LeftFrame(Frame):
    """LeftFrame of the jobcreator gui. This frame contains all the things
    configurable by the user. It contains 3 subframes: top, mid and bot.
    Top - glob. exec. settings for the jobs (f.e. wallclock, cputime, ppn...)
    Mid - invocation settings (f.e. from all runs, lists, results...)
    Bot - glob. env. settings (f.e. template, save paths, copy paths...)

    Has to inherit from the root frame because job access is required.

    Will spawn additional windows promting user for settings for any
    particularily complex configurations.
    """
    def __init__(self, parent):
        Frame.__init__(self, parent, relief=RAISED, borderwidth=1)
        self.pack(side=LEFT, fill=BOTH, expand=1)

        # carry the root frame and the root job so that configurations can be
        # accessed and changed from any frame later on
        self.root = parent
        self.job = parent.job

        self.topFrame = TopFrame(self)
        self.midFrame = MidFrame(self)
        self.botFrame = BotFrame(self)

        a = Button(self, text="Create Jobs", command=self.createjobs)
        a.grid(row=10, column=0, columnspan=2)


    def createjobs(self):
        self.root.job.n = self.topFrame.getn()
        self.root.job.queue =  self.topFrame.queue.get()
        self.root.job.wallclock = self.topFrame.wallclock.get()
        self.root.job.cputime =  self.topFrame.cputime.get()
        self.root.job.ppn =  self.topFrame.ppn.get()
        self.root.job.command = self.topFrame.getcommand()

        #runs = self.midFrame.runs

        #savepath = self.botFrame.savepath
        #templatepath = self.botFrame.templatepath

        #jobs = cj.Jobs(n, queue=queue, path=savepath,
        #               wallclock=wallclock, cputime=cputime, ppn=ppn,
        #               command=cmnd, runs=runs,
        #               template_path=templatepath)
        self.root.job.create()
#        del jobs
