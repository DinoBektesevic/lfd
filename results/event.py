import sqlalchemy as sql
from sqlalchemy.orm import relationship, composite, validates
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method

from .frame import Frame
from .point import Point, Line
from .basictime import BasicTime, LineTime
from .coord_conversion import convert_frame2ccd
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
    id      - PrimaryKey, autoincremental
    _run    - run id (ForeignKey)
    _camcol - camcol id (ForeignKey)
    _filter - filter id (ForeignKey)
    _field  - field id (ForeignKey)
    frame   - Frame on which the linear feature was detected, a many to one
              relationship to frames
    x1      - x frame coordinate of a point belonging to the linear feature
    y1      - y frame coordinate of a point belonging to the linear feature
    x2      - x frame coordinate of a point belonging to the linear feature
    y2      - y frame coordinate of a point belonging to the linear feature
    cx1     - x ccd coordinate of a point belonging to the linear feature
    cy1     - y ccd coordinate of a point belonging to the linear feature
    cx2     - x ccd coordinate of a point belonging to the linear feature
    cy2     - y ccd coordinate of a point belonging to the linear feature
    p1      - composite Column mapping x1, y1 to a point p1, see class Point
    p2      - composite Column mapping x2, y2 to a point p2, see class Point
    start_t - if possible to calculate, the time of the earliest detection of
              the linear feature on the frame, see class BasicTime
    end_t   - if possible to calculate the latest time of detection on the
              frame, see class BasicTime
    lt      - not very usefull, see class LineTime

      Usage and Notes
    -------------------
    Values of x1, y1, x2 and y2 coordinates are always kept in the 'frame'
    coordinate system. The values of the coordinates in the ccd coordinate
    system are calculated on the fly and are not stored. Point (i.e. p1, p2)
    objects will calculate and keep the coordinates in both coordinate systems.
    Any change to any of the coordinate attributes will update all the values,
    thus maintaining consistency during use, however only by using the points
    p1 and p2 will not bear overhead of recalculating the coordinate values.
    Cases where just a quick
    """
    __tablename__ = "events"
    id = sql.Column(sql.Integer, primary_key=True)

    _run    = sql.Column(sql.Integer)
    _camcol = sql.Column(sql.Integer)
    _filter = sql.Column(sql.String(length=1))
    _field  = sql.Column(sql.Integer)

    x1 = sql.Column(sql.Float, nullable=False)
    y1 = sql.Column(sql.Float, nullable=False)
    x2 = sql.Column(sql.Float, nullable=False)
    y2 = sql.Column(sql.Float, nullable=False)

    cx1 = sql.Column(sql.Float, nullable=False)
    cy1 = sql.Column(sql.Float, nullable=False)
    cx2 = sql.Column(sql.Float, nullable=False)
    cy2 = sql.Column(sql.Float, nullable=False)

    start_t = sql.Column(BasicTime)
    end_t   = sql.Column(BasicTime)

    lt = composite(LineTime, start_t, end_t)
    p1 = Point(x1, y1)#, _camcol, _filter, cx=cx1, cy=cy1)
    p2 = Point(x2, y2)#, _camcol, _filter, cx=cx2, cy=cy2)
#    l = Line(x1, y1, x2, y2, _camcol, _filter, cx1, cy1, cx2, cy2)

    #http://docs.sqlalchemy.org/en/latest/orm/relationship_persistence.html#mutable-primary-keys-update-cascades
    __table_args__ = (
        sql.ForeignKeyConstraint(['_run', '_camcol', "_filter", "_field"],
                                 ['frames.run', 'frames.camcol', "frames.filter",
                                  "frames.field"], onupdate = "CASCADE"),{}
	  )

    frame = relationship("Frame", back_populates="events")

    def __init__(self, x1, y1, x2, y2, frame, start_t=None, end_t=None,
                 coordsys="frame"):

        self.frame = frame
        self.coordsys = coordsys

        p1 = Point(x1, y1, frame.camcol, frame.filter)
        p2 = Point(x2, y2, frame.camcol, frame.filter)

        self.x1  = p1.x
        self.y1  = p1.y
        self.cx1 = p1.cx
        self.cy1 = p1.cy

        self.x2  = p2.x 
        self.y2  = p2.y 
        self.cx2 = p2.cx
        self.cy2 = p2.cy

        self.p1 = p1
        self.p2 = p2

        self.line_start_time = start_t
        self.line_end_time   = end_t

    def __repr__(self):
        m = self.__class__.__module__
        n = self.__class__.__name__
        f = repr(self.frame).split("results.")[-1][:-1]
        p1 = repr(self.p1).split("point.")[-1][:-1]
        p2 = repr(self.p2).split("point.")[-1][:-1]
        st = self.start_t.iso if self.start_t is not None else None
        et = self.end_t.iso if self.end_t is not None else None
        return "<{0}.{1}({4}, {2}, {3}, {5})>".format(m, n, p1, p2, f, st, et)

    def useCoordSys(self, coordsys):
        self.p1.useCoordSys(coordsys)
        self.p2.useCoordSys(coordsys)


#    @validates("x1")
#    def validate_x1(self, key, value):
#        if all((self.x1, self.y1)) and self.p1 is not None:
#            self.p1.move(value, self.y1, alert=False)
#            self.cx1 = self.p1._cx
#        return value
#
#    @validates("y1")
#    def validate_y1(self, key, value):
#        if all((self.x1, self.y1)) and self.p1 is not None:
#                self.p1._fy = value
#        return value
#
#    @validates("x2")
#    def validate_x2(self, key, value):
#        if all((self.x2, self.y2)) and self.p2 is not None:
#            self.p2._fx = value
#        return value
#
#    @validates("y2")
#    def validate_y2(self, key, value):
#        if all((self.x2, self.y2)) and self.p2 is not None:
#            self.p2._fy = value
#        return value

    @classmethod
    def query(cls, condition=None):
        if condition is None:
            with session_scope() as s:
                return s.query(cls).join("frame")

        for key, val in query_aliases.items():
            condition = condition.replace(key, val)

        with session_scope() as s:
            return s.query(cls).join("frame").filter(sql.text(condition))

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

    def __getconv(self, x, y, which):
        return convert_frame2ccd(x, y, self._camcol, self._filter)[which]

    def __setconv(self, x, y, which):
        cordsys = getattr(self, which+".coordsys")

#   @hybrid_property
#   def cx1(self):
#       return self._cx1
#
#   @cx1.setter
#   def cx1(self, val):
#       if all((self.x1, self.y1)) and self.p1 is not None:
#           self.p1.move(val, self._cy1, coordsys="ccd", alert=False)
#       self._cx1 = val        
#
#   @hybrid_property
#   def cy1(self):
#       return self._cy1
#
#   @cx1.setter
#   def cy1(self, val):
#       if all((self.x1, self.y1)) and self.p1 is not None:
#           self.p1.move(self._cx1, val, coordsys="ccd", alert=False)
#       self._cx1 = val

#
#    @hybrid_property
#    def cx2(self):
#        return self.__getconv(self.x1, self.y2, 0)
#
#    @hybrid_property
#    def cy2(self):
#        return self.__getconv(self.x1, self.y2, 1)
#
#    @cx1.setter
#    def cx1(self, val):
#        if self.p1.coordsys == "ccd":
#            self.p1.x = val
#        else:
#            self.p1.useCoordSys("ccd")
#            self.p1.x = val
#            self.p1.useCoordSys("frame")

