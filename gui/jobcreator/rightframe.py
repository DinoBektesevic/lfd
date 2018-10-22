import os

from tkinter import *
from tkinter.ttk import *

from lfd import createjobs

class RightFrame(Frame):
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
