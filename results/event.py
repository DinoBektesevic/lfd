import sqlalchemy as sql
from sqlalchemy.orm import relationship, composite, validates
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method

from astropy.time import Time

from .basictime import BasicTime, LineTime
from .frame import Frame
from .point import Point
from .coord_conversion import convert_frame2ccd, convert_ccd2frame
from .ccd_dimensions import W_CAMCOL, H_FILTER
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
    In short:
    1) x1, y1, cx2 ... are properties and _x1, _y1 ... are the actual column
       names
    2) always change the coordinates through properties, or better yet p1, p2
       Point objects
    3) Points interpret the coordinates in frame-referenced mode
    4) Frame properties can not be changed through Event
    5) If Frame is changed the changes won't reflect on Event untill DB commit
       is made.

    In long:
    Non-prefixed coordinates are properties of the Event class (i.e. x1, y1...).
    The column names are prefixed with an underscore (i.e. _x1, _cx1...) and
    should not be changed directly.
    Point objects handle the coord conversions and maintain consistency among
    the coordinates during interactive work. The table values are hot-wired to
    Point objects through composites and properties. Changing prefixed values
    directly can leave the DB in an inconsistent state from which it is hard
    to recover. Always use the properties of Event or, better yet, the Point
    objects themselves, available as attributes p1 and p2, to change coords.

    Point objects are dependant on the Frame object to provide a reference point
    for conversion between the two coordinate systems. Therefore, changing the
    Event's Frame should update the Event's coordinates, but this is only
    enforced at instantiation time. Because of this it is possible to exit the
    narrow definition of a consistent state when in interacive mode. If a Frame
    attribute is changed - that change will not reflect in the Event object
    until a DB commit is made.

    Because a frame reference must always be provided for an Event the Point
    will default to its referenced mode of interpreting the coordinates. Points
    are allowed to exist outside of CCD areas where their camcol, filter and
    'frame' coordinates are defined and an error will not be raised. For more
    details see Point class.

    Point objects will issue warnings or errors if inconsistent situations arise
    when a warning is issues, unless it's clearly understood and expected, the
    best course of action is to issue a rollback. DB could be sent to an
    inconsistent state otherwise.

    The start/end times are stored in the DB in the SDSS-TAI format. There are
    some caveats when converting this time to MJD.
    See: https://www.sdss.org/dr12/help/glossary/#tai
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

    # the order in instantiation of the composite and the Point class in __init__
    # itself is **very important**. The Point will resolve its init procedures
    # itself so that various different inits are possible, but this is based on
    # the order of init parameters and on their value (Truthy or None). If the
    # order of the init parameters in the __init__ function does not match the
    # order of parameters in the composite, when instantiating from the DB wrong
    # values will be sent as wrong parameters. Additionally _camcol and _filter
    # can not be in front of the _cx and _cy because __composite_values__ of
    # Point DO NOT CHANGE THEM so the x, y, cx, cy will try to map to
    # x, y, camcol, filter, cx, cy and because types won't be correct it will
    # default to None
    lt = composite(LineTime, start_t, end_t)
    p1 = composite(Point, _x1, _y1, _cx1, _cy1, _camcol, _filter)
    p2 = composite(Point, _x2, _y2, _cx2, _cy2, _camcol, _filter)

    #http://docs.sqlalchemy.org/en/latest/orm/relationship_persistence.html#mutable-primary-keys-update-cascades
    # THIS IS THE ONLY WAY to make sure foreign keys work as foreign composite
    # key. It is a many-to-one relationship where 1 frame can have many events.
    # On-update cascades shoud ensure that an update of frames row all events
    # rows are updated; and not orphaned; but only works on commit.
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
        # we check that the points are actually sensible and not inconsistent
        p1 = Point(x=x1, y=y1, cx=cx1, cy=cy1,
                   camcol=frame.camcol, filter=frame.filter, coordsys=coordsys)
        p2 = Point(x=x2, y=y2, cx=cx2, cy=cy2,
                   camcol=frame.camcol, filter=frame.filter, coordsys=coordsys)
        if any([frame.filter != p1._filter,
                frame.filter != p2._filter,
                frame.camcol != p1._camcol,
                frame.camcol != p2._camcol]):
            msg = ("Instantiation inconsistency: Supplied coordinates do not "
                   "match the given Frame. Expected camcol={0}, filter={1} but "
                   "calculated P1(camcol={2}, filter={3}) and "
                   "P2(camcol={4}, filter={5})")
            msg = msg.format(frame.camcol, frame.filter, p1.camcol, p1.filter,
                             p2.camcol, p2.filter)
            raise sql.exc.DataError(msg)

        # if they are we use them, because of Mutable Composite this updates
        # the relevant fields in the object immediatelly
        self.p1 = p1
        self.p2 = p2

        # the same is not true for frame - it's a relationship and won't fill in
        # object attributes untill commited to DB. So, we fill then in manually
        self.frame = frame
        self._run = frame.run
        self._camcol = frame.camcol
        self._filter = frame.filter
        self._field = frame.field

        # assume sdss-tai format in case format is not supplied.
        t_format = kwargs.pop("format", "sdss-tai")
        self.start_t = self.__init_t(start_t, t_format)
        self.end_t   = self.__init_t(end_t, t_format)



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
        # returns a string in following format:
        # <library.package.module.ClassName(all_class_components_and_origins)>
        m = self.__class__.__module__
        n = self.__class__.__name__
        f = repr(self.frame).split("results.")[-1][:-1]
        p1 = repr(self.p1).split("results.")[-1][:-1]
        p2 = repr(self.p2).split("results.")[-1][:-1]
        st = self.start_t.iso if self.start_t is not None else None
        et = self.end_t.iso if self.end_t is not None else None
        return "<{0}.{1}({4}, {2}, {3}, {5})>".format(m, n, p1, p2, f, st, et)

    def __str__(self):
        # returns a string in the following format:
        # Event(Frame, Point, Point, BasicTime, BasicTime)
        p1 = str(self.p1)
        p2 = str(self.p2)
        st = str(self.start_t)
        et = str(self.end_t)
        frame = str(self.frame)
        printstr = "Event({0}, {1}, {2}, {3}, {4})"
        return printstr.format(frame, p1, p2, st, et)

    def _findPointsOnSides(self, m, b):
        """Looking for an intersection of a horizontal/vertical borders with
        a line equation does not neccessarily return a point within the range
        we're looking for. It is easier and faster to do it manually.
        Each individual border will be checked manually and if it satisfies,
        two coordinates (defining a Point) will be appended to a list. Special
        cases of (0, 0) and (2048, 2048) will satisfy both border conditions
        and so will be duplicated in the result.
        Interestingly, if working from 'frame' reference system it's not
        neccessary to know which reference frame we're looking at.

          Params
        -------------------
        m - line slope
        b - line y intercept
        """
        # make new coords
        newx = []
        newy = []
        success = False

        # check vertical border x=0, then y=b, ignore if it's outside CCD
        if b >= 0 and b <= H_FILTER:
            newx.append(0)
            newy.append(b)

        # check the vertical border x=W_CAMCOL, then y = m*W_CAMCOL+b
        tmp = m*W_CAMCOL + b
        if tmp >= 0 and tmp <= W_CAMCOL:
            newx.append(W_CAMCOL)
            newy.append(tmp)

        # check the horizontal border y=0, then x = -b/m
        tmp = -b/m
        if tmp >= 0 and tmp <= W_CAMCOL:
            newx.append(tmp)
            newy.append(0)

        # check the horizontal border y=H_FILTER, then x = (H_FILTER-b)/m
        tmp = (H_FILTER-b)/m
        if tmp >= 0 and tmp <= W_CAMCOL:
            newx.append(tmp)
            newy.append(H_FILTER)

        return newx, newy


    def snap2ccd(self):
        """Snap the curent coordinates to the points of intersection of the
        reference frame CCD border and the linear feature.

        A negatively sloped 45° linear feature passes diagonally across the
        first CCD in the array (1, 'r'), cutting through both its corners. Such
        feature could be defined by P1(-1000, -1000) and P2(10000, 10000). Snap
        will determine the two border points P1(0,0) and P2(2048, 2048).
        """
        # calculate the line slope and intercept y=mx+b, pray it works, needs
        # checks for verticality and horizontality
        m = (self.y2-self.y1)/(self.x2-self.x1)
        b = -m*self.x1 + self.y1

        newx, newy = self._findPointsOnSides(m, b)

        # The pints (0,0) and (2048, 2048) are special cases since they belong
        # to both borders so returned results are duplicated.
        if (len(newx) == 2 and len(newy) == 2) or \
           (len(newx) == 4 and len(newy) == 4):
            self.x1 = newx[0]
            self.x2 = newx[1]
            self.y1 = newy[0]
            self.y2 = newy[1]
        else:
            msg = "Could not compute edge points, returned: P1{0} and P2{1}."
            raise ValueError(msg.format(newx, newy))



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
    def __check_sensibility(self, attr):
        if attr[-1:] == "1":
            camcol, filter = self.p1._camcol, self.p1._filter
        elif attr[-1:] == "2":
            camcol, filter = self.p2._camcol, self.p2._filter

        if camcol != self._camcol or filter != self._filter:
            msg = ("New camcol and filter ({0}, {1}) do not correspond to Frame "
                   "camcol and filter ({2}, {3}) anymore. If commited to DB it "
                   "will not be recoverable.")
            msg = msg.format(camcol, filter, self._camcol, self._filter)
            warnings.warn(msg, SyntaxWarning)

    @hybrid_property
    def x1(self):
        return self._x1

    @x1.setter
    def x1(self, val):
        self.p1._initFrame(val, self.y1, self.camcol, self.filter)

    @hybrid_property
    def y1(self):
        return self._y1

    @y1.setter
    def y1(self, val):
        self.p1._initFrame(self.x1, val, self.camcol, self.filter)

    @hybrid_property
    def cx1(self):
       return self._cx1

    @cx1.setter
    def cx1(self, val):
        self.p1._initCCD(val, self.cy1)
        self.__check_sensibility("cx1")

    @hybrid_property
    def cy1(self):
        return self._cy1

    @cy1.setter
    def cy1(self, val):
        self.p1._initCCD(self.cx1, val)
        self.__check_sensibility("cy1")


    ###########################################################################
    ###################                 p2                       ##############
    ###########################################################################
    @hybrid_property
    def x2(self):
        return self._x2

    @x2.setter
    def x2(self, val):
        self.p2._initFrame(val, self.y2, self.camcol, self.filter)

    @hybrid_property
    def y2(self):
        return self._y2

    @y2.setter
    def y2(self, val):
        self.p2._initFrame(self.x2, val, self.camcol, self.filter)

    @hybrid_property
    def cx2(self):
       return self._cx2

    @cx2.setter
    def cx2(self, val):
        self.p2._initCCD(val, self.cy2)
        self.__check_sensibility("cx2")

    @hybrid_property
    def cy2(self):
        return self._cy2

    @cy2.setter
    def cy2(self, val):
        self.p2._initCCD(self.cx2, val)
        self.__check_sensibility("cy2")
