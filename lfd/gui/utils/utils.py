import os

from tkinter import *
from tkinter.ttk import *

import lfd.results as results

def center(toplevel):
    toplevel.update_idletasks()
    w = toplevel.winfo_screenwidth()
    h = toplevel.winfo_screenheight()
    size = tuple(int(_) for _ in toplevel.geometry().split('+')[0].split('x'))
    x = w/2 - size[0]/2
    y = h/2 - size[1]/2
    toplevel.geometry("%dx%d+%d+%d" % (size + (x, y)))

def expandpath(path):
    if path is not None and path != "":
        if path[0] == "~":
            path = os.path.expanduser(path)
        if os.path.exists(path):
            path = os.path.abspath(path)
            return (True, path)
    return (False, None)

def read_results(queue, respath):
    """
    Tk is single threaded. To run another thread you must not access
    Tk app from it. This kernel function reads Results for ImageData
    and puts them in a queue, which can be accessed from Tk.
    """
#    results.connect2db(uri=)
    a = Results(respath)
    a.session.commit()
    queue.put(a)


def multi_getattr(obj, attr, default=None):
    """
    Get a named attribute from an object; multi_getattr(x, 'a.b.c.d') is
    equivalent to x.a.b.c.d. When a default argument is given, it is
    returned when any attribute in the chain doesn't exist; without
    it, an exception is raised when a missing attribute is encountered.

    """
    attributes = attr.split(".")
    for i in attributes:
        try:
            obj = getattr(obj, i)
        except AttributeError:
            if default:
                return default
            else:
                raise
    return obj


def centerWindow(parent, w, h):
    """
    Returns a string for .geometry method that centers the window.
    Send in the root window and desired width and height of current
    window.
    """
    sw = parent.winfo_screenwidth()
    sh = parent.winfo_screenheight()

    x = (sw - w)/2
    y = (sh - h)/2

    return ('%dx%d+%d+%d' % (w, h, x, y))
