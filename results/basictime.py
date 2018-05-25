from astropy.time import Time

__all__ = ["BasicTime", "LineTime"]

class BasicTime(object):
    def __init__(self, t, t_format="tai"):
        if t is None:
            self._tai = None
            self._mjd = None
        elif t_format.lower()=="tai":
            self._init_tai(t)
        elif t_format.lower()=="mjd":
            self._init_mjd(t)
        else:
            raise ValueError("Unrecognized time format")

    def _init_tai(self, t):
        self._tai = t
        self._mjd = t/(24.0*3600.0)

    def _init_mjd(self, t):
        self._mjd = t
        self._tai = t*(24.0*3600.0)

    @property
    def iso(self):
        return Time(self._mjd, format="mjd").iso

    @property
    def tai(self):
        return self._tai

    @tai.setter
    def tai(self, val):
        self._init_tai(val)

    @property
    def mjd(self):
        return self._mjd

    @mjd.setter
    def mjd(self, val):
        self._init_mjd(val)

    def __repr__(self):
        m = self.__class__.__module__
        n = self.__class__.__name__
        return "<{0}.{1}(t={2})>".format(m, n, self.tai)

    def __eq__(self, other):
        if self.mjd == other.mjd:
            return True
        return False

    def __lt__(self, other):
        if self.mjd < other.mjd:
            return True
        return False

    def __gt__(self, other):
        return not self.__lt__(other)

    def __le__(self, other):
        if self.__lt__(other) or self.__eq__(other):
            return True
        return False

    def __ge__(self, other):
        return not self.__le__(other)


class LineTime(object):
    def __init__(self, t_start, t_end, t_format="tai"):
        self.st = BasicTime(t_start, t_format)
        self.et = BasicTime(t_end, t_format)


    def __repr__(self):
        m = self.__class__.__module__
        n = self.__class__.__name__
        return "<{0}.{1}(start={2}, end={3})>".format(m, n, self.st.tai,
                                                      self.et.tai)

