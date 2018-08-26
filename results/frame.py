import sqlalchemy as sql
from sqlalchemy.orm import relationship

from astropy.time import Time

from .basictime import BasicTime
from . import Base

__all__ = ["Frame"]


class Frame(Base):
    __tablename__ = "frames"
    run    = sql.Column(sql.Integer, primary_key=True)
    camcol = sql.Column(sql.Integer, primary_key=True)
    filter = sql.Column(sql.String(length=1), primary_key=True)
    field  = sql.Column(sql.Integer, primary_key=True)

    crpix1 = sql.Column(sql.Float, nullable=False)
    crpix2 = sql.Column(sql.Float, nullable=False)
    crval1 = sql.Column(sql.Float, nullable=False)
    crval2 = sql.Column(sql.Float, nullable=False)

    cd11 = sql.Column(sql.Float, nullable=False)
    cd12 = sql.Column(sql.Float, nullable=False)
    cd21 = sql.Column(sql.Float, nullable=False)
    cd22 = sql.Column(sql.Float, nullable=False)

    t = sql.Column(BasicTime, nullable=False)

    #http://docs.sqlalchemy.org/en/latest/orm/cascades.html
    events = relationship("Event", back_populates="frame", passive_updates=False,
                          cascade="save-update, delete")

    def __init__(self, run, camcol, filter, field, crpix1, crpix2, crval1, crval2,
                 cd11, cd12, cd21, cd22, t, **kwargs):
        self.run    = run
        self.camcol = camcol
        self.filter = filter
        self.field  = field

        self.crpix1 = crpix1
        self.crpix2 = crpix2

        self.crval1 = crval1
        self.crval2 = crval2

        self.cd11 = cd11
        self.cd12 = cd12
        self.cd21 = cd21
        self.cd22 = cd22

        if isinstance(t, Time):
            self.t = t
        else:
            format = kwargs.pop("format", "sdss-tai")
            if format == "sdss-tai":
                self.t = Time(t/(24*3600.), format="mjd")
            else:
                self.t = Time(t, format=format)


    def __repr__(self):
        m = self.__class__.__module__
        n = self.__class__.__name__
        return "<{0}.{1}(run={2}, camcol={3}, filter={4}, frame={5}, "\
            "t={6})>".format(m, n, self.run, self.camcol, self.filter,
                             self.field, self.t.iso)
