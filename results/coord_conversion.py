from . import ccd_dimensions as ccd

__all__ = ["convert_ccd2frame", "convert_frame2ccd"]

class CoordinateConversionError(ArithmeticError):
    def __init__(self, incoords, outcoords, msg=None, *args):

        if msg is not None:
            self.message = msg
        else:
            self.message = "Unsolvable system.\n" +\
            "Initial coordinates are not attributable to any CCD "  +\
            "in the array. \n Initial coordinates: "+str(incoords)  +\
            " Retrieved coordinates: "+str(outcoords)

        self.errorcoords = incoords
        self.outcoords = outcoords

        if args:
            for arg in args:
                self.message += arg

        ArithmeticError.__init__(self, self.message)

def get_filter_int(filter):
#    ordered_filters = {"r":0, "i":1, "u":2, "z":3, "g":4}
    return {"r":0, "i":1, "u":2, "z":3, "g":4}[filter]

def get_filter_from_int(filterint):
    return ["r", "i", "u", "z", "g"][filterint-1]

def convert_ccd2frame(x, y):

    res = [None, None, None, "nofilter"]
    solved_camcol = False
    solved_filter = False

    #whatever you have in your book is wrong, you messed something up in your notes?
    newx = lambda camcol: \
           x - camcol * (ccd.W_CAMCOL + ccd.W_CAMCOL_SPACING)
    newy = lambda filter: \
           y - filter * (ccd.H_FILTER + ccd.H_FILTER_SPACING)


    for i in range(0, 6):
        tmp = newx(i)
        if tmp >= 0 and tmp <= ccd.W_CAMCOL:
            res[0] = tmp
            res[2] = i+1
            solved_camcol = True
            break

    for i in range(0, 5):
        tmp = newy(i)
        if tmp >= 0 and tmp <= ccd.H_FILTER:
            res[1] = tmp
            res[3] = get_filter_from_int(i+1)
            solved_filter = True
            break

    if solved_camcol and solved_filter:
        return res
    else:
        raise CoordinateConversionError((x,y), res)


def convert_frame2ccd(x, y, camcol, filter):
    if isinstance(filter, str):
        filter = str(filter)
    if isinstance(filter, str) and filter in "riuzg":
        filter = get_filter_int(filter)
    elif isinstance(filter, int) and filter in (1,2,3,4,5):
        pass
    else:
        raise ValueError("Unrecognized filter: {0}".format(filter))

    newx = x + (camcol-1) * (ccd.W_CAMCOL_SPACING+ccd.W_CAMCOL)
    newy = y + filter*(ccd.H_FILTER + ccd.H_FILTER_SPACING)

    return [newx,newy]
