import sqlalchemy as sql
from sqlalchemy.orm import relationship, composite

from .frame import Frame
from .point import Point
from .basictime import BasicTime, LineTime

from . import Base

__all__ = ["Event"]


class Event(Base):
    __tablename__ = "events"
    id = sql.Column(sql.Integer, primary_key=True)

    _run    = sql.Column(sql.Integer)
    _camcol = sql.Column(sql.Integer)
    _filter = sql.Column(sql.String(length=1))
    _field  = sql.Column(sql.Integer)

    x1 = sql.Column(sql.Integer, nullable=False)
    y1 = sql.Column(sql.Integer, nullable=False)
    x2 = sql.Column(sql.Integer, nullable=False)
    y2 = sql.Column(sql.Integer, nullable=False)

    start_t = sql.Column(BasicTime)
    end_t   = sql.Column(BasicTime)

    lt = composite(LineTime, start_t, end_t)
    p1 = composite(Point, x1, y1, _camcol, _filter)
    p2 = composite(Point, x2, y2, _camcol, _filter)

    #http://docs.sqlalchemy.org/en/latest/orm/relationship_persistence.html
    __table_args__ = (
        sql.ForeignKeyConstraint(['_run', '_camcol', "_filter", "_field"],
                                 ['frames.run', 'frames.camcol', "frames.filter",
                                  "frames.field"], onupdate = "CASCADE"),{}
	  )

    frame = relationship("Frame", back_populates="events")

    def __init__(self, x1, y1, x2, y2, frame, start_t=None, end_t=None):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

        self.line_start_time = start_t
        self.line_end_time   = end_t

        self.frame = frame

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
        self.p1.useCoordsys(coordsys)
        self.p2.useCoordsys(coordsys)

    @property
    def run(self):
        return self._run

    @property
    def camcol(self):
        return self._camcol

    @property
    def filter(self):
        return self._filter

    @property
    def field(self):
        return self._field

