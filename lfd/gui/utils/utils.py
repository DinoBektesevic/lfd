import os


def expandpath(path):
    """Normalize a string assuming it's a filesystem path. If the given string
    is empty  or equivalent assumes the path can not be expanded. This is to
    account for various ways different widgets return an empty string (None,
    empty or empty tuple).

    Parameters
    ----------
    path : `str`
        string to expand as path

    Returns
    -------
    expandedPath : `tuple`
        A tuple containing a bool and the expanded path. If the path can be
        expanded the bool will be True. It is False otherwise.
    """
    if path is not None and path != "" and path != ():
        if path[0] == "~":
            path = os.path.expanduser(path)
        if os.path.exists(path):
            path = os.path.abspath(path)
            return (True, path)
    return (False, None)


def multi_getattr(obj, attr, default=None):
    """Get a named attribute from an object; multi_getattr(x, 'a.b.c.d') is
    equivalent to x.a.b.c.d. When a default argument is given, it is returned
    when any attribute in the chain doesn't exist; without it, an exception is
    raised when a missing attribute is encountered.

    Parameters
    ----------
    obj : `object`
        Object whose nested attribute will be returned.
    attr : `str`
        String containing attribute names separated by a dot.
    default : `object`, optional
        Literally anything. Defaults to None.

    Returns
    -------
    attribute : `obj`
        Either the requested attribute or, if given, the ``default`` parameter.
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


def centerWindow(window, w, h):
    """Returns a string for .geometry method that centers the window.
    Send in the root window and desired width and height of current
    window.

    Parameters
    ----------
    window : `tkinter.Frame` or `object`
        Usually a ttk Frame object, but can be any object that has
        winfo_screenwidth and winfo_screenheight methods.
    w : `int`
        Desired width, in pixels
    h : `int`
        Desired height, in pixels

    Returns
    -------
    centerCoords : `str`
        A string formated as required by tkinter.geometry function containing
        the desired window width and height values, nd x and y coordinates.

    Notes
    -----
    The return string format is ``{w}x{h}+{x}+{y}`` where the w x h are the
    given desired window width and height and x and y the coordinates of the
    top left corner of that window if the window center were to match the
    screen center.
    """
    sw = window.winfo_screenwidth()
    sh = window.winfo_screenheight()

    x = (sw - w)/2
    y = (sh - h)/2

    return (f"{w}x{h}+{x}+{y}")
