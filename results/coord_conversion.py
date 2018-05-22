import ccd_dimensions as ccd

#W_CAMCOL = 2048
#W_CAMCOL_SPACING = 1743.820956

#H_FILTER = 2048
#H_FILTER_SPACING = 660.4435401

#MAX_W_CCDARRAY = 21008 #unrounded: 21007.10478
#MAX_H_CCDARRAY = 12882 #unrounded: 12881.77416

#ARCMIN2PIX = 0.0066015625
#MM2ARCMIN = 3.63535503

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
    ordered_filters = {"r":1, "i":2, "u":3, "z":4, "g":5}
    return ordered_filters[filter]

def get_filter_from_int(filterint):
    return ["r", "i", "u", "z", "g"][filterint-1]

def convert_ccd2frame(x, y):

    res = [None, None, None, "nofilter"]
    solved_camcol = False
    solved_filter = False

    newx = lambda camcol: \
           x - (camcol-1) * (ccd.W_CAMCOL + ccd.W_CAMCOL_SPACING)
    newy = lambda filter: \
           y - (filter-1) * (ccd.H_FILTER + ccd.H_FILTER_SPACING)

    for i in range(1, 7):
        tmp = newx(i)
        if tmp >= 0 and tmp <= ccd.W_CAMCOL:
            res[0] = tmp
            res[2] = i
            solved_camcol = True

    for i in range(1, 6):
        tmp = newy(i)
        if tmp >= 0 and tmp <= ccd.H_FILTER:
            res[1] = tmp
            res[3] = get_filter_from_int(i)
            solved_filter = True

    if solved_camcol and solved_filter:
        return res
    else:
        raise CoordinateConversionError((x,y), res)


def convert_frame2ccd(x, y, camcol, filter):
    if isinstance(filter, unicode):
        filter = str(filter)
    if isinstance(filter, str) and filter in "riuzg":
        filter = get_filter_int(filter)
    elif isinstance(filter, int) and filter in (1,2,3,4,5):
        pass
    else:
        raise ValueError("Unrecognized filter: {0}".format(filter))

    newx = x + (camcol-1) * (ccd.W_CAMCOL + ccd.W_CAMCOL_SPACING)
    newy = y + (filter-1) * (ccd.H_FILTER + ccd.H_FILTER_SPACING)

    return [newx,newy]
