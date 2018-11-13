from tkinter import *
from tkinter.ttk import *

class TopRight(Frame):
    def __init__(self, parent):
        Frame.__init__(self, width=300)
        self.pack(side=TOP, fill=BOTH)
        #self.grid_propagate(False)

        self.parent = parent
        self.data = parent.root.data

    def updateImageData(self):
        for widget in self.winfo_children():
            widget.destroy()

        try: self.data.loadEvent()
        except IndexError: self.parent.failedEventLoadScreen()

        if self.data.event is not None:
            e = self.data.event
            displayKeys = ["run", "camcol", "filter", "field", "t"]
            displayVals = [e.run, e.camcol, e.filter, e.field, e.frame.t.iso]
            row = 1

            #spacer from the top of the frame
            Label(self).grid(row=0, columnspan=2, padx=50, pady=13)
            for key, val in zip(displayKeys, displayVals):
                color = "light steel blue"
#                if i == "false_positive":
#                    if curres.false_positive == "1":
#                        color = "red"
#                    else:
#                        color = "DarkOliveGreen3"

                Label(self, text=key, relief=RIDGE, width=10,
                      background=color).grid(row=row, column=0, padx=(25, 0))

                Label(self, text=val, relief=RIDGE, width=25,
                      background=color).grid(row=row, column=1, padx=(0, 40))
                row+=1

            #spacer between topright and botright
            Label(self).grid(row=0, columnspan=2, padx=50, pady=13)
        else:
            self.parent.failedEventLoadScreen()
