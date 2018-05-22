#!/usr/bin/python
# -*- coding: utf-8 -*-
from Tkinter import *
from ttk import *
from Tkinter import Button, Label


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

        curres = self.data.getImageData()
        
        if curres is not None:
            r = 1

            #spacer from the top of the frame
            Label(self).grid(row=0, columnspan=2, padx=50, pady=13)

            for i in self.data.keys[:5]:
                color = "light steel blue"
                if i == "false_positive":
                    if curres.false_positive == "1":
                        color = "red"
                    else:
                        color = "DarkOliveGreen3"
                        
                Label(self, text=i, relief=RIDGE, width=10, bd=1,
                      bg="light steel blue").grid(
                          row=r,column=0, padx=(50, 0))
                Label(self, text=getattr(curres, i), width=15,  bd=1,
                      relief=RIDGE, bg=color).grid(
                          row=r,column=1, padx=(0, 80))
                r+=1

            #spacer between topright and botright
            Label(self).grid(row=0, columnspan=2, padx=50, pady=13)
            
        else:
            Label(self, bg="red2", font=("Helvetica", 20),
                  text="NO IMAGE DATA\nFOUND").grid(row=0,
                                                    columnspan=2,
                                                    padx=50, pady=(50,0))
