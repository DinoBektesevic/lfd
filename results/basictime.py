from astropy.time import Time

class BasicTime(object):
    def __init__(self, t, t_format="tai"):
        if t_format.lower()=="tai":
            self._init_tai(t)
        elif t_format.lower()=="mjd":
            self._init_mjd(t)
        else:
            raise ValueError("Unrecognized time format")

    def _init_tai(self, t):
        self.tai = t
        self.mjd = t/(24.0*3600.0)

    def _init_mjd(self, t):
        self.mjd = t
        self.tai = t*(24.0*3600.0)

    @property
    def iso(self):
        return Time(self.mjd, format="mjd").iso

    def __repr__(self):
        return str(self.tai)

    def __eq__(self, other):
        #mjd time is in seconds and offers a much more 
        #precise way of comparing time than tai which is in days.
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

        