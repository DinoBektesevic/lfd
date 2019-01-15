#!/usr/bin/python
# -*- coding: utf-8 -*-
from .leftframe import LeftFrame
from .rightframe import RightFrame
from lfd.gui import utils
from tkinter import *
from tkinter import ttk

from tkinter import Label
from tkinter import filedialog

from lfd.gui.imagechecker.databrowser import ImageBrowser, EventBrowser

class ImageChecker(Tk):
    """GUI app that allows for visual inspection of Events. To run the app
    instantiate the class and run its mainloop method or invoke run function
    located in this module.

    The App itself does not manage the data. Data loading and management is
    handled by the EventBrowser class stored in self.data attribute.

    The GUI consits of 2 Frames - left and right. Left frame is used to display
    information on the Event and the right hand side displays the image
    representation of the Event if availible. GUI binds the following shortcut
    keys:

    * <Left> - move to previous image without saving any changes
    * <Right> - continue to the next image without saving any changes
    * <Up> - continue to the next image but set the verified and false positive
      flags of the current Event to True and False respectively. Persist the
      changes to the DB
    * <Down> - continue to the next image but set the verified and false
      positive flags of the current Event to True and True respectively and
      persist the change to the DB
    * <LMB> - when clicked on the image will move the first point of the linear
      feature to that location and persist the changes to the database
    * <RMB> - when clicked on the image will move the second point of the
      linear feature to that location and persist the changes to the database

    The colors in the data table on the right frame indicate the following:

    * Yellow - the Event was never visually inspected
    * Green - the Event was visually inspected and confirmed as true
    * Red - the Event was visually inspected and was determined to be a false
      detection

    """
    def __init__(self):
        """There are several configurable parameters that are imporant for this
        class:

        * resize_x - the reduction factor describing how much has the width
          been reduced from the original to the displayed image.
        * resize_y - the reduction factor describing how much has the height
          reduced between the original and displayed image.

        Optionally you can rebind the key functionality or change the color
        scheme of the table in the top right by editing the TopRight Frame of
        the rightFrame. Additionally, the displayed keys in the TopRight Frame
        are editable through that class.
        """
        Tk.__init__(self)
        self.geometry(utils.centerWindow(self, 1100, 600))
        self.title("Trail Sorter")

        self.respath = "~/Desktop"
        self.imgpath = "~/Desktop"

        self.resize_x = 2.56
        self.resize_y = 2.5628227194492257

        self.data = EventBrowser() #ImageBrowser()

        self.leftFrame = LeftFrame(self)
        self.rightFrame = RightFrame(self)

        self.bind('<Left>', self.rightFrame.bottomRight.previmg)
        self.bind('<Right>', self.rightFrame.bottomRight.nextimg)
        self.bind("<Up>", self.rightFrame.bottomRight.true)
        self.bind("<Down>", self.rightFrame.bottomRight.false)

        self.initGUI()

    def initGUI(self):
        """Will initialize the GUI for the first time by prompting user for the
        location of the Database to connect to and the location of the images.
        The order of operations here is not particulary important because the
        update function will be called to clean and redisplay everything on the
        screen.
        """
        self.initResults()
        self.initImages()
        self.update()

    def initResults(self):
        """Prompt user for the database file from which Events will be read."""
        path = filedialog.askopenfilename(parent=self,
                                          title="Please select results database...",
                                          initialdir=self.respath)
        if path is not None:
            try:
                self.data.initEvents("sqlite:///"+path)
            except (OSError, IndexError, FileNotFoundError):
                self.rightFrame.failedEventLoadScreen()
        else:
            self.rightFrame.failedEventLoadScreen()

    def initImages(self):
        """Prompt user for the directory containing all the images in the DB."""
        path = filedialog.askopenfilename(parent=self,
                                          title="Please select image database...",
                                          initialdir=self.imgpath)
        if path is not None:
            try:
                self.data.initImages("sqlite:///"+path)
            except (OSError, IndexError, FileNotFoundError):
                self.leftFrame.failedImageLoadScreen()
        else:
            self.leftFrame.failedImageLoadScreen()

    def update(self):
        """Redraw right and left Frames. The order is important, updating left
        frame before loading new event will not load the data required to draw
        the line over the canvas.
        """
        self.rightFrame.update()
        self.leftFrame.update()

    def failedUpdate(self):
        """Redraw left and right Frames and display their failure screens."""
        self.rightFrame.failedEventLoadScreen()
        self.leftFrame.failedImageLoadScreen()


def run():
    """Instantiate the ImageChecker App and runs its GUI."""
    app = ImageChecker()
    app.mainloop()
