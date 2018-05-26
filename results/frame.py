import sqlalchemy as sql
from sqlalchemy.orm import relationship, composite

from .basictime import BasicTime
#from LFDS3.results import Base
from . import Base

__all__ = ["Frame"]

class Frame(Base):
    __tablename__ = "frames"
    #id = sql.Column(sql.Integer, primary_key=True)

    run = sql.Column(sql.Integer, primary_key=True)
    camcol = sql.Column(sql.Integer, primary_key=True)
    filter = sql.Column(sql.String, primary_key=True)
    field = sql.Column(sql.Integer, primary_key=True)

    crpix1 = sql.Column(sql.Float)
    crpix2 = sql.Column(sql.Float)

    crval1 = sql.Column(sql.Float)
    crval2 = sql.Column(sql.Float)

    cd11 = sql.Column(sql.Float)
    cd12 = sql.Column(sql.Float)
    cd21 = sql.Column(sql.Float)
    cd22 = sql.Column(sql.Float)

    #again how to map a single column to a class
    _t = sql.Column(sql.Float)
    _format = sql.Column(sql.String, default="tai")
    t = composite(BasicTime, _t, _format)

    events = relationship("Event", back_populates="frame")

    def __init__(self, run, camcol, filter, field, crpix1, crpix2,
                 crval1, crval2, cd11, cd12, cd21, cd22, t, format="tai"):
        self.run = run
        self.camcol = camcol
        self.filter = filter
        self.field = field

        self.crpix1 = crpix1
        self.crpix2 = crpix2

        self.crval1 = crval1
        self.crval2 = crval2

        self.cd11 = cd11
        self.cd12 = cd12
        self.cd21 = cd21
        self.cd22 = cd22

        self._t = t
        self._format = format

    @property
    def tai(self):
        return self.t.tai

    @tai.setter
    def tai(self, val):
        self.t._init_tai(val)
        self._t = self.t.tai

    @property
    def mjd(self):
        return self.t.mjd

    @mjd.setter
    def mjd(self, val):
        self.t._init_mjd(t)
        self._t = self.t.tai

    @property
    def iso(self):
        return self.t.iso
    @iso.setter
    def iso(self):
        pass

    def __repr__(self):
        m = self.__class__.__module__
        n = self.__class__.__name__
        t = repr(self.t).split("basictime.")[-1][:-1]
        return "<{0}.{1}(run={2}, camcol={3}, filter={4}, frame={5}, "\
            "t={6})>".format(m, n, self.run, self.camcol, self.filter,
                             self.field, t)
