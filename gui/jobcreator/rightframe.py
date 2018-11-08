import os

from tkinter import *
from tkinter.ttk import *

from lfd import createjobs

class RightFrame(Frame):
    """RightFrame of the jobcreator gui. Contains the template from which jobs
    will be created. The template is not editable unless its state is changed
    by the eddittemplate function found in the leftbotframe module.
    """
    def __init__(self, parent):
        Frame.__init__(self, parent, relief=RAISED, borderwidth=1)
        self.pack(side=RIGHT, fill=BOTH, expand=1)

        generictmpltpath = os.path.split(createjobs.__file__)[0]
        generictmpltpath = os.path.join(generictmpltpath, "generic")
        template = open(generictmpltpath)

        self.templatetext = template.read()

        self.activetmpl = Text(self)
        self.activetmpl.pack(side=LEFT, expand=True, fill=BOTH)

        scrollw = Scrollbar(self)
        scrollw.pack(side=LEFT, fill=Y)
        scrollw.config(command=self.activetmpl.yview)

        self.activetmpl.config(yscrollcommand=scrollw.set)

        self.activetmpl.insert(END, self.templatetext)
        self.activetmpl.config(state=DISABLED)

    def getTemplate(self):
        return self.activetmpl.get(1.0, END)
