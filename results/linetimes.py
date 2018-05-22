from .base import Base
from .basictime import BasicTime

from astropy.time import Time

import sqlalchemy as sa
from sqlalchemy.orm import relationship


class LineTime(Base):
    __tablename__ = "linetimes"
    id = sa.Column(sa.Integer, primary_key=True)

    start_tai = sa.Column(sa.Float)
    start_mjd = sa.Column(sa.Float)

    end_tai = sa.Column(sa.Float)
    end_mjd = sa.Column(sa.Float)

    lines = relationship('Line', back_populates="linetimes")

    def __init__(self, start_t, end_t, t_format="tai"):#start_t, end_t,  t_format="tai"):
        start_t = BasicTime(start_t, t_format)
        end_t = BasicTime(end_t, t_format)

        self.start_tai = start_t.tai
        self.end_tai = end_t.tai

        self.start_mjd = start_t.mjd
        self.end_mjd = end_t.mjd


#class LineTime(Base):
#    __tablename__ = "linetimes"
#    id = sa.Column(sa.Integer, primary_key=True)
#
#    start_tai = sa.Column(sa.Float)
#    start_mjd = sa.Column(sa.Float)
#
#    end_tai = sa.Column(sa.Float)
#    end_mjd = sa.Column(sa.Float)
##    iso = sa.Column(sa.String(23))
#
#    lines = relationship('Line', back_populates="linetimes")
#
#    def __init__(self, start_t, end_t, t_format="tai"):
#        if t_format.lower()=="tai":
#            self._init_tai(start_t, end_t)
#        elif t_format.lower()=="mjd":
#            self._init_mjd(start_t, end_t)
#        else:
#            raise ValueError("Unrecognized time format")
#
#
#    def _init_tai(self, start_t, end_t):
#        self.start_tai = start_t
#        self.start_mjd = start_t/(24.0*3600.0)
#
#        self.end_tai = end_t
#        self.end_mjd = end_t/(24.0*3600.0)
#
#
#    def _init_mjd(self, start_t, end_t):
#        self.start_mjd = start_t
#        self.start_tai = start_t*(24.0*3600.0)
#
#        self.end_mjd = end_t
#        self.end_tai = end_t*(24.0*3600.0)
#
#    def __repr__(self):
#        return str(self.tai)
#
#    def __eq__(self, other):
#        #mjd time is in seconds and offers a much more
#        #precise way of comparing time than tai which is in days.
#        if self.mjd == other.mjd:
#            return True
#        return False
#
#    def __lt__(self, other):
#        if self.mjd < other.mjd:
#            return True
#        return False
#
#    def __gt__(self, other):
#        return not self.__lt__(other)
#
#    def __le__(self, other):
#        if self.__lt__(other) or self.__eq__(other):
#            return True
#        return False
#
#    def __ge__(self, other):
#        return not self.__le__(other)

