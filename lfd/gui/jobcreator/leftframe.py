#!/usr/bin/python
# -*- coding: utf-8 -*-
from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox

from  lfd.gui.jobcreator.lefttopframe import TopFrame
from  lfd.gui.jobcreator.leftmidframe import MidFrame
from  lfd.gui.jobcreator.leftbotframe import BotFrame

import lfd.createjobs as cj

import collections

class LeftFrame(Frame):
    """LeftFrame of the jobcreator gui. Contains 3 subframes: top, mid and bot.
    In order they control the folowing settings for job creation:

    * Top - global execution settings for the jobs (f.e. wallclock, cputime,
      ppn...)
    * Mid - invocation settings (f.e. from all runs, lists, results...)
    * Bot - global environment settings (f.e. template, save paths,
      copy paths...)

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

        a = Button(self, text="Create Jobs", command=self.root.create)
        a.grid(row=10, column=0, columnspan=2)


    def getConf(self):
        """Reads the complete configuration selected by the user."""
        Conf = collections.namedtuple("Conf", ("n runs  q wallt cput ppn cmd "
                                               "savepath tmpltpath respath"))

        # template path will never really be used as the template will be read
        # dirrectly from the rightFrame and sent in as a string.
        conf = Conf(
            n = self.topFrame.getn(),
            q =  self.topFrame.queue.get(),
            ppn =  self.topFrame.ppn.get(),
            cmd = self.topFrame.getcommand(),
            cput =  self.topFrame.cputime.get(),
            wallt = self.topFrame.wallclock.get(),
            respath = self.botFrame.respath.get(),
            savepath = self.botFrame.jobsavepath.get(),
            tmpltpath = self.botFrame.tmpltpath.get(),
            runs = self.midFrame.runs
        )
        return conf
