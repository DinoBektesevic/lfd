from sqlalchemy.ext.mutable import MutableComposite

from .coord_conversion import convert_ccd2frame, convert_frame2ccd

__all__ = ["Point"]

class Point(MutableComposite):
    def __init__(self, x, y, camcol=None, filter=None, coordsys="frame"):
        self.coordsys = coordsys.lower()

        if (self.coordsys == "frame" and None not in [x, y, camcol, filter]):
            self.__initFrame(x, y, camcol, filter)
        elif self.coordsys == "ccd":
            self.__initCCD(x, y)
        else:
            raise TypeError("Send x, y coordinates with 'ccd' " + \
                            "coordinate system or send x, y, camcol " + \
                            "and filter with 'frame' coordinate system. Received", x, y, camcol, filter, coordsys, "instead")

    def __initFrame(self, x, y, camcol, filter):
        self._fx = x
        self._fy = y
        self._camcol = camcol
        self._filter = filter

        tmp = convert_frame2ccd(x, y, camcol, filter)
        self._cx = tmp[0]
        self._cy = tmp[1]

    def __initCCD(self, x, y):
        self._cx = x
        self._cy = y

        tmp = convert_ccd2frame(x, y)
        self._fx = tmp[0]
        self._fy = tmp[1]
        self._camcol = tmp[2]
        self._filter = tmp[3]

    def __composite_values__(self):
        return self._fx, self._fy

    def __setattr__(self, key, value):
        "Intercept set events"

        # set the attribute
        object.__setattr__(self, key, value)

        # alert all parents to the change
        if key in ("x", "y"):
            print("alert going out")
            self.changed()

    def __repr__(self):
        m = self.__class__.__module__
        n = self.__class__.__name__
        return "<{0}.{1}(x={2}, y={3})>".format(m, n, self.x, self.y)


    @property
    def x(self):
        if self.coordsys == "frame":
            return self._fx
        else:
            return self._cx

    @x.setter
    def x(self, value):
        if self.coordsys == "frame":
            self.__initFrame(value, self._fy, self.camcol, self.filter)
        else:
            self.__initCCD(value, self._cy)

    @property
    def y(self):
        if self.coordsys == "frame":
            return self._fy
        else:
            return self._cy

    @y.setter
    def y(self, value):
        if self.coordsys == "frame":
            self.__initFrame(self._fx, value, self._camcol, self._filter)
        else:
            self.__initCCD(self._cx, value)

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


    def move(self, *args, **kwargs):
        if len(args) == 2:
            x, y = args
        elif len(args) == 1:
            x, y = args[0]
        else:
            x, y = kwargs["x"], kwargs["y"]

        if self.coordsys == "frame":
            self.__initFrame(x, y, self._camcol, self._filter)
        else:
            self.__initCCD(x, y)
