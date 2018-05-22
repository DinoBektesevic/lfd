from Tkinter import *
from ttk import *
import tkFileDialog, tkMessageBox

from gui.utils import expandpath
import os

class BotFrame(Frame):
    def __init__(self, parent, row=2, col=0):
        Frame.__init__(self, parent)
        self.grid(row=row, column=col, pady=10)
        self.parent = parent
        
        title = Label(self, text="Enviroment options",
                      font=("Helverica", 16), justify="center")
        title.grid(row=row, column=col, columnspan=2)

        self.job = self.parent.root.job

############# SAVEPATH
        self.tmpsavepath = StringVar()
        self.tmpsavepath.set(self.job.save_path)
        self.tmpsavepath.trace("w", self.setSavePath)   
        
        a = Button(self, text="Select Save Folder", width=15,
                   command = self.getSavePath)
        a.grid(row=row+1, column=col, pady=5, sticky=W)
        
        b = Entry(self, textvariable=self.tmpsavepath, width=25)
        b.grid(row=row+1, column=col+1, pady=5, sticky=W+E)

############ TEMPLATEPATH
        self.templpath = StringVar(self)
        self.templpath.set(self.job.template_path)
        self.templpath.trace("w", self.setTemplatePath)

        c = Button(self, text="Select template", width=15,
                   command = self.getTemplatePath)
        c.grid(row=row+2, column=col, pady=5, sticky=W)

        d = Entry(self, textvariable=self.templpath, width=25)
        d.grid(row=row+2, column=col+1, pady=5, sticky=W+E)

############ EDITTEMPLATE
        e = Button(self, text="Edit template", width=15,
                   command = self.edittemplate)
        e.grid(row=row+3, column=col, pady=5, sticky=W+E)

        self.savetmpbtn = Button(self, text="Save template",
                                   width=15, state=DISABLED,
                                   command=self.savetmpl)
        self.savetmpbtn.grid(row=row+3, column=col+1, pady=5,
                               sticky=W+E)



    def setSavePath(self, *args):
        newpath = self.tmpsavepath.get()
        self.updateSavePath(newpath)        
        
    def getSavePath(self):
        newpath = tkFileDialog.askdirectory(parent=self,
                   title="Please select save destination...",
                   initialdir=self.job.save_path)
        self.tmpsavepath.set(newpath)
        self.updateSavePath(newpath, showerr=True)

    def updateSavePath(self, path, showerr=False):
        tmppath = expandpath(path)
        if tmppath[0]:
            self.job.save_path=tmppath[1]
        else:
            self.job.save_path="/"
            if showerr:
                tkMessageBox.showerror("Input Error",
                                       "Input path does not " + \
                                       "exist! \n" + path)
    
    def setTemplatePath(self, *args):
        newpath = self.templpath.get()
        self.updateTemplatePath(newpath)
        
    def getTemplatePath(self):
        initdir = os.path.dirname(self.job.template_path)
        newpath = tkFileDialog.askopenfilename(parent=self,
                   title="Please select a template...",
                   initialdir=initdir)
        self.templpath.set(newpath)
        self.updateTemplatePath(newpath, showerr = True)

    def updateTemplatePath(self, path, showerr=False):
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
                tkMessageBox.showerror("Input Error",
                                       "Input path does not exist " +\
                                       "or is a folder! \n" + path)
            activetmpl.config(state=NORMAL)
            activetmpl.delete(1.0, END)
            activetmpl.config(state=DISABLED)       

            
    def edittemplate(self):
        self.savetmpbtn.config(state=NORMAL)
        self.activetmpl = self.parent.root.rightFrame.activetmpl
        self.activetmpl.config(state=NORMAL)
        
    def savetmpl(self):
        self.savetmpbtn.config(state=DISABLED)
        self.activetmpl.config(state=DISABLED)
        
        filename = tkFileDialog.asksaveasfilename(
            initialdir=self.job.template_path, confirmoverwrite=True)
        f = open(filename, "w")
        for line in self.activetmpl.get(1.0, END):
            f.write(line)
        f.close()

        self.templpath.set(filename)
        

