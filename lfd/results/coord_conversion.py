from lfd.results import ccd_dimensions as ccd


__all__ = ["convert_ccd2frame", "convert_frame2ccd",
           "CoordinateConversionError"]


class CoordinateConversionError(ArithmeticError):
    """Generic Error to be called when no sollution to coordinate conversions
    between CCD and frame coordinate systems are not possible. A light wrapper
    around ArithmeticError.

    Example
    -------

    >>> raise CoordinateConversionError(incoords, outcoords)

    Parameters
    ----------

    incoords : tuple, list
      a set of ingoing to-be-converted coordinates
    outcoords : tuple, list
      set of (miss)calculated coordinates
    msg : str
      customize the error message
    *args : tuple, list
      any additional args can be supplemented and are appended to the end of
      the error message

    incoords are (cx, cy) CCD coordinates and outcoords are the frame
    (x, y, camcol, filter) coordinates or vice-versa.

    """

    def __init__(self, incoords, outcoords, msg=None, *args):
        """CoordinateConversionError(incoords, outcoords)
        where incoords are (cx, cy) CCD coordinates and outcoords are the frame
        (x, y, camcol, filter) coordinates or vice-versa.

        Optionally supply a custom message by providing msg and a set of args
        that will be appended to said msg.

        Parameters
        ----------

        incoords : tuple, list
          a set of ingoing to-be-converted coordinates
        outcoords : tuple, list
          set of (miss)calculated coordinates
        msg : str
          customize the error message. String .format method with positional
          arguments with incoords and outcoords always being the first two,
          rest is then appended in the order it was given in *args. 
        *args : tuple, list
          any additional args can be supplemented and are appended to the end of
          the error message
    
        incoords are (cx, cy) CCD coordinates and outcoords are the frame
        (x, y, camcol, filter) coordinates or vice-versa.

        """

        if msg is not None:
            self.message = msg
        else:
            self.message = ("Unsolvable system. Coordinates not attributable "
                            "to any CCD in the array. \n Initial coordinates: "
                            "{0}. Retrieved coordinates: {1}. ")
            if args:
                self.message += "\n Args: "
                for i in range(2, len(args)+2):
                    self.message += "{0} ".format(i)

        if args:
            self.message.format(incoords, outcoords, *args)
        else:
            self.message = self.message.format(incoords, outcoords)

        self.errorcoords = incoords
        self.outcoords = outcoords

        ArithmeticError.__init__(self, self.message)


def get_filter_int(filter):
    """Provides the mapping between filter in string form and integer value
    based on the row the searched for filter is in, starting from the top::

     r -> 0
     i -> 1
     u -> 2
     z -> 3
     g -> 4

    """

    return {"r":0, "i":1, "u":2, "z":3, "g":4}[filter]


def get_filter_from_int(filterint):
    """Provides translation between an integer row value of the filter and its
    string value where the top row is indexed with a zero::

     0 -> r
     1 -> i
     2 -> u
     3 -> z
     4 -> g

    """

    return ["r", "i", "u", "z", "g"][filterint-1]


def convert_ccd2frame(x, y):
    """Conversts the coordinate pair (x, y) from the CCD coordinate system to a
    frame coordinate system by applying the following formulae::

     x = cx - {camcol} * (W_CAMCOL + W_CAMCOL_SPACING)
     y = cy - {filter} * (H_FILTER + H_FILTER_SPACING)

    Where camcol and filter are iterated over untill a possible sollution is
    found. A sollution is possible if it is contained within the width and
    height of a single CCD respective to its (0, 0) point in the frame coord.
    system. Only one such sollution is guaranteed to exists.

    """

    res = [None, None, None, "nofilter"]
    solved_camcol = False
    solved_filter = False

    # whatever you have in your book is wrong, you messed something up in your
    # notes? Given a camcol and filter the annon funcs calculate the coordinates
    # in the frame coord sys. on the given single CCD at (camcol, filter)
    newx = lambda camcol: \
           x - camcol * (ccd.W_CAMCOL + ccd.W_CAMCOL_SPACING)
    newy = lambda filter: \
           y - filter * (ccd.H_FILTER + ccd.H_FILTER_SPACING)

    # to invert the solution we iterate over all camcols and only one camcol
    # will produce a value of x coordinate contained within the respective single
    # CCD. We store the calculated frame x coordinate and the respective camcol
    for i in range(0, 6):
        tmp = newx(i)
        if tmp >= 0 and tmp <= ccd.W_CAMCOL:
            res[0] = tmp
            res[2] = i+1
            solved_camcol = True
            break

    # procedure is repeated for filters, only one filter will produce a valid
    # value of frame y coordinate, we remember the coord and the filter.
    for i in range(0, 5):
        tmp = newy(i)
        if tmp >= 0 and tmp <= ccd.H_FILTER:
            res[1] = tmp
            res[3] = get_filter_from_int(i+1)
            solved_filter = True
            break

    # it is possible no solutions are found if the CCD coordinates fall in the
    # gaps between CCD array columns and rows. We check:
    if solved_camcol and solved_filter:
        return res
    else:
        raise CoordinateConversionError((x,y), res)


def convert_frame2ccd(x, y, camcol, filter):
    """Converts from frame coordinates (x, y, camcol, filter) to CCD coordinates
    (cx, cy) via the following formulae::

     cx = x + (camcol-1) * (W_CAMCOL + W_CAMCOL_SPACING)
     cy = y +  filter    * (H_FILTER + H_FILTER_SPACING)

    Filter can be sent as an integer or a string from {riuzg}.

    """

    # check filter type and resolve into integer
    if isinstance(filter, str) and filter in "riuzg":
        filter = get_filter_int(filter)
    elif isinstance(filter, int) and filter in (1,2,3,4,5):
        pass
    else:
        raise ValueError("Unrecognized filter: {0}".format(filter))

    # check camcol is correct
    if camcol > 6 or camcol < 1:
        raise ValueError("Unrecognized camcol: {0}".format(filter))

    newx = x + (camcol-1) * (ccd.W_CAMCOL_SPACING+ccd.W_CAMCOL)
    newy = y + filter*(ccd.H_FILTER + ccd.H_FILTER_SPACING)

    return [newx,newy]
