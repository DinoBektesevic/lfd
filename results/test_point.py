from sqlalchemy.ext.mutable import MutableComposite

class Point(MutableComposite):
    def __init__(self, x, y, camcol=None, filter=None,
                 coordsys="frame"):
        x = float(x)
        y = float(y)
        self.coordsys = coordsys.lower()

        if (self.coordsys == "frame" and None not in [x, y, camcol, filter]):
            self.__initFrame(x, y, camcol, filter)
        elif self.coordsys == "ccd":
            self.__initCCD(x, y)
        else:
            raise TypeError("Send x, y coordinates with 'ccd' " + \
                            "coordinate system or send x, y, camcol " + \
                            "and filter with 'frame' coordinate system.")


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
