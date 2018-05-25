import sqlalchemy as sql
from sqlalchemy import create_engine, ForeignKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, composite

from .point import Point
from .basictime import BasicTime, LineTime

########################################

engine = create_engine('sqlite:///:memory:', echo=False)
Base = declarative_base()



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




class Event(Base):
    __tablename__ = "events"

    id = sql.Column(sql.Integer, primary_key=True)

    #composite foreign keys are hard
    _run = sql.Column(sql.Integer)
    _camcol = sql.Column(sql.Integer)
    _filter = sql.Column(sql.String)
    _field = sql.Column(sql.Integer)
    frame = relationship("Frame", back_populates="events")
    __table_args__ = (ForeignKeyConstraint([_run, _camcol, _filter, _field],
                                           [Frame.run, Frame.camcol,
                                            Frame.filter, Frame.field],
                                           onupdate="CASCADE",
                                           ondelete="SET NULL"), {})

    _x1 = sql.Column(sql.Integer)
    _y1 = sql.Column(sql.Integer)
    _x2 = sql.Column(sql.Integer)
    _y2 = sql.Column(sql.Integer)
    _line_start_time = sql.Column(sql.Float)
    _line_end_time = sql.Column(sql.Float)

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


Base.metadata.create_all(engine)

Base.metadata.create_all(engine)

########################################

Session = sessionmaker(bind=engine)
session = Session()

tmp = list()
tmp.append(
    Frame(run=1, camcol=3, filter='i', field=1, crpix1=1, crpix2=1, crval1=1,
          crval2=1, cd11=1, cd12=1, cd21=1, cd22=1, t=4412911074.78)
)
tmp.append(
    Frame(run=1, camcol=4, filter='i', field=1, crpix1=1, crpix2=1, crval1=1,
          crval2=1, cd11=1, cd12=1, cd21=1, cd22=1, t=4412911074.78)
)
tmp.append(
    Frame(run=1, camcol=5, filter='r', field=1, crpix1=1, crpix2=1, crval1=1,
          crval2=1, cd11=1, cd12=1, cd21=1, cd22=1, t=4412911074.78)
)
tmp.append(
    Frame(run=3, camcol=4, filter='i', field=1, crpix1=1, crpix2=1, crval1=1,
          crval2=1, cd11=1, cd12=1, cd21=1, cd22=1, t=4412911074.78)
)

session.add_all(tmp)
session.commit()

#print ""
#print ""
#print "THIS IS FRAME ID: ", f.id
#print ""
#print ""

tmp2 = list()
tmp2.append(Event(x1=1, y1=1, x2=2, y2=2, frame=tmp[0]))
tmp2.append(Event(x1=2, y1=2, x2=3, y2=3, frame=tmp[1]))
tmp2.append(Event(x1=3, y1=3, x2=4, y2=4, frame=tmp[2]))
tmp2.append(Event(x1=4, y1=4, x2=5, y2=5, frame=tmp[3]))
session.add_all(tmp2)
session.commit()
