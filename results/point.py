#from sqlalchemy import Column
from sqlalchemy.ext.mutable import MutableComposite


from .coord_conversion import convert_ccd2frame, convert_frame2ccd

__all__ = ["Point", "Line"]

Line = 2


#class Point(MutableComposite):
#    def __init__(self, x, y, camcol=None, filter=None, coordsys="frame",
#                 cx=None, cy=None):
#
#        self.coordsys = coordsys.lower()
#
#        tmpf = lambda x: isinstance(x, Column)
#        are_columns = map(tmpf, (x, y, cx, cy, camcol, filter))
#        if all(are_columns):
#            self.x = x
#            self.y = y
#            self.cx = cx
#            self.cy = cy
#            self._camcol = camcol
#            self._filter = filter
#        else:
#            if all((cx, cy)):
#                _, _, camcol, filter = convert_ccd2frame(cx, cy)
#                self.__initAll(x, y, cx, cy, camcol, filter)  
#            elif self.coordsys == "frame" and all([x, y, camcol, filter]):
#                self.__initFrame(x, y, camcol, filter)
#            elif self.coordsys == "ccd":
#                self.__initCCD(x, y)
#            else:
#                errmsg = "Expected (x,y, coordsys='ccd') or"
#                errmsg += "(x, y, camcol, filter). Got ({0}, {1}, {2}, {3}, {4})"
#                errmsg += "instead."
#                raise TypeError(errmsg.format(x, y, camcol, filter, coordsys))
#
#    def __initAll(self, x, y, cx, cy, camcol, filter):
#        self.x = x
#        self.y = y
#        self.cx = cx
#        self.cy = cy
#        self._camcol = camcol
#        self._filter = filter
#
#    def __initFrame(self, x, y, camcol, filter):
#        cx, cy = convert_frame2ccd(x, y, camcol, filter)
#        print("in init frame", cx, cy)
#        self.__initAll(x, y, cx, cy, camcol, filter)
#
#    def __initCCD(self, cx, cy):
#        print("initting ccd", cx, cy)
#        x, y, camcol, filter = convert_ccd2frame(x, y)
#        self.__initAll(x, y, cx, cy, camcol, filter)
#
#    def __repr__(self):
#        m = self.__class__.__module__
#        n = self.__class__.__name__
#        return "<{0}.{1}(x={2}, y={3})>".format(m, n, self.x, self.y)
#
#    def __composite_values__(self):
#        return self.x, self.y, self.cx, self.cy
#
#    def __setattr__(self, key, val):
##        print("in setattr", key)
##        d = self.__dict__
##        if key not in self.__dict__:
#        object.__setattr__(self, key, val)
##        else:
##            if "x" in d and  key == "x":
##                self.move(val, self.y)
##            elif "y" in d and  key == "y":
##                self.move(self.x, val)
##            elif "cx" in d and  key == "cx":
##                self.move(val, self.cy, frame="ccd")
##            elif "cy" in d and  key == "cy":
##                self.move(self.cx, val, frame="ccd")
#        self.changed()
#
#    @property
#    def camcol(self):
#        if self.coordsys == "frame":
#            return self._camcol
#        else:
#            raise AttributeError("Atribute 'camcol' is availible "+\
#                                 "only in 'frame' coordinate system.")
#
#    @property
#    def filter(self):
#        if self.coordsys == "frame":
#            return self._filter
#        else:
#            raise AttributeError("Atribute 'filter' is availible "+\
#                                 "only in 'frame' coordinate system.")
#
#    def useCoordSys(self, coordsys):
#        if coordsys.lower() in ["frame", "ccd"]:
#            self.coordsys = coordsys.lower()
#
#    def move(self, *args, coordsys=None):#, alert=True):
#        if len(args) == 2:
#            x, y = args
#        elif len(args) == 1:
#            x, y = args[0]
#        else:
#            x, y = kwargs["x"], kwargs["y"]
#
#        if coordsys is None:
#            coordsys = self.coordsys
#        if coordsys == "frame":
#            self.__initFrame(x, y, self._camcol, self._filter)
#        else:
#            print("initting ccd")
#            self.__initCCD(x, y)


class Point(MutableComposite):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __setattr__(self, key, value):
        "Intercept set events"

        # set the attribute
        object.__setattr__(self, key, value)

        # alert all parents to the change
        self.changed()

    def __composite_values__(self):
        return self.x, self.y

    def __eq__(self, other):
        return isinstance(other, Point) and \
            other.x == self.x and \
            other.y == self.y

    def __ne__(self, other):
        return not self.__eq__(other)


#class Line(MutableComposite):
#    def __init__(self, x1, y1, x2, y2, camcol=None, filter=None,
#                 cx1=None, cy1=None, cx2=None, cy2=None, coordsys="frame"):
#
#        tmpf = lambda x: isinstance(x, Column)
#        are_columns = map(tmpf, (x1, y1, x2, camcol, filter, cx1, cy1, cx2, cy2))
#        if all(are_columns):
#            self.x1 = x1
#            self.y1 = y1
#            self.x2 = x2
#            self.y2 = y2
#            self.cx1 = cx1
#            self.cy1 = cy1
#            self.cx2 = cx2
#            self.cy2 = cy2
#            self._camcol = camcol
#            self._filter = filter
#        else:
#            p1 = Point(x1, y1, camcol, filter, coordsys, cx=cx1, cy=cy1)
#            self.p1 = p1
#            self.x1  = p1.x
#            self.y1  = p1.y
#            self.cx1 = p1.cx
#            self.cy1 = p1.cy
#
#            p2 = Point(x2, y2, camcol, filter, coordsys, cx=cx2, cy=cy2)
#            self.p2 = p2
#            self.x2  = p2.x
#            self.y2  = p2.y
#            self.cx2 = p2.cx
#            self.cy2 = p2.cy
#        
#
#    def __composite_values__(self):
#        return self.p1.x, self.p1.y, self.p1.cx, self.p1.cy, \
#            self.p2.x, self.p2.y, self.p2.cx, self.p2.py
#
#    def __setattr__(self, key, value):
#        "Intercept set events"
#
#        object.__setattr__(self, key, value)
#        if key in ("x1", "y1", "cx1", "cy1"):
#            #setattr(self, key, value)
#            try: setattr(self.p1, key[:-1], value)
#            except: pass
#        elif key in ("x2", "y2", "cx2", "cy2"):
#            #setattr(self, key, value)
#            try: setattr(self.p2, key[:-1], value)
#            except: pass
#
#        print("alert going out")
#        self.changed()
#
#    def __getattr__(self, key):
#        if key in ("x1", "y1", "cx1", "cy1"):
#            return getattr(self.p1, key[:-1])
#        elif key in ("x2", "y2", "cx2", "cy2"):
#            return getattr(self.p1, key[:-1])
#        else:
#            errmsg = "Object {0} has no attribute {1}"
#            raise AttributeError(errmsg.format(self, key))
