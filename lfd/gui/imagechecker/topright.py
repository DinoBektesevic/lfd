from tkinter import *
from tkinter.ttk import *
from lfd.gui.utils import multi_getattr

class TopRight(Frame):
    """Top right part of the right frame. Used to display the data on currently
    selected Event.

    Contains several customizable attributes such as:

    * unverified_color- the color to display when the Event's verified flag
      is False (DarkGoldenrod1 by default)
    * falsepositive_color - the color to display when the Event is verified as
      false positive (red by default)
    * positive_color - color to display when the Event is verified as a
      positive detection (DarkOliveGreen3)
    * displayKeys - keys that will be displayed in the information table of the
      Event. Any valid column name of Event is accepted, by default will be:
      `[run, camcol, filter, field, frame.t.iso]`

    """
    def __init__(self, parent):
        Frame.__init__(self, width=300)
        self.pack(side=TOP, fill=BOTH)
        #self.grid_propagate(False)

        self.unverified_color =  "DarkGoldenrod1"
        self.falsepositive_color = "red"
        self.positive_color = "DarkOliveGreen3"

        self.parent = parent
        self.data = parent.root.data

        self.displayKeys = ["run", "camcol", "filter", "field", "frame.t.iso"]

    def updateImageData(self):
        """Clears the currently displayed table, and draws a new table
        displaying the data of currently loaded Event. If there is no Event
        currently loaded, raises an IndexError (since the index of current
        Event is None).

        """
        # This is repeated in the failedEventLoadScreen and here so that the
        # order of the calls to these two functions would not matter
        for widget in self.winfo_children():
            widget.destroy()

        event = self.data.event
        # spacer between top of window and table
        Label(self).grid(row=0, columnspan=2, padx=50, pady=13)

        for row, key in enumerate(self.displayKeys, 1):
            if not event.verified:
                color = self.unverified_color
            elif event.false_positive:
                color = self.falsepositive_color
            else:
                color = self.positive_color

            Label(self, text=key, relief=RIDGE, width=10,
                  background=color).grid(row=row, column=0, padx=(25, 0))
            Label(self, text=multi_getattr(event, key), relief=RIDGE, width=25,
                  background=color).grid(row=row, column=1, padx=(0, 40))

            row+=1

        #spacer between topright and botright
        Label(self).grid(row=0, columnspan=2, padx=50, pady=13)
