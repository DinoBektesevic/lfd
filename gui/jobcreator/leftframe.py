#!/usr/bin/python
# -*- coding: utf-8 -*-
from Tkinter import *
from ttk import *
import tkMessageBox

from .lefttopframe import TopFrame
from .leftmidframe import MidFrame
from .leftbotframe import BotFrame
import createjobs as cj

class LeftFrame(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent, relief=RAISED, borderwidth=1)
        self.pack(side=LEFT, fill=BOTH, expand=1)

        self.root = parent
        self.job = parent.job
        self.topFrame = TopFrame(self)
        self.midFrame = MidFrame(self)
        self.botFrame = BotFrame(self)

        a = Button(self, text="Create Jobs", command=self.createjobs)
        a.grid(row=10, column=0, columnspan=2)


    def setn(self):
        try:
            n = int(self.topFrame.numjobs.get())
        except ValueError as e:
            tkMessageBox.showerror("Incorrect Format", e)
        if n==0:
            tkMessageBox.showerror("Input Error", "Number of jobs "+\
                                   "can't be 0")
        else:
            return n

    def setcommand(self):
        command = self.topFrame.command.get(1.0, END)
        cmnd = command[:-1]
        cmnd = cmnd.replace("\n", ";")
        cmnd = cmnd.replace(";;", ";")
        print self.job.command[:38] + cmnd + '"\n '
        return self.job.command[:38] + cmnd + '"\n '

    def createjobs(self):
        self.root.job.n = self.setn()
        self.root.job.queue =  self.topFrame.queue.get()
        self.root.job.wallclock = self.topFrame.wallclock.get()
        self.root.job.cputime =  self.topFrame.cputime.get()
        self.root.job.ppn =  self.topFrame.ppn.get()
        self.root.job.command = self.setcommand()

        #runs = self.midFrame.runs
        
        #savepath = self.botFrame.savepath
        #templatepath = self.botFrame.templatepath
                
        #jobs = cj.Jobs(n, queue=queue, path=savepath,
        #               wallclock=wallclock, cputime=cputime, ppn=ppn,
        #               command=cmnd, runs=runs,
        #               template_path=templatepath)
        self.root.job.create()
#        del jobs        
