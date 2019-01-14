import os
import threading
import queue
import time

from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog, messagebox

import lfd.createjobs as cj
from lfd.gui.utils import utils
import lfd.results as results

class MidFrame(Frame):
    """Part of the LeftFrame of the GUI. Contains the drop-down menu that
    selects the runs that will be processed. Currently the option to select
    from results database are a bit wonky.

    Requires a parent Frame that has access to Job object so that the settings
    can propagate to it.

    """
    def __init__(self, parent, row=1, col=0):
        Frame.__init__(self, parent)
        self.parent = parent
        self.grid(row=row, column=col)

        title = Label(self, text="Run(s) options", font=("Helvetica", 16),
                      justify="center")
        title.grid(row=row, column=col, columnspan=2)

        # this is the same job from root, so that settings can be changed
        self.job = self.parent.job
        self.runs = None

        # the respath and uri will only be used if the source of runs are
        # results - otherwise mostly ignored.
        self.respath = "~/Desktop"
        self.uri = "sqlite:///"

        runsl = Label(self, text="Runs: ")
        runsl.grid(row=row+1, column=col, pady=5, sticky=W)

        self.tmpruns = StringVar(self)
        self.tmpruns.set("All")

        # the first All seems as the default "title" setting to tell users
        # what the dropdown menu is for, the second one is then registered as
        # an option that won't dissapear after selection.
        runsom = OptionMenu(self, self.tmpruns, "All", "All", "Single", "List",
                            "Results", "Errors", command=self.selectRuns)
        runsom.grid(row=row+1, column=col+1, pady=5, sticky=W+E)

    def selectRuns(self,selection):
        """Callback that will execute everytime the drop-down menu selection
        changes. For each of the option in the menu here we define an action
        that will triger the appropriate additional menus required to configure
        the job.

        * All - the runs are allowed to be undefined, createjobs package will
          read the runlistAll file in $PHOTO_REDUX env var location for runs
        * Single - a pop-up with an entry field is displayed where only 1 run
          id is permitted
        * List - a pop-up with a textbox is displayed where a list of runs is
          given as a comma separated string
        * Results - a pop-up window that lets user select the DB from which
          jobs will be created.

        """
        if selection == "All":
            self.runs = None
            # we return early for this case to avoid spawning the toplevel
            return

        # otherwise we spawn another window which will hold the boxes where
        # user will fill in run or runs or pick the results DB
        top = Toplevel(self.parent)
        top.title(selection)
        top.geometry(utils.centerWindow(self.parent, 250,200))

        if selection == "Single":
            a = Label(top, text="Input a single run:", justify="left")
            a.grid(row=0, column=0, pady=10, padx=10)

            tempruns = Entry(top)
            tempruns.grid(row=1, column=0, pady=10, padx=10)

            c = Button(top, text="Ok",
                       command = lambda parent=top, runs=tempruns:
                       self.runFromSingle(parent, runs)
            )
            c.grid(row=2, column=0, pady=10, padx=10)

        elif selection == "List":
            a = Label(top, text="Input a list of runs.\n"+ \
                      "Separate each run with a coma.", justify="left")
            a.grid(row=0, column=0, pady=10, padx=5)

            tempruns = Text(top, height=4, width=30, pady=10, padx=10)
            tempruns.grid(row=1, column=0, pady=10, padx=10)

            b = Button(top, text="Ok",
                       command=lambda parent=top, runs=tempruns:
                           self.runsFromList(parent, runs))
            b.grid(row=2, column=0, pady=10)

        elif selection == "Results":
            respathVar = StringVar()
            respathVar.set(self.respath)
            respathVar.trace("w", lambda a, b, c, path=respathVar:
                             self.setResPath(a, b, c, path))

            uriVar = StringVar()
            uriVar.set(self.uri)
            uriVar.trace("w", lambda a, b, c, path=uriVar:
                         self.setUriPath(a, b, c, path))

            a = Label(top, text="Is this the correct DB:", justify="left")
            a.grid(row=0, column=0, pady=10, padx=10, columnspan=2)

            b = Entry(top, textvariable=uriVar)
            b.grid(row=1, column=0, columnspan=2, pady=10, padx=10)

            c = Label(top, text="Is this the correct path:", justify="left")
            c.grid(row=2, column=0, pady=10, padx=10, columnspan=2)

            d = Entry(top, textvariable=respathVar)
            d.grid(row=3, column=0, columnspan=2, pady=10, padx=10)

            e = Button(top, text="Reselect DB file",
                       command = lambda parent=top, updateVar=respathVar:
                       self.getResultsDBPath(parent, updateVar))
            e.grid(row=4, column=0, pady=10, padx=10)

            f = Button(top, text="Ok", command=lambda parent=top:
                       self.readRes(parent))
            f.grid(row=5, column=1)

    def runFromSingle(self, parent, runs):
        """Callback function for the case when a 'Single' run source is chosen.

        Parameters
        ----------
        parent - the parent window that contains the widget that registers this
            callback. This window will be destroyed at the end of this func.
        runs - an Entry or a Text widget from which the value will be read out
            as.

        """
        # see selection=="Single" in selectRuns method (above)
        try:
            self.runs =  [ int( runs.get() ) ]
        except ValueError:
            messagebox.showerror("Input Error", "You have inputed "+\
                                 "runs in an incorrect format!")
        parent.destroy()

    def setResPath(self, *tmp):
        """Callback 'observer' function used to track when the contents of an
        Entry changes. Specifically, tracks when the text value of an Entry
        used to select path to results database has changed. Updates the stored
        path to the results.

        Expects the arguments corresponding to the invocation of trace method
        of a StringVar.

        """
        # see selection=="Results" in selectRuns method (variable respathVar)
        self.respath = tmp[-1].get()

    def setUriPath(self, *tmp):
        """Callback 'observer' function used to track when the contents of an
        Entry changes. Specifically, tracks when the text value of an Entry
        used to select URI path to results database has changed. Updates the
        stored URI path to the results.

        Expects the arguments corresponding to the invocation of trace method
        of a StringVar.

        """
        # see selection=="Results" in selectRuns method (variable uriVar)
        self.uri = tmp[-1].get()

    def readRes(self, parent):
        """Callback that connects to the database given by the URI and path
        provided by the user and selects all existing Frames in that database.
        Selected frames are propagated to the runs attribute of the job object
        inherited from root.
        Expects to receive the parent window containing the binding object. The
        parent window is destroyed once all results are read in.
        """
        # see selection=="Results" in selectRuns method (OK button)
        import lfd.results as results
        results.connect2db(self.uri+self.respath)
        self.runs = results.Frame.query().all()
        parent.destroy()

    def runsFromList(self, parent, runs):
        """Callback function to convert a coma separated string of runs into a
        list of integers. Propagates the list to the job object inherited from
        root.
        Expects to receive the parent window containing the binding object. The
        parent window is destroyed once the conversion is complete.
        """
        # see selection=="List" in selectRuns method (OK button)
        intruns = None
        stringruns = runs.get(1.0, END).split(",")
        try:
            intruns = list(map(int, stringruns))
        except ValueError:
            messagebox.showerror("Input Error", "You have inputed "+\
                                 "runs in an incorrect format!")
        self.runs = intruns
        parent.destroy()


    def getResultsDBPath(self, parent, update):
        """Opens a file dialog window that enables user to navigate through the
        filesystem to select their desired database of results.

        Expects to receive the parent window of the binding object and a
        StringVar that is used to represent this path. It will update its value
        which triggers its trace method, which updates the class attribute used
        to store the path to the database.

        """
        # see selection=="Results" in selectRuns method (Button e)
        respath = filedialog.askopenfilename(parent=parent,
                                             title="Please select results DB.",
                                             initialdir=self.respath)
        if os.path.isfile(respath):
            update.set(respath)
        else:
            messagebox.showerror("Filename Error!", "Filename does not exist!")
