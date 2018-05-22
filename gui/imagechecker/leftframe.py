from Tkinter import *
from ttk import *

from PIL import Image, ImageTk
import os

class LeftFrame(Frame):
    def __init__(self, parent):
        Frame.__init__(self, relief=RAISED, borderwidth=1)
        self.pack(side=LEFT, fill=BOTH, expand=1)
        self.root = parent
        self.data = parent.data
        
        self.canvas = Canvas(self, width=800, height=600)
        self.canvas.bind("<Button-1>", self.lmb)
        self.canvas.bind("<Button-3>", self.rmb)
        self.canvas.pack(fill=BOTH, expand=1)

    def update(self):
        curimg = self.data.getImage()

        if curimg is not None:
            self.canvas.delete("all")
            tmpimg = Image.open(curimg)
            self.img = ImageTk.PhotoImage(tmpimg)
            self.canvas.create_image(0, 0, image=self.img, anchor=NW)#self.canvas.winfo_height(),
#                                     anchor=SW, image=self.img)
            
            curimgdata = self.data.getImageData()
            if curimgdata is not None:
                self.drawline(curimgdata)
        else:
            tmpimg = Image.open(os.path.join(os.getcwd(),
                                     "gui/imagechecker/noimage.png"))
            self.img = ImageTk.PhotoImage(tmpimg)
            self.canvas.create_image(0, 0, image=self.img, anchor=NW)

    def lmb(self, event):
        x1,y1,x2,y2 =  self.canvas.coords(self.drawnline)
        newcoords = [event.x, event.y, x2, y2]
        self.canvas.coords(self.drawnline, *newcoords)
        self.updateLine(event.x, event.y, "1")

    def rmb(self, event):
        x1,y1,x2,y2 =  self.canvas.coords(self.drawnline)
        newcoords = [x1, y1, event.x, event.y]
        self.canvas.coords(self.drawnline, *newcoords)
        self.updateLine(event.x, event.y, "2")

    def updateLine(self, sx, sy, which):
        y2 = self.data.getImageData().y2
        x = sx*2.56
        y1 = sy*2.5628227194492257
        if which == "1":
            y = (y1+y2)/2.0
            self.data.updateImageData({"x1":x, "y1":y})
        elif which == "2":
            y = y1
            self.data.updateImageData({"x2":x, "y2":y})
        #use these to check if db is actually updated:
        #self.canvas.delete(self.drawnline)
        #self.drawline(self.data.getImageData())
        
    def drawline(self, curimg):
        x1, y0 = curimg.x1, curimg.y1
        x2, y2 = curimg.x2, curimg.y2
        y1 = 2*y0-y2
        
        sx1, sy1 = x1/2.56, y1/2.5628227194492257
        sx2, sy2 = x2/2.56, y2/2.5628227194492257
        
        #m = float(sy2-sy1)/float(sx2-sx1)
        #b = sy1 - m*sx1

        self.drawnline = self.canvas.create_line(sx1, sy1, sx2, sy2,
                                                 fill="red", width=1)
        
