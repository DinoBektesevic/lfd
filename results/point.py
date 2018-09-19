#from sqlalchemy import Column
from sqlalchemy.ext.mutable import MutableComposite


from .coord_conversion import convert_ccd2frame, convert_frame2ccd

__all__ = ["Point", "Line"]

class Point(MutableComposite):
    def __init__(self, x, y,  cx=None, cy=None,
                 camcol=None, filter=None, coordsys="frame"):

        self.coordsys = coordsys.lower()

        if all([x, y, camcol, filter, cx, cy]):
            self.__initAll(x, y, cx, cy, camcol, filter)
        elif self.coordsys == "ccd" and all((cx, cy)):
            self.__initCCD(cx, cy)
        elif self.coordsys == "frame" and all([x, y, camcol, filter]):
            self.__initFrame(x, y, camcol, filter)
        else:
            errmsg = "Expected (x,y, coordsys='ccd') or "
            errmsg += "(x, y, camcol, filter). Got ({0}, {1}, {2}, {3}, {4}) "
            errmsg += "instead."
            raise TypeError(errmsg.format(x, y, camcol, filter, coordsys))

    def __initAll(self, x, y, cx, cy, camcol, filter):
        print("in init all")
        self._x = x
        self._y = y
        self._cx = cx
        self._cy = cy

        self._camcol = camcol
        self._filter = filter

    def __initFrame(self, x, y, camcol, filter):
        cx, cy = convert_frame2ccd(x, y, camcol, filter)
        print("in init frame", cx, cy)
        self.__initAll(x, y, cx, cy, camcol, filter)

    def __initCCD(self, cx, cy):
        print("initting ccd", cx, cy)
        x, y, camcol, filter = convert_ccd2frame(cx, cy)
        self.__initAll(x, y, cx, cy, camcol, filter)

    def __repr__(self):
        m = self.__class__.__module__
        n = self.__class__.__name__
        return "<{0}.{1}(x={2}, y={3})>".format(m, n, self.x, self.y)

    def __composite_values__(self):
        return self._x, self._y, self._cx, self._cy

    def __setattr__(self, key, val):
        "Intercept set events"
#
#        key = key.lower()
#        selfdict = dir(self)
#        if key == "x" and "x" in selfdict:
#            self.move(x=val)
#        elif key == "y" and "y" in selfdict:
#            self.move(y=val)
#        elif key == "cx" and "cx" in selfdict:
#            self.move(cx=val)
#        elif key == "cy" and "cy" in selfdict:
#            self.move(cy=val)
#        else:
#            # default to generic setter
        object.__setattr__(self, key, val)

        # alert all parents to the change
        if key in (["x", "y", "cx", "cy"]):
            print("issuing change")
            self.changed()


    @property
    def camcol(self):
        if self.coordsys == "frame":
            return self._camcol
        else:
            raise AttributeError("Atribute 'camcol' is availible "+\
                                 "only in 'frame' coordinate system.")

    @property
    def filter(self):
        if self.coordsys == "frame":
            return self._filter
        else:
            raise AttributeError("Atribute 'filter' is availible "+\
                                 "only in 'frame' coordinate system.")

    def useCoordSys(self, coordsys):
        if coordsys.lower() in ["frame", "ccd"]:
            self.coordsys = coordsys.lower()

    def move(self, *args, **kwargs):#, alert=True):
        print("", args)
        print("           ", kwargs)
        print(dir(self))

#        if coordsys is None:
#            coordsys = self.coordsys
#        else:
#            coordsys = coordsys.lower()
#
#        if coordsys == "frame":
#            if len(args) == 2:
#                x, y = args
#            elif len(args) == 1:
#                x, y = args[0]
#        elif coordsys == "ccd":
#            if len(args) == 2:
#                cx, cy = args
#            elif len(args) == 1:
#                cx, cy = args[0]
#        else:
#            x = kwargs.pop("x", self.x)
#            y = kwargs.pop("y", self.y)
#            cx = kwargs.pop("cx", self.cx)
#            cy = kwargs.pop("cy", self.cy)


        x = kwargs.pop("x", self.x)
        y = kwargs.pop("y", self.y)
        cx = kwargs.pop("cx", self.cx)
        cy = kwargs.pop("cy", self.cy)
        coordsys = kwargs.pop("coordsyy", self.coordsys)


        if coordsys == "frame":
            self.__initFrame(x, y, self._camcol, self._filter)
        else:
#            print("initting ccd")
            self.__initCCD(cx, cy)

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, val):
        self.__initFrame(val, self._y, self._camcol, self._filter)

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, val):
        self.__initFrame(self._x, val, self._camcol, self._filter)

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

class Line(MutableComposite):
    def __init__(self, x1, y1, x2, y2, cx1=None, cy1=None, cx2=None, cy2=None,
                 camcol=None, filter=None, coordsys="frame"):

#        try: print(cx)
#        except: pass
        self.p1 = Point(x1, y1, camcol, filter, cx1, cy1, coordsys)
        self.p2 = Point(x2, y2, camcol, filter, cx2, cy2, coordsys)


    def __composite_values__(self):
        return self.p1.x, self.p1.y, self.p2.x, self.p2.y, \
            self.p1.cx, self.p1.cy, self.p2.cx, self.p2.cy

    def __setattr__(self, key, value):
        "Intercept set events"

        if key == "x1":
            self.p1.move(value, self.p1.y, "frame")
        elif key == "y1":
            self.p1.move(self.p1.x, value, "frame")
        elif key == "cx1":
            self.p1.move(value, self.p1.cy, "ccd")
        elif key == "cy1":
            self.p1.move(self.p1.cx, value, "ccd")
        elif key == "x2":
            self.p2.move(value, self.p2.y, "frame")
        elif key == "y2":
            self.p2.move(self.p2.x, value, "frame")
        elif key == "cx2":
            self.p2.move(value, self.p2.cy, "ccd")
        elif key == "cy2":
            self.p2.move(self.p2.cx, value, "ccd")
        else:
            object.__setattr__(self, key, value)

#        print("alert going out")
        self.changed()

    def __getattr__(self, key):
        if key in ("x1", "y1", "cx1", "cy1"):
            return getattr(self.p1, key[:-1])
        elif key in ("x2", "y2", "cx2", "cy2"):
            return getattr(self.p2, key[:-1])
        else:
            errmsg = "Object {0} has no attribute {1}"
            raise AttributeError(errmsg.format(self, key))
