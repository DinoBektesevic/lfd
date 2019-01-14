from tkinter import *
from tkinter.ttk import *
import os

from tkinter import filedialog, messagebox

from lfd.gui.utils import expandpath


class BotFrame(Frame):
    """Bottom part of the LeftFrame of the GUI. Handles all of the paths
    involved in the creation of a Job and updates the template in RightFrame
    when the template path changes.

    """
    def __init__(self, parent, row=2, col=0):
        Frame.__init__(self, parent)
        self.grid(row=row, column=col, pady=10)
        self.parent = parent

        title = Label(self, text="Enviroment options",
                      font=("Helvetica", 16), justify="center")
        title.grid(row=row, column=col, columnspan=2)

        self.job = self.parent.root.job

        #######################################################################
        #            Path to where job DQS files will be produced
        #######################################################################
        self.jobsavepath = StringVar()
        self.jobsavepath.set(self.job.save_path)

        a = Button(self, text="Select Save Folder", width=15,
                   command = self.setSavePathWithPrompt)
        a.grid(row=row+1, column=col, pady=5, sticky=W)

        b = Entry(self, textvariable=self.jobsavepath, width=25)
        b.grid(row=row+1, column=col+1, pady=5, sticky=W+E)

        #######################################################################
        #            Path to where the current template is located
        #######################################################################
        self.tmpltpath = StringVar(self)
        self.tmpltpath.set(self.job.template_path)
        self.tmpltpath.trace("w", self.setTemplatePath)

        c = Button(self, text="Select template", width=15,
                   command = self.setTemplatePathWithPrompt)
        c.grid(row=row+2, column=col, pady=5, sticky=W)

        d = Entry(self, textvariable=self.tmpltpath, width=25)
        d.grid(row=row+2, column=col+1, pady=5, sticky=W+E)

        #######################################################################
        #            Path to where the results will be saved on the cluster
        #######################################################################
        respathl= Label(self, text="Results save folder: ")
        respathl.grid(row=row+6, column=col, pady=3, sticky=W)

        self.respath = Entry(self)
        self.respath.insert(0, self.job.res_path)
        self.respath.grid(row=row+6, column=col+1, pady=3, sticky=W+E)


        #######################################################################
        #            Edit template
        #######################################################################
        e = Button(self, text="Edit template", width=15,
                   command = self.editTemplate)
        e.grid(row=row+3, column=col, pady=5, sticky=W+E)

        self.savetmpbtn = Button(self, text="Save template",
                                   width=15, state=DISABLED,
                                   command=self.saveTemplate)
        self.savetmpbtn.grid(row=row+3, column=col+1, pady=5,
                               sticky=W+E)

    def setSavePathWithPrompt(self):
        """Callback that will spawn a directory selector through which a new
        path, where the job DQS files will be saved, can be selected.
        """
        newpath = filedialog.askdirectory(parent=self,
                                          title="Please select save destination.",
                                          initialdir=self.jobsavepath)
        self.jobsavepath.set(newpath)

    def setTemplatePath(self, *args):
        """Callback that will track the Entry box of the template path and upon
        modification will cause the RightFrame template display to reload the
        new template.
        """
        newpath = self.tmpltpath.get()
        self.updateTemplatePath(newpath)

    def setTemplatePathWithPrompt(self):
        """Callback that will spawn a file selector window through which a new
        template can be selected. See setTemplatePath.
        Will cause an update of the RightFrame to redisplay the newly selected
        template.

        """
        initdir = os.path.dirname(self.tmpltpath.get())
        newpath = filedialog.askopenfilename(parent=self,
                                             title="Please select a template.",
                                             initialdir=self.tmpltpath)
        self.tmpltpath.set(newpath)
        self.updateTemplatePath(newpath, showerr=True)

    def updateTemplatePath(self, path, showerr=False):
        """Updates the RightFrame's template display and replaces the current
        content with content read from a file at the provided path. If showerr
        is supplied an error will be raised if the given path does not exist.
        This is useful if the directory will be created after the path selection
        or if the update is called from a callback tied to a StringVar/Entry
        trace methods as a way to silence errors untill the full path has been
        manually inputed.

        Parameters
        ----------
        path : str
          path to the new template
        showerr : bool
          if False no error will be raised even if path does not exist, usefull
          when error needs to be raised later, on a callback initiated by a
          button click

        """
        tmppath = expandpath(path)
        activetmpl = self.parent.root.rightFrame.activetmpl

        if tmppath[0] and os.path.isfile(tmppath[1]):
            activetmpl.config(state=NORMAL)
            activetmpl.delete(1.0, END)
            activetmpl.insert(1.0, open(tmppath[1], "r").read())
            activetmpl.config(state=DISABLED)
            self.job.template_path = tmppath[1]
        else:
            if showerr:
                messagebox.showerror(("Input Error. Input path does not exist "
                                      "or is a folder! {}".format(path)))
            activetmpl.config(state=NORMAL)
            activetmpl.delete(1.0, END)
            activetmpl.config(state=DISABLED)

    def editTemplate(self):
        """A callback of a Button action that will change the state of the
        RightFrame Text box and make it editable.

        """
        self.savetmpbtn.config(state=NORMAL)
        self.activetmpl = self.parent.root.rightFrame.activetmpl
        self.activetmpl.config(state=NORMAL)

    def saveTemplate(self):
        """A Button callback that will save the current template to a file.
        Spawns a file dialog to retrieve the save location. Changes the state
        of the RightFrame Text box back to un-editable.
        
        """
        self.savetmpbtn.config(state=DISABLED)
        self.activetmpl.config(state=DISABLED)

        filename = filedialog.asksaveasfilename(initialdir=self.tmpltpath,
                                                confirmoverwrite=True)
        f = open(filename, "w")
        for line in self.activetmpl.get(1.0, END):
            f.write(line)
        f.close()

        self.tmpltpath.set(filename)
