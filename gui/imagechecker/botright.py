#!/usr/bin/python
# -*- coding: utf-8 -*-
from Tkinter import *
from ttk import *
from Tkinter import Button, Label
from gui.utils import utils


class BottomRight(Frame):
    def __init__(self, parent):
        Frame.__init__(self)
        self.pack(side=TOP, fill=BOTH, expand=1)
        self.parent = parent
        self.data = parent.root.data
        
        self.falsebtn = Button(self, text="FALSE", bg="tomato2",
                               command=self.false)
        self.falsebtn.pack(side=TOP, pady=4)
        
        self.truebtn = Button(self, text="TRUE",
                              bg="DarkOliveGreen3", command=self.true)
        self.truebtn.pack(side=TOP, pady=4)

        
        self.imgselector = Button(self, text="Select images",
                                  command=self.selectimages)
        self.imgselector.pack(side=BOTTOM, pady=4)

        self.resselector = Button(self, text="Select results",
                                  command=self.selectresults)
        self.resselector.pack(side=BOTTOM, pady=4)


        self.nextbtn = Button(self, text="Next", command=self.nextimg)
        self.nextbtn.pack(side=RIGHT)


        self.prevbtn = Button(self, text="Previous",
                              command=self.previmg)
        self.prevbtn.pack(side=LEFT)
        
        self.searchbtn = Button(self, text="Find", command=self.search)
        self.searchbtn.pack(side=LEFT, padx=50)

    def nextimg(self, *args):
        self.data.getNext()
        self.parent.root.update()

    def previmg(self, *args):
        self.data.getPrevious()
        self.parent.root.update()

    def true(self, *args):
        self.data.updateImageData({"false_positive": False})
        self.nextimg()

    def false(self, *args):
        res = self.data.getImageData()
        if res is not None:
            res.false_positive = True
        self.nextimg()

    def selectimages(self):
        self.parent.root.initImages()
        self.parent.root.update()

    def selectresults(self):
        self.parent.root.initImageData()
        self.parent.root.update()

    def search(self):
        #5327 6 u 61
        #self.data.skip(run=5327, camcol=6, filter="u", field=61)
        top = Toplevel()
        top.geometry(utils.centerWindow(self, 270, 120))

        Label(top, text="Run:", width=10).grid(row=0,column=0)
        Label(top, text="Camcol:", width=10).grid(row=1,column=0)
        Label(top, text="Filter:", width=10).grid(row=2,column=0)
        Label(top, text="Field:", width=10).grid(row=3,column=0)

        run, camcol, filter, field = StringVar(), StringVar(), \
                                     StringVar(), StringVar()
        
        Entry(top, textvariable=run).grid(row=0, column=1)
        Entry(top, textvariable=camcol).grid(row=1, column=1)
        Entry(top, textvariable=filter).grid(row=2, column=1)
        Entry(top, textvariable=field).grid(row=3, column=1)

        top.bind("<Return>", lambda _:
                 self._find(run, camcol, filter, field)
        )
        Button(top, text="Search", width=10, command = lambda:
               self._find(run, camcol, filter, field)
        ).grid(row=4, column=1, columnspan=2)
        

    def _find(self, run, camcol, filter, field):
        run = int(run.get())
        camcol = int(camcol.get())
        filter = filter.get()
        field = int(field.get())
        self.data.skip(run=run, camcol=camcol, filter=filter,
                       field=field)