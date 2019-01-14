import os

from tkinter import *
from tkinter.ttk import *

from PIL import Image, ImageTk


class LeftFrame(Frame):
    """Represents the left frame of the GUI. Contains the Canvas within which
    the image is displayed and additional functionality that allows the users
    to chage the line parameters, and persist those changes to the DB. The
    following mouse actions are bound to the canvas:

    * <Button-1> - on click of the left mouse button (LMB) will bind the
      current coordinates of the mouse pointer and convert the on-canvas
      coordinates to the frame-coordinate system using the resize_x and
      resize_y resizing reduction factors defined in the root class of the app.
      These converted coordinates are then set as a new x1, y1 coordinates of
      the p1 Point of the Event.
    * <Button-3> - on right mouse button (RMB) click records the coordinates of
      the pointer, scales them to frame coord. sys. and persists the change as
      the x2, y2 coordinates of p2 Point of the Event.
    """
    def __init__(self, parent):
        Frame.__init__(self, relief=RAISED, borderwidth=1)
        self.pack(side=LEFT, fill=BOTH, expand=1)
        self.root = parent
        self.data = parent.data

        tmppath = os.path.split(__file__)[0]
        failimg = Image.open(os.path.join(tmppath, "noimage.png"))
        self.img = failimg
        self.drawnline = None

        self.canvas = Canvas(self, width=800, height=600)
        self.canvas.bind("<Button-1>", self.lmb)
        self.canvas.bind("<Button-3>", self.rmb)
        self.canvas.pack(fill=BOTH, expand=1)

        self.x1 = None
        self.y1 = None
        self.x2 = None
        self.y2 = None

    def update(self):
        """Updates the canvas and handles the errors."""
        if self.data.image is not None:
            self.canvas.delete("all")
            tmpimg = Image.open(self.data.image.imgpath)
            # a reference to the image has to be kept, otherwise img is lost
            self.img = ImageTk.PhotoImage(tmpimg)
            self.canvas.create_image(0, 0, image=self.img, anchor=NW)

            try:
                self.drawline()
            except AttributeError:
                self.drawline(delete=True)
                pass
        else:
            self.failedImageLoadScreen()

    def failedImageLoadScreen(self):
        """Clears the canvas and displays the Error image."""
        self.canvas.delete("all")
        tmppath = os.path.split(__file__)[0]
        tmpimg = Image.open(os.path.join(tmppath, "noimage.png"))
        # a reference to the image has to be kept, otherwise img is lost
        self.img = ImageTk.PhotoImage(tmpimg)
        self.canvas.create_image(0, 0, image=self.img, anchor=NW)

    def lmb(self, event):
        """Callback, records and updates the x1, y1 coordinates of the Event."""
        x1,y1,x2,y2 =  self.canvas.coords(self.drawnline)
        newcoords = [event.x, event.y, x2, y2]
        self.canvas.coords(self.drawnline, *newcoords)
        self.updateLine(event.x, event.y, "1")

    def rmb(self, event):
        """Callback, records and updates the x2, y2 coordinates of the Event."""
        x1,y1,x2,y2 =  self.canvas.coords(self.drawnline)
        newcoords = [x1, y1, event.x, event.y]
        self.canvas.coords(self.drawnline, *newcoords)
        self.updateLine(event.x, event.y, "2")

    def updateLine(self, sx, sy, which):
        """Function that will scale the canvas coordinates to correspond to the
        frame-coordinate system and sets the new coordinates as the p1 or p2
        coordinates of the Event.
        It is important that the resize scaling factors used in the App are
        correct if the output is to be trusted.

        Parameters
        ----------
        sx : int
          x coordinate in canvas coordinate system
        sy : int
          y coordinate in canvas coordinate system
        which : str
          used to determine whether the coordinates belong to point 1 or point
          2 of the Event. Either '1' or '2'.
        """
        #y2 = self.data.event.y2
        x = sx*self.root.resize_x
        y = sy*self.root.resize_y
        if which == "1":
            #y = (y1+y2)/2.0
            self.data.event.x1 = x
            self.data.event.y1 = y
        elif which == "2":
         #   y = y1
            self.data.event.x2 = x
            self.data.event.y2 = y
        #use these to check if db is actually updated:
        #self.canvas.delete(self.drawnline)
        #self.drawline(self.data.getImageData())

    def drawline(self, delete=False):
        """Draws the line defined by the current Event's Points p1 and p2. If
        delete is set to True then it will delete any existing line. It is
        important that the resize scaling factors are correctly set.
        """
        if delete:
            sx1, sy1, sx2, sy2 = 0, 0, 0, 0
        else:
            x1, y1 = self.data.event.x1, self.data.event.y1
            x2, y2 = self.data.event.x2, self.data.event.y2
            #y1 = 2*y0-y2

            sx1, sy1 = x1/self.root.resize_x, y1/self.root.resize_y
            sx2, sy2 = x2/self.root.resize_x, y2/self.root.resize_y

            #m = float(sy2-sy1)/float(sx2-sx1)
            #b = sy1 - m*sx1

        self.drawnline = self.canvas.create_line(sx1, sy1, sx2, sy2,
                                                 fill="red", width=1)
