from Tkinter import *
import tkFileDialog
import tkMessageBox
from ttk import *

import createjobs as cj
import threading
import Queue
import time
from gui.utils import utils

class MidFrame(Frame):
    def __init__(self, parent, row=1, col=0):
        Frame.__init__(self, parent)
        self.parent = parent
        self.grid(row=row, column=col)
                
        title = Label(self, text="Run(s) options",
                      font=("Helvetica", 16), justify="center")
        title.grid(row=row, column=col, columnspan=2)

        self.jobs = self.parent.root.job

        runsl = Label(self, text="Runs: ")
        runsl.grid(row=row+1, column=col, pady=5, sticky=W)
        
        self.tmpruns = StringVar(self)
        self.tmpruns.set("All")
        
        runsom = OptionMenu(self, self.tmpruns, "All", "Single",
                            "List", "Results", "Errors",
                            command=self.selectRuns)
        runsom.grid(row=row+1, column=col+1, pady=5, sticky=W+E) 

    def selectRuns(self,selection):
        if selection == "All":
            self.runs = None
            return
            
        top = Toplevel(self.parent)
        top.title(selection)
        top.geometry(utils.centerWindow(self.parent, 250,200))
        
        if selection == "Single":
            a = Label(top, text="Input a single run:", justify="left")
            a.grid(row=0, column=0, pady=10, padx=10)
            
            tempruns = Entry(top)
            tempruns.grid(row=1, column=0, pady=10, padx=10)
            
            c = Button(top, text="Ok",
                       command=lambda parent=top, runs=tempruns:
                           self.runFromSingle(parent, runs))
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
            self.respath = "~/Desktop"
            
            tmprespath = StringVar()
            tmprespath.set(self.respath)
            tmprespath.trace("w", lambda a, b, c, path=tmprespath:
                             self.setResPath(path))
            
            a = Label(top, text="Is this the correct path:",
                      justify="left")
            a.grid(row=0, column=0, pady=10, padx=10, columnspan=2)

            b = Entry(top, textvariable=tmprespath)
            b.grid(row=1, column=0, columnspan=2, pady=10, padx=10)

            c = Button(top, text="Reselect folder",
                       command=lambda parent=top, update=tmprespath:
                                self.getresfolder(parent, update))
            c.grid(row=2, column=0, pady=10, padx=10)

            d = Button(top, text="Ok", command=lambda parent=top:
                                               self.readRes(parent))
            d.grid(row=2, column=1)

    def setResPath(self, *tmp):
        self.respath = tmp[-1].get()
        
    def readRes(self, parent):
        self.readResults()
        parent.destroy()
        
    def runFromSingle(self, parent, runs):
        try:
            self.jobs.runs =  [ int( runs.get() ) ]
        except ValueError:
            tkMessageBox.showerror("Input Error", "You have inputed "+\
                                   "runs in an incorrect format!")
        parent.destroy()
        
    def runsFromList(self, parent, runs):
        stringruns = runs.get(1.0, END).split(",")
        try:
            intruns = map(int, stringruns)
        except ValueError:
            tkMessageBox.showerror("Input Error", "You have inputed "+\
                                   "runs in an incorrect format!")
        self.jobs.runs = intruns
        parent.destroy()

        
    def getresfolder(self, parent, update):
        respath = tkFileDialog.askdirectory(parent=parent,
                   title="Please select results folder...",
                   initialdir=self.respath)
        if not respath:
            pass
            #raise ValueError("Invalid results path.")
        else:
            update.set(respath)
        
    def readResults(self):
        """
        Results module can take its time reading in results. To amortize
        the wait a progress bar is displayed. Progress bar requires
        threading. Tkinter is a single threaded app, therefore a kernel
        function read_results is called that doesn't edit Tk instance.
        Function freezes the app untill thread finishes.
        Instance is edited by adding a Results instance as attribute
        res.
        """
        respath = self.respath
        queue = Queue.Queue()

        popup = Toplevel(self.parent)
        startx = self.parent.winfo_rootx()
        starty = self.parent.winfo_rooty()
        popup.geometry(utils.centerWindow(self.parent, 400, 50))

        Label(popup, text="Reading results, please wait... \n"+
                          "Depending on number of results "+
                          "this could take up to a minute.").pack(
                          fill=BOTH, expand=1)
        
        loadingbar = Progressbar(popup, orient='horizontal',
                                     length=400, mode='indeterminate')
        loadingbar.pack(fill=BOTH, expand=1)
        loadingbar.start(10)
        
        t1=threading.Thread(target=utils.read_results,
                            args=(queue, respath))

        t1.start()
        while t1.is_alive():
            time.sleep(0.1)
            #print("sleep")
            loadingbar.step(1)
            loadingbar.update_idletasks()
        t1.join()
        popup.destroy()

        self.runs = queue.get()


