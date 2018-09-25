#from sqlalchemy import Column
import warnings
warnings.simplefilter('always', SyntaxWarning)

from sqlalchemy.ext.mutable import MutableComposite

from .coord_conversion import convert_ccd2frame, convert_frame2ccd

__all__ = ["Point"]

class Point(MutableComposite):
    """Provides a more comfortable interface for handling coordinates and coord
    transformations. Capable of moving and setting of new coordinate values in
    any frame while maintaning consistency across all coordinates.
    Will produce a warning in an inconsistent situations to warn the user that,
    logically, the performed operations do not make sense, but will not enforce
    consistency. See Notes in results.event.Event object for more information.




    """
    def __init__(self, x=None, y=None,  cx=None, cy=None,
                 camcol=None, filter=None, coordsys="frame"):

        self.coordsys = coordsys.lower()

        if coordsys == "ccd" and all([x, y]):
            cx, cy = x, y
            x, y = None, None

        if all([x, y, camcol, filter, cx, cy]):
            self.__initAll(x, y, cx, cy, camcol, filter)
        elif self.coordsys == "ccd" and all((cx, cy)):
            self.__initCCD(cx, cy)
        elif self.coordsys == "frame" and all([x, y, camcol, filter]):
            self._initFrame(x, y, camcol, filter)
        else:
            errmsg = "Expected (x,y, coordsys='ccd') or "
            errmsg += "(x, y, camcol, filter). Got ({0}, {1}, {2}, {3}, {4}) "
            errmsg += "instead."
            raise TypeError(errmsg.format(x, y, camcol, filter, coordsys))

    def __initAll(self, x, y, cx, cy, camcol, filter, check=True):
        # check for consistency when defaulting to immediate __initAll
        if check:
            tmpcx, tmpcy = convert_frame2ccd(x, y, camcol, filter)
            if tmpcx != cx or tmpcy != cy:
                msg = ("Instantiation inconsistency: Supplied coordinates do not "
                       "match. Received (x={0}, y={1}, cx={2}, cy={3}) but "
                       "calculated (x={4}, y={5}, cx={6}, cy={7}).")
                raise ValueError(msg.format(x, y, cx, cy, x, y, tmpcx, tmpcy))
        self._x = x
        self._y = y
        self._cx = cx
        self._cy = cy

        self._camcol = camcol
        self._filter = filter

        self.changed()

    def _initFrame(self, x, y, camcol, filter):
        cx, cy = convert_frame2ccd(x, y, camcol, filter)
        self.__initAll(x, y, cx, cy, camcol, filter, check=False)

    def __initCCD(self, cx, cy):
        x, y, camcol, filter = convert_ccd2frame(cx, cy)
        self.__initAll(x, y, cx, cy, camcol, filter, check=False)

    def __repr__(self):
        m = self.__class__.__module__
        n = self.__class__.__name__
        retrstr = "<{0}.{1}(x={2}, y={3}, cx={4}, cy={5})>"
        return retrstr.format(m, n, self.x, self.y, self.cx, self.cy)

    def __str__(self):
        return "Point(x={0}, y={1})".format(self.x, self.y)

    def __composite_values__(self):
        return self.x, self.y, self.cx, self.cy

    def _check_sensibility(self, attr):
        msg = "Attribute {0} should only be accessed when coordsys={1}"
        if attr in (["x", "y", "camcol", "filter"]) and self.coordsys == "ccd":
            warnings.warn(msg.format(attr, "frame"), SyntaxWarning)
        if attr in (["cx", "cy"]) and self.coordsys == "frame":
            warnings.warn(msg.format(attr, "ccd"), SyntaxWarning)

    @property
    def camcol(self):
        self._check_sensibility("camcol")
        return self._camcol

    @property
    def filter(self):
        self._check_sensibility("filter")
        return self._filter

    def useCoordSys(self, coordsys):
        if coordsys.lower() in ["frame", "ccd"]:
            self.coordsys = coordsys.lower()

    def move(self, *args, **kwargs):
        print("", args)
        print("           ", kwargs)
        print(dir(self))

        x = kwargs.pop("x", self.x)
        y = kwargs.pop("y", self.y)
        cx = kwargs.pop("cx", self.cx)
        cy = kwargs.pop("cy", self.cy)
        coordsys = kwargs.pop("coordsyy", self.coordsys)

        if coordsys == "frame":
            self._initFrame(x, y, self._camcol, self._filter)
        else:
            self.__initCCD(cx, cy)

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, val):
        self._initFrame(val, self._y, self._camcol, self._filter)

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, val):
        self._initFrame(self._x, val, self._camcol, self._filter)

    @property
    def cx(self):
        return self._cx

    @cx.setter
    def cx(self, val):
        self.__initCCD(val, self.cy)

    @property
    def cy(self):
        return self._cy

    @cy.setter
    def cy(self, val):
        self.__initCCD(self.cx, val)

