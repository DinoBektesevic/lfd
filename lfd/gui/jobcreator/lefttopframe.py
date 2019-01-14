from tkinter import *
from tkinter.ttk import *


class TopFrame(Frame):
    """Part of the LeftFrame of the GUI.
    Contains fields to select the:
    - number of jobs
    - queue type
    - wallclock limits
    - CPU time limits
    - processors per node limit (ppn)
    - command editor

    Requires a parent Frame that has access to Job object so that the settings
    can propagate to it.
    """
    def __init__(self, parent, row=0, col=0):
        Frame.__init__(self, parent)
        self.grid(row=row, column=col, pady=10)
        self.parent = parent

        title = Label(self, text = "Parameter options",
                      font=("UbuntuBold", 16), justify="center")
        title.grid(row=row, column=col, columnspan=2)

        self.job = self.parent.root.job

        #######################################################################
        #                    NUMBER OF JOBS SELECTOR
        #######################################################################
        numjobsl = Label(self, text="Num. Jobs: ")
        numjobsl.grid(row=row+1, column=col, pady=5, sticky=W)

        self.numjobs = Entry(self)
        self.numjobs.insert(0, self.job.n)
        self.numjobs.grid(row=row+1, column=col+1, pady=5, sticky=W+E)

        #######################################################################
        #                    QUEUE TYPE SELECTOR
        #######################################################################
        queuel = Label(self, text="Queue: ")
        queuel.grid(row=row+2, column=col, pady=5, sticky=W)

        self.queue = StringVar(self)
        self.queue.set(self.job.queue)

        queuedm = OptionMenu(self, self.queue, "standard", "standard",
                                "serial", "parallel", "xlarge")
        queuedm.grid(row=row+2, column=col+1, pady=5, sticky=W+E)

        #######################################################################
        #                    WALLCLOCK SELECTOR
        #######################################################################
        wallclockl= Label(self, text="Wallclock: ")
        wallclockl.grid(row=row+3, column=col, pady=3, sticky=W)

        self.wallclock = Entry(self)
        self.wallclock.insert(0, self.job.wallclock)
        self.wallclock.grid(row=col+3, column=col+1, pady=3,
                            sticky=W+E)

        #######################################################################
        #                    CPUTIME SELECTOR
        #######################################################################
        cputimel= Label(self, text="Cputime: ")
        cputimel.grid(row=row+4, column=col, pady=3, sticky=W)

        self.cputime = Entry(self)
        self.cputime.insert(0, self.job.cputime)
        self.cputime.grid(row=row+4, column=col+1, pady=3, sticky=W+E)

        #######################################################################
        #                    PPN SELECTOR
        #######################################################################
        ppnl= Label(self, text="Processors per node: ")
        ppnl.grid(row=row+5, column=col, pady=5, sticky=W)

        self.ppn = StringVar(self)
        self.ppn.set(self.job.ppn)

        queueoptions = map(str, range(1, 13))
        queuedm = OptionMenu(self, self.ppn, *queueoptions)
        queuedm.grid(row=row+5, column=col+1, pady=5, sticky=W+E)

        #######################################################################
        #                    COMMAND SELECTOR
        #######################################################################
        commandl= Label(self, text="Command: python -c \n \"import "+
                        "detecttrails as dt;")
        commandl.grid(row=row+7, column=col, pady=5, sticky=W)

        self.command = Text(self, height=6, width=35)
        self.command.insert(END, self.job.command[38:-2])
        self.command.grid(row=row+7, column=col+1, pady=5, sticky=W+E)

    def getn(self):
        """Reads the current value from the Entry for number of jobs and
        performs basic sanity checks. Will raise an error if the value in the
        box is unreadable or if the number of jobs is zero.
        Technically all these boxes should have verifiers but I can't really be
        bothered and this one is the one that will likely get changed the most.
        """
        try:
            n = int(self.numjobs.get())
        except ValueError as e:
            messagebox.showerror("Incorrect Format", e)
        if n==0:
            messagebox.showerror("Input Error", "Number of jobs "+\
                                   "can't be 0")
        else:
            return n

    def getcommand(self):
        """Reads the curent command TextBox and reduces it to a form compatible
        with the createjobs module. Separating lines in the TextBox by using
        <Return> key is allowed.
        """
        # using <Return> key to separate lines is allowed, but in the createjob
        # module the command has to be entered as a semicolon separated string.
        # So the newlines are replaced by semicolons and then all doubled-up
        # semicolons (if users separated their lines by both ; and <Return>)
        # are reduced to a single semicolon. It's a bit hackish which is why
        # this is not a 'feature' of createjobs module.
        command = self.command.get(1.0, END)
        cmnd = command[:-1]
        cmnd = cmnd.replace("\n", ";")
        cmnd = cmnd.replace(";;", ";")
        return self.job.command[:38] + cmnd + '"\n'
