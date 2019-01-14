from tkinter import *
from tkinter.ttk import *
from tkinter import Button, Label

from lfd.gui import utils


class BottomRight(Frame):
    """Bottom right Frame of the RightFrame of the app. This section contains
    all the active elements of the app, such as Buttons for selecting the DB,
    directory of images, moving to the next or previous image or changing the
    DB entries by verifying their truthfulness.

    """
    def __init__(self, parent):
        Frame.__init__(self)
        self.pack(side=TOP, fill=BOTH, expand=1)
        self.parent = parent
        self.data = parent.data

        self.falsebtn = Button(self, text="FALSE", bg="tomato2",
                               command=self.false)
        self.falsebtn.pack(side=TOP, pady=4)

        self.truebtn = Button(self, text="TRUE", bg="DarkOliveGreen3",
                              command=self.true)
        self.truebtn.pack(side=TOP, pady=4)

        self.imgselector = Button(self, text="Select images",
                                  command=self.selectimages)
        self.imgselector.pack(side=BOTTOM, pady=4)

        self.resselector = Button(self, text="Select results",
                                  command=self.selectresults)
        self.resselector.pack(side=BOTTOM, pady=4)

        self.nextbtn = Button(self, text="Next", command=self.nextimg)
        self.nextbtn.pack(side=RIGHT)

        self.prevbtn = Button(self, text="Previous", command=self.previmg)
        self.prevbtn.pack(side=LEFT)

        self.searchbtn = Button(self, text="Find", command=self.search)
        self.searchbtn.pack(side=LEFT, padx=50)

    def nextimg(self, *args):
        """Callback function that moves the current data index to the following
        one and updates the whole GUI.
        """
        self.data.getNext()
        self.parent.root.update()

    def previmg(self, *args):
        """Callback function that moves to the previous data instance and
        updates the whole GUI.
        """
        self.data.getPrevious()
        self.parent.root.update()

    def true(self, *args):
        """Callback that sets the false_positive attribute of the current Event
        to False, persists the change to the DB, moves the current data index
        to the following data instance and updates the whole GUI.

        """
        self.data.event.false_positive = False
        self.data.events.commit()
        self.nextimg()

    def false(self, *args):
        """Callback that sets the false_positive attribute of the current Event
        to True, persists the change to the DB, moves the current data index to
        the following data instance and updates the whole GUI.

        """
        self.data.event.false_positive = True
        self.data.events.commit()
        self.nextimg()

    def selectimages(self):
        """Re-initializes the apps selection of directory containing images and
        refreshes the whole GUI.

        """
        self.parent.root.initImages()
        self.parent.root.update()

    def selectresults(self):
        """Re-initializes the apps selection of the Event database and
        refreshes the whole GUI.

        """
        self.parent.root.initResults()
        self.parent.root.update()

    def search(self):
        """Opens a new window that allows user to input the run, camcol, filter
        and field designations of the Frame they would like to jump to. The
        search will jump to the first Event with the correct Frame designation.

        As there can be multiple Events on the same Frame, user can provide the
        ordinal number of the Event they are interested in.

        """
        top = Toplevel()
        top.geometry(utils.centerWindow(self, 270, 120))

        Label(top, text="Run:",    width=10).grid(row=0, column=0)
        Label(top, text="Camcol:", width=10).grid(row=1, column=0)
        Label(top, text="Filter:", width=10).grid(row=2, column=0)
        Label(top, text="Field:",  width=10).grid(row=3, column=0)
        Label(top, text="Event:",  width=10).grid(row=4, column=0)

        run, camcol, filter, field = StringVar(), StringVar(), \
                                     StringVar(), StringVar()
        which = StringVar(value="0")

        Entry(top, textvariable=run).grid(row=0, column=1)
        Entry(top, textvariable=camcol).grid(row=1, column=1)
        Entry(top, textvariable=filter).grid(row=2, column=1)
        Entry(top, textvariable=field).grid(row=3, column=1)
        Entry(top, textvariable=which).grid(row=4, column=1)

        top.bind("<Return>", lambda _: self._find(top, run, camcol, filter,
                                                  field, which))
        Button(top, text="Search", width=10, command = lambda:
               self._find(top, run, camcol, filter, field, which)
        ).grid(row=5, column=1, columnspan=2)


    def _find(self, window, run, camcol, filter, field, which):
        """Callback function that will read the required information from the
        search window, skip to (load) that data instance and update the GUI.

        """
        run = int(run.get())
        camcol = int(camcol.get())
        filter = filter.get()
        field = int(field.get())
        which = int(which.get())
        try:
            self.data.skip(run=run, camcol=camcol, filter=filter,
                           field=field, which=which)
            self.parent.root.update()
        except IndexError:
            self.parent.root.failedUpdate()
        window.destroy()

