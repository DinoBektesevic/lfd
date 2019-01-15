from tkinter import *
from tkinter.ttk import *

from lfd.gui.imagechecker.topright import TopRight
from lfd.gui.imagechecker.botright import BottomRight

class RightFrame(Frame):
    """Represents the right part of the frame containing all the action buttons
    and displaying the data of he Event from the database. The right frame is
    split into two sub-frames one used to display the Event in question and the
    other one containing all the action elements (next, true, false, previous,
    find, change data source etc.)

    """
    def __init__(self, parent):
        Frame.__init__(self, relief=RAISED, borderwidth=1)
        self.pack(side=RIGHT, fill=BOTH, expand=1)
        self.root = parent
        self.data = parent.data

        self.topRight = TopRight(self)
        self.bottomRight = BottomRight(self)

    def update(self):
        """Calls the update methods of each subframe in the correct order and
        handles failures.

        """
        # in this case it's only the top right frame, displaying the data, that
        # needs to be updated as the action elements need to stay put.
        if self.data.event is None:
            self.failedEventLoadScreen()
        else:
            self.topRight.updateImageData()

    def failedEventLoadScreen(self):
        """Redraws the right frame displaying appropriate error messages in
        case of failure.

        """
        # realistically this consists only of clearing the table displaying the
        # prvious Event information and setting a label with error message.
        for widget in self.topRight.winfo_children():
            widget.destroy()

        Label(self.topRight, background="red2", font=("Helvetica", 20),
              text="NO IMAGE DATA\nFOUND").grid(row=0, columnspan=2, padx=50,
                                                pady=(50,0))

