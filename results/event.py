import sqlalchemy as sql
from sqlalchemy.orm import relationship, composite

from .frame import Frame
from .point import Point
from .basictime import LineTime

#from results import Session
from results import Base

__all__ = ["Event"]

class Event(Base):
    __tablename__ = "events"

    id = sql.Column(sql.Integer, primary_key=True)

    #composite foreign keys are hard
    _run    = sql.Column(sql.Integer)
    _camcol = sql.Column(sql.Integer)
    _filter = sql.Column(sql.String)
    _field  = sql.Column(sql.Integer)

    frame   = relationship("Frame", back_populates="events")
    __table_args__ = (sql.ForeignKeyConstraint([_run, _camcol, _filter, _field],
                                               [Frame.run, Frame.camcol,
                                                Frame.filter, Frame.field],
                                               onupdate="CASCADE",
                                               ondelete="SET NULL"), {})

    _x1 = sql.Column(sql.Integer)
    _y1 = sql.Column(sql.Integer)
    _x2 = sql.Column(sql.Integer)
    _y2 = sql.Column(sql.Integer)
    _line_start_time = sql.Column(sql.Float)
    _line_end_time   = sql.Column(sql.Float)

    lt = composite(LineTime, _line_start_time, _line_end_time)
    p1 = composite(Point, _x1, _y1, _camcol, _filter)
    p2 = composite(Point, _x2, _y2, _camcol, _filter)

    def __init__(self, x1, y1, x2, y2, frame, start_t=None, end_t=None):
        self._run    = frame.run
        self._camcol = frame.camcol
        self._filter = frame.filter
        self._field  = frame.field

        self._x1 = x1
        self._y1 = y1
        self._x2 = x2
        self._y2 = y2

#        self.frame_id = frame.id

        self._line_start_time = start_t
        self._line_end_time = end_t

    @property
    def run(self):
        return self.frame.run

    @run.setter
    def run(self, val):
        self._run = val
        self.frame.run = val

    @property
    def camcol(self):
        return self.frame.camcol

    @camcol.setter
    def camcol(self, val):
        self._camcol = val
        self.frame.camcol = val

    @property
    def filter(self):
        return self.frame.camcol

    @filter.setter
    def filter(self, val):
        self._filter = val
        self.frame._filter = val

    @property
    def field (self):
        return self.frame.field

    @field.setter
    def field (self, val):
        self._field = val
        self.frame.field = val

    @property
    def x1(self):
        return self.p1.x

    @x1.setter
    def x1(self, val):
        self.p1.x = val
        self._x1 = self.p1._fx

    @property
    def y1(self):
        return self.p1.y

    @x1.setter
    def y1(self, val):
        self.p1.y = val
        self._y1 = self.p1._fy

    @property
    def x2(self):
        return self.p2.x

    @x2.setter
    def x2(self, val):
        self.p2.x = val
        self._x2 = self.p2._fx

    @property
    def y2(self):
        return self.p2.y

    @y2.setter
    def y2(self, val):
        self.p2.y = val
        self._y2 = self.p2._fy

    def useCoordSys(self, coordsys):
        self.p1.useCoordsys(coordsys)
        self.p2.useCoordsys(coordsys)

    def __repr__(self):
        m = self.__class__.__module__
        n = self.__class__.__name__
        lt = repr(self.lt).split("basictime.")[-1][:-1]
        f = repr(self.frame).split("results.")[-1][:-1]
        p1 = repr(self.p1).split("point.")[-1][:-1]
        p2 = repr(self.p2).split("point.")[-1][:-1]
        return "<{0}.{1}({4}, {2}, {3}, {5})>".format(m, n, p1, p2,
                                                            f, lt)
