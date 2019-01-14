"""Frame represents a single SDSS image. On a single CCD there can be up to 3
such frames simultaneously, slightly overlapped on top and bottom edges. It is
not clear to me how to resolve a Frame's position within a CCD due to the SDSS'
drift-scan method.

Frames can only exist within a CCD and CCD's are placed in an fiter x camcol
grid in the CCD plane where the distance between camcols is only slightly less
than the size of the CCD itself so that the gaps can be filled in by another
run.

A single Frame can contain many Events. 
"""
import sqlalchemy as sql
from sqlalchemy.orm import relationship

from astropy.time import Time

from lfd.results import Base
from lfd.results import __query_aliases as query_aliases
from lfd.results.basictime import BasicTime
from lfd.results.utils import session_scope

__all__ = ["Frame"]


class Frame(Base):
    """Class Frame maps table 'frames'. Corresponds to an SDSS frame. A frame
    is uniquely defined by the set (run, camcol, filter, field). For in-depth
    see datamodel: https://data.sdss.org/datamodel/files/BOSS_PHOTOOBJ/frames/RERUN/RUN/CAMCOL/frame.html

    Parameters
    ----------
    run : int
      run id (composite PrimaryKey)
    camcol : int
      camcol id (composite PrimaryKey)
    filter : str
      filter id (composite PrimaryKey)
    field : int
      field id (composite PrimaryKey)
    crpix1 : int
      x frame coordinate of the reference central pixel
    crpix2 : int
      y frame coordinate of the reference central pixel
    crval1 : float
      RA on-sky coordinates of the reference pixel (degrees)
    crval2 : float
      DEC on-sky coordinate of the reference pixel
    cd11 : float
      change of RA per column pixel
    cd12 : float
      change of RA per row pixel
    cd21 : float
      change of DEC per column pixel
    cd22 : float
      chage of DEC per row pixel
    t : BasicTime
      time of start of frame exposure
    events : sql.relationship
      list of all event(s) registered on this frame, a one to many
      relationship to events

    Example
    -------

    Almost everything is not nullable so supply everything:

    >>> foo = Frame(run, camcol, filter, field, crpix1, cprix2, crval1, crval2,
                    cd11, cd21, cd22, t)

    i.e.

    >>> foo = Frame(2888, 1, 'i', 139, 741, 1024, 119, 23, 1, 1, 1,
                    4575925956.49)

    Time can be given as SDSS TAI or any of the other formats supported by
    Astropy Time Object. In the DB itself it is always forced to the SDSS TAI
    time format.

    """

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
                          cascade="save-update,delete,expunge", lazy="joined",
                          innerjoin=True)

    def __init__(self, run, camcol, filter, field, crpix1, crpix2, crval1, crval2,
                 cd11, cd12, cd21, cd22, t, **kwargs):
        """Supply everything:

        >>> foo = Frame(run, camcol, filter, field, crpix1, cprix2, crval1,
                        crval2, cd11, cd21, cd22, t)

        i.e.:

        >>> foo = Frame(2888, 1, 'i', 139, 741, 1024, 119.211, 23.321, 1, 1, 1,
                        4575925956.49)

        Time can be given as Astropy Time Object, SDSS TAI format or any of the
        formats supported by Astropy Time object.

        """

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
        t = repr(self.t).split("results.")[-1][:-1]
        return "<{0}.{1}(run={2}, camcol={3}, filter={4}, frame={5}, "\
            "t={6})>".format(m, n, self.run, self.camcol, self.filter,
                             self.field, t)

    def __str__(self):
        return "Frame(run={0}, camcol={1}, filter={2}, field={3}, {4})".format(
            self.run, self.camcol, self.filter, self.field, self.t.iso)

    @classmethod
    def query(cls, condition=None):
        """Class method that used to query the Frame ('frames') table. Returns
        a Query object. Appropriate for interactive work as Session remains open
        for the lifetime of the Query. See results package help to see details.

        If condition is supplied it is interpreted as an SQL string query. It's
        suffiecient to use mapped class names and their attributes as the
        translation to table and column names will be automaticall performed.

        Example
        -------
        Frame.query("Frame.run > 2").first()
        Frame.query("field == 1 and filter == 'i'").all()
        Frame.query("Event.y1 > 2).all()

        """

        if condition is None:
            with session_scope() as s:
                return s.query(cls).join("events")

        for key, val in query_aliases.items():
            condition = condition.replace(key, val)

        with session_scope() as s:
            return s.query(cls).join("events").filter(sql.text(condition))
