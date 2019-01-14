"""Dealing with time-stamps has always been a challenging aspect of APIs. This
module, hopefully, alleviates some of issues wen dealing with timestamps by
defining a new database type decorator that will wrap the awkward SDSS TAI
timestamps into a more pleasant OO interface by using Astropy Time objects.

"""

import sqlalchemy as sql
from sqlalchemy.types import TypeDecorator

from astropy.time import Time


__all__ = ["BasicTime", "LineTime"]

def timerepr(self):
    """Creates a repr string out of an Astropy Time object more alike to the
    repr str format used elswhere in the results package. Forcefully overwrites
    the default Astropy Time __repr__ function.
    """
    scale = self.scale
    format = self.format
    value = self.value*24.0*3600.0
    retrstr = "<lfd.results.basictime.BasicTime(scale={0}, format={1}, value={2})>"
    return retrstr.format(scale, format, value)

def timestr(self):
    """Creates a str string out of an Astropy Time object that is more alike to
    the the str format used elswhere in the results package. Forcefully
    overwrites the default Astropy Time __str__ function.
    """
    return "Time({0})".format(self.iso)

# overwrite the default __repr__ and __str__ functions of Astropy Time to
# force a consistent __repr__ and __str__ format across result package
#Time.__repr__ = timerepr
#Time.__str__ = timestr


class BasicTime(TypeDecorator):
    """A class that will force storing time stamps in the SDSS TAI format and
    will force read-out of the timestamp from the DB as an Astropy Time object.

    Assignments, comparisons and other interactions will be the same as any
    other Astropy Time object.

    """

    impl = sql.types.Float

    def process_bind_param(self, value, dialect):
        """Used to map value to the desired storage format within the DB.
        Expects an Astropy Time object. Converts the time to SDSS TAI format
        for storage.

        """

        if value is not None:
            if isinstance(value, Time):
                return value.mjd*24.0*3600.0
            else:
                return value
        return None

    def process_result_value(self, value, dialect):
        """Used to map read values from the DB to a format appropriate for
        interactive work. Expects an SDSS TAI format float value and returns an
        Astropy Time object.

        """

        if value is not None:
            return Time(value/(24.0*3600.0), format="mjd")
        return None




class LineTime(object):
    """Used to map two BasicTime timestamps onto a singular object.
    Potential for expansion to a point where Events can be queried on
    statistical properties of the duration of  the linear feature and other
    such features.

    Currently useless as many of the advanced interfaces are not implemented.

    """

    def __init__(self, t_start, t_end, t_format="tai"):
        self.st = BasicTime(t_start, t_format)
        self.et = BasicTime(t_end, t_format)


    def __repr__(self):
        m = self.__class__.__module__
        n = self.__class__.__name__
        st = self.st.iso if self.st is not None else None
        et = self.et.iso if self.et is not None else None
        return "<{0}.{1}(start={2}, end={3})>".format(m, n, st, et)

