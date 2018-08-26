import sqlalchemy as sql
from sqlalchemy.types import TypeDecorator

from astropy.time import Time


__all__ = ["BasicTime", "LineTime"]


class BasicTime(TypeDecorator):
    impl = sql.types.Float

    def process_bind_param(self, value, dialect):
        if value is not None:
            return value.mjd*24.0*3600.0
        return None

    def process_result_value(self, value, dialect):
        if value is not None:
            return Time(value/(24.0*3600.0), format="mjd")
        return None


class LineTime(object):
    def __init__(self, t_start, t_end, t_format="tai"):
        self.st = BasicTime(t_start, t_format)
        self.et = BasicTime(t_end, t_format)


    def __repr__(self):
        m = self.__class__.__module__
        n = self.__class__.__name__
        st = self.st.iso if self.st is not None else None
        et = self.et.iso if self.et is not None else None
        return "<{0}.{1}(start={2}, end={3})>".format(m, n, st, et)

