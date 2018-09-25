import sqlalchemy as sql
from sqlalchemy.orm import relationship, composite, validates
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method

from astropy.time import Time

from .frame import Frame
from .point import Point
from .basictime import BasicTime, LineTime
from .coord_conversion import convert_frame2ccd, convert_ccd2frame
from .utils import session_scope

from . import Base
from . import __query_aliases as query_aliases

__all__ = ["Event"]


class Event(Base):
    """Class Event maps table 'events'. Corresponds to a single linear feature
    detection. Contains the measured properties of the feature and links to the
    Frame on which it was detected.

      Attributes
    ----------------
    id       - PrimaryKey, autoincremental
    _run     - run id (ForeignKey)
    _camcol  - camcol id (ForeignKey)
    _filter  - filter id (ForeignKey)
    _field   - field id (ForeignKey)
    frame    - Frame on which the linear feature was detected, a many to one
               relationship to frames
    x1, y1   - x, y frame coordinates of a point 1 of the linear feature
    x2, y2   - x, y frame coordinates of a point 2 of the linear feature
    cx1, cy2 - x, y ccd coordinates of a point 1 of the linear feature
    cx2, cy2 - x, y ccd coordinates of a point 2 of the linear feature
    p1       - see class Point composite Column mapping of x1, y1 to a point p1
    p2       - see class Point,composite Column mapping of x2, y2 to a point p2
    start_t  - if possible, the time of the first detection of the linear
               feature on the frame, see class BasicTime
    end_t    - if possible, the time of the last detection of the linear
               feature on the frame, see class BasicTime
    lt       - not very usefull, see class LineTime

      Usage
    ----------------
    A Frame object reference is required. See lfd.results.frame.Frame for
    documentation. At minimum, supply the Frame object and coordinates of two
    points defining a line:
        foo = Event(Frame, 1, 1, 2, 2)
    By default the coordinates are considered to be in "frame" coordinate sys.

    Optionally it is possible to specify the "ccd" as the reference coordinate
    sys, then the supplied coordinates are not assumed to be in the "frame"
    coord. sys:
        foo = Event(Frame, 1, 1, 2, 2, coordsys="ccd")
    CAUTION: If the Frame camcol!=1 and filter!="r" an Error will be raised.
    It is not possible to have CCD coordinates (1, 1) or (2, 2) except on the
    first chip of the CCD-array which is the camcol=1, filter='r' chip.

    Additionally all values could be supplied:
        foo = Event(Frame, 1, 1, 2, 2, 1, 1, 2, 2)
    or verbosely:
        foo = Event(frame=Frame, x1=1, y1=1, x2=2, y2=2,
                    cx1=1, cy1=1, cx2=2, cy2=2, coordsys="frame")
    or on an example of a different CCD (4, 'i'):
        foo = Event(f, 1, 1, 1, 1,
                    11376.462868, 2709.4435401, 11376.462868, 2709.4435401)
    CAUTION: This will only be possible if frame is set to correct CCD of the
    CCD array, as explained, and if x1=cx1, y1=cy1, x2=cx2 and cy2=y2. Any
    inconsistency in the coordinates would cause an error at instantiation.

    It is possible to submit start or end time of the linear feature in any
    the following formats: Astropy Time object, float number in mjd format,
    float number in sdss-tai format:
    Astropy Time Object - supply an instantiated Astropy Time Object:
        st = astropy.time.Time(58539.0, format="mjd")
        et = astropy.time.Time("2019-02-25 00:00:10.000")
        foo = Event(frame, 1, 1, 2, 2, start_t=st, end_t=et)
    Any Astropy Time supported format such as mjd, iso, isot, jd etc...
        foo = Event(frame, 1, 1, 2, 2, start_t= 63072064.184, format="cxcsec")
    the SDSS modified tai format:
        foo = Event(frame, 1, 1, 2, 2, end_t=4575925956.49, format="sdss-tai")


      Important Notes
    -------------------
    All values are modifiable which requries consistency checking. Consistency
    is checked only at instantiation time! It is possible to exit a completely
    consistent state. This is a feature not a bug.

    Non-prefixed coordinates are properties of the Event class (i.e. x1, y1...)
    and are "hot-wired" to the underlying Point object. Point object handles
    the coord conversions and maintains consistency among the coordinates
    during interactive work.
    Point objects are dependant on the Frame object to provide a reference point
    for conversion between the two coordinate systems. Therefore, changing the
    Event's Frame should update the Event's coordinates but vice-versa is only
    enforced at instantiation time.
    Coordinates are allowed to exit a frame without changing the frame attributes.
    This is intended so that the Point objects can temporarily be moved outside
    of the Frame limits to enable better fit to the linear feature and other
    exploratory behaviour. For example for a Frame(camcol=2, filter="u") it is
    possible to do:
    #           x1 y1  x2 y2
    e = Event(f, 0, 0, 0, 0)
    e.cx1
    >>> 3792.82
    e.x1 = -1
    >>> 3791.82
    Technically, that is minus first pixel of that particular CCD in the CCD
    array and technically is not attributable to a CCD (i.e. it is undefined in
    the "frame" coordinate system), yet the coordsystem, filter nor the camcol
    are changed. This is intentional, as it allows loops across the CCD array
    coordinates, resolving individual CCD IDs once over them, better line fits
    etc...

    Since these values should never be commited to the DB by the users, the
    Event's Point objects are availible to the user under p1 and p2 attributes.
    It is recommended that they are always used to assign, move or otherwise
    change the coordinates instead acting on the table attributes themselves.

    Point objects will issue warnings when these inconsistent situations occur,
    thus resolving the ambiguity of these situations. However, recognizing that
    the majority of operations involving points will not involve such situati-
    ons and recognizing the importance of expression brevity, clarity and gene-
    ral practicality the coordinate table attributes have been made availible
    to the user as such properties.

    Unrelated, the times of the linear feature are stored in the DB in the SDSS
    TAI format. There are some caveats when converting this time to MJD. See:
    https://www.sdss.org/dr12/help/glossary/#tai
    """
    __tablename__ = "events"
    id = sql.Column(sql.Integer, primary_key=True)

    # a copy of each of the foreign key components must be kept for join to work
    _run    = sql.Column(sql.Integer)
    _camcol = sql.Column(sql.Integer)
    _filter = sql.Column(sql.String(length=1))
    _field  = sql.Column(sql.Integer)

    # we hide the coordinates because they should be accessed through properties
    _x1 = sql.Column(sql.Float, nullable=False)
    _y1 = sql.Column(sql.Float, nullable=False)
    _x2 = sql.Column(sql.Float, nullable=False)
    _y2 = sql.Column(sql.Float, nullable=False)
    
    _cx1 = sql.Column(sql.Float, nullable=False)
    _cy1 = sql.Column(sql.Float, nullable=False)
    _cx2 = sql.Column(sql.Float, nullable=False)
    _cy2 = sql.Column(sql.Float, nullable=False)

    start_t = sql.Column(BasicTime)
    end_t   = sql.Column(BasicTime)

    # the order in instantiation of the composite and the Point class itself is
    # very important. The Point will resolve its init procedures itself but that
    # is based of init parameters being None or not - which is why they're all
    # init to None in the Poit __init__ signature. LineTime is useless.
    lt = composite(LineTime, start_t, end_t)
    p1 = composite(Point, _x1, _y1, _cx1, _cy1, _camcol, _filter)
    p2 = composite(Point, _x2, _y2, _cx2, _cy2, _camcol, _filter)

    #http://docs.sqlalchemy.org/en/latest/orm/relationship_persistence.html#mutable-primary-keys-update-cascades
    # THIS IS THE ONLY WAY to make sure foreign keys work as foreign composite
    # key. It is a many-to-one relationship where 1 frame can have many events.
    # On-update cascades shoud ensure that an update of frames row all events
    # rows are updated; and not orphaned.
    __table_args__ = (
        sql.ForeignKeyConstraint(['_run', '_camcol', "_filter", "_field"],
                                 ['frames.run', 'frames.camcol', "frames.filter",
                                  "frames.field"], onupdate = "CASCADE"),{}
	  )

    # back_populates will create an attribute on Event that will make the Frame
    # object accessible through Event.
    frame = relationship("Frame", back_populates="events")


    def __init__(self, frame, x1=None, y1=None, x2=None, y2=None, cx1=None,
                 cy1=None, cx2=None, cy2=None, start_t=None, end_t=None,
                 coordsys="frame", **kwargs):
        """foo = Event(frame=Frame, x1=1, y1=1, x2=2, y2=2,
                       cx1=1, cy1=1, cx2=2, cy2=2,
                       start_t=58539.0, end_t=58541.0
                       format="mjd", coordsys="frame")

        Frame object reference is required alongside with 4 coordinates that
        define two points P1 and P2 that lie on the linear feature. They can be
        in either the "frame" or "ccd" coordinate system.

        foo = Event(Frame, 1, 1, 2, 2)
        foo = Event(Frame, 1, 1, 2, 2, coordsys="ccd")
        foo = Event(Frame, 1, 1, 2, 2, 1, 1, 2, 2)
        foo = Event(f, 1, 1, 1, 1,
                    11376.462868, 2709.4435401, 11376.462868, 2709.4435401,
                    58539.0, 58541.0,
                    format="mjd", coordsys="frame")
        See class docstring for more details.
        """
        p1 = Point(x1, y1, cx1, cy1, frame.camcol, frame.filter, coordsys)
        p2 = Point(x2, y2, cx2, cy2, frame.camcol, frame.filter, coordsys)

        if any([frame.filter != p1._filter,
                frame.filter != p2._filter,
                frame.camcol != p1._camcol,
                frame.camcol != p2._camcol]):
            msg = ("Instantiation inconsistency: Supplied coordinates do not "
                   "match the given Frame. Expected camcol={0}, filter={1} but "
                   "calculated P1(camcol={2}, filter={3}) and "
                   "P2(camcol={4}, filter={5})")
            raise ValueError(msg.format(frame.camcol, frame.filter, p1.camcol,
                                        p1.filter, p2.camcol, p2.filter))

        self.p1 = p1
        self.p2 = p2

        # assume sdss-tai format in case none is supplied.
        t_format = kwargs.pop("format", "sdss-tai")
        self.start_t = self.__init_t(start_t, t_format)
        self.end_t   = self.__init_t(end_t, t_format)

        self.frame = frame

    def __init_t(self, t, format):
        # It might not be possible to determine the times of the linear
        # feature's first and last recording so we return None when that is the
        # case. Otherwise we return the Astropy's Time object. This discrepancy
        # does not exist for Frame because t can not be None in that case.
        if t is None:
            return None
        if isinstance(t, Time):
            self.t = t
        elif format == "sdss-tai":
            self.t = Time(t/(24*3600.), format="mjd")
        else:
            self.t = Time(t, format=format)

    def __repr__(self):
        m = self.__class__.__module__
        n = self.__class__.__name__
        f = repr(self.frame).split("results.")[-1][:-1]
        p1 = repr(self.p1).split("results.")[-1][:-1]
        p2 = repr(self.p2).split("results.")[-1][:-1]
        st = self.start_t.iso if self.start_t is not None else None
        et = self.end_t.iso if self.end_t is not None else None
        return "<{0}.{1}({4}, {2}, {3}, {5})>".format(m, n, p1, p2, f, st, et)

    def __str__(self):
        p1 = str(self.p1)
        p2 = str(self.p2)
        st = str(self.start_t)
        et = str(self.end_t)
        frame = str(self.frame)
        printstr = "Event({0}, {1}, {2}, {3}, {4})"
        return printstr.format(frame, p1, p2, st, et)

    @classmethod
    def query(cls, condition=None):
        """A class method that can be used to query the Event table. Appropriate
        for interactive work, not as appropriate for large codebase usage. See
        package help for more details on how the Session is kept open. Will
        return a query object, not the query result.

        If condition is supplied it is interpreted as a common string SQL. It's
        sufficient to use the names of mapped classes and their attributes as
        they will automatically be replaced by the correct table and column
        names.

        Examples:
        Event.query().all()
        Event.query().first()
        Event.query("run == 3").all()
        Event.query("Event.run > 3").all()
        Event.query("Frame.t > 4412911072y").all()
        Event.query("events.cx1 > 10000").all()
        Event.query("frames.filter == 'i'").all()
        """
        if condition is None:
            with session_scope() as s:
                return s.query(cls).join("frame")

        # the condition is essentially consistent of two 
        for key, val in query_aliases.items():
            if key[:1] in (["x", "y", "c"]):
                condition = condition.replace("."+key, "."+val)
            else:
                condition = condition.replace(key, val)

        with session_scope() as s:
            return s.query(cls).join("frame").filter(sql.text(condition))

    ###########################################################################
    ##################                frame                       #############
    ###########################################################################
    @hybrid_property
    def run(self):
        return self._run

    @hybrid_property
    def camcol(self):
        return self._camcol

    @hybrid_property
    def filter(self):
        return self._filter

    @hybrid_property
    def field(self):
        return self._field

    ###########################################################################
    ###################                 p1                       ##############
    ###########################################################################
    @hybrid_property
    def x1(self):
        return self._x1

    @x1.setter
    def x1(self, val):
        self.p1.x = val

    @hybrid_property
    def y1(self):
        return self._y1

    @y1.setter
    def y1(self, val):
        self.p1.y = val

    @hybrid_property
    def cx1(self):
       return self._cx1

    @cx1.setter
    def cx1(self, val):
        self.p1.cx = val

    @hybrid_property
    def cy1(self):
        return self._cy1

    @cy1.setter
    def cy1(self, val):
        self.p1.cy = val


    ###########################################################################
    ###################                 p2                       ##############
    ###########################################################################
    @hybrid_property
    def x2(self):
        return self._x2

    @x2.setter
    def x2(self, val):
        self.p2.x = val

    @hybrid_property
    def y2(self):
        return self._y2

    @y2.setter
    def y2(self, val):
        self.p2.y = val

    @hybrid_property
    def cx2(self):
        return self._cx2

    @cx2.setter
    def cx2(self, val):
        self.p2.cx = val

    @hybrid_property
    def cy2(self):
        return self._cy2

    @cy2.setter
    def cy2(self, val):
        self.p2.cy = val
