import sqlalchemy as sa
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


import time

class Timer(object):
    def __init__(self, verbose=False):
        self.verbose = verbose

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.end = time.time()
        self.secs = self.end - self.start
        self.msecs = self.secs * 1000  # millisecs
        if self.verbose:
            print 'elapsed time: %f ms' % self.msecs





#Base = declarative_base()
#
#class LineTime(Base):
#    __tablename__ = "linetimes"
#    id = sa.Column(sa.Integer, primary_key=True)
#
#    tai = sa.Column(sa.Float)
#    mjd = sa.Column(sa.Float)
#    
#    lines = relationship('Line', back_populates="linetimes")
#
#    def __init__(self, t, t_format="tai"):
#        if t_format.lower()=="tai":
#            self._init_tai(t)
#        elif t_format.lower()=="mjd":
#            self._init_mjd(t)
#        else:
#            raise ValueError("Unrecognized time format")
#
#    def _init_tai(self, t):
#        self.tai = t
#        self.mjd = t/(24.0*3600.0)
#
#    def _init_mjd(self, t):
#        self.tai = t*(24.0*3600.0)
#        self.mjd = t
#
#        
#class Line(Base):
#    __tablename__ = "lines"
#    
#    id = sa.Column(sa.Integer, primary_key=True)
#    
#    frame_id = sa.Column(sa.Integer, sa.ForeignKey('frames.id'), nullable=False)
#    linetime_id = sa.Column(sa.Integer, sa.ForeignKey('linetimes.id'), nullable=False)
#    
#    x1 = sa.Column(sa.Float)
#    y1 = sa.Column(sa.Float)
#    x2 = sa.Column(sa.Float)
#    y2 = sa.Column(sa.Float)
#
#
#    frame = relationship('Frame', back_populates='lines')
#    linetimes = relationship('LineTime', back_populates="lines")
#
#    def __init__(self, x1, y1, x2, y2, frame_id, linetime_id):
#        self.x1 = x1
#        self.y1 = y1
#        self.x2 = x2
#        self.y2 = y2
#        self.frame_id = frame_id
#        self.linetime_id = linetime_id
#
#
#frame_frametimes_t = sa.Table(
#    "frame_frametimes", Base.metadata,
#    sa.Column('frame_id', sa.Integer, sa.ForeignKey('frames.id'), nullable=False),
#    sa.Column('frametime_id', sa.Integer, sa.ForeignKey('frametimes.id'), nullable=False),
#)
#
#class FrameTime(Base):
#    __tablename__ = "frametimes"
#    id = sa.Column(sa.Integer, primary_key=True)
#  # add other columns here for your line time data, such as tai
#  # you should use unique constraints to make sure there is only one FrameTime object with the same corresponding time.
#    frames = relationship('Frame', secondary=frame_frametimes_t, back_populates="frametimes")
#
#class Frame(Base):
#    __tablename__ = "frames"
#    id = sa.Column(sa.Integer, primary_key=True)
#
#    run = sa.Column(sa.Integer)
#    camcol = sa.Column(sa.Integer)
#    filter = sa.Column(sa.String)
#    field = sa.Column(sa.Integer)
#
#    lines = relationship("Line", back_populates="frame")
#    frametimes = relationship("FrameTime", secondary=frame_frametimes_t, back_populates='frames')
#
#    def __init__(self, run, camcol, filter, field):
#        self.run = run
#        self.camcol = camcol
#        self.filter = filter
#        self.field = field

from .base import Base
from .frame import Frame
from .line import Line, LineTime

import os
if os.path.isfile("foo1.db"):
    os.remove("foo1.db")

engine = sa.create_engine('sqlite:///foo1.db', echo=True)
Base.metadata.create_all(engine)

session = sessionmaker()
session.configure(bind=engine)
session = session()

def parse(data):
    #some file reading and whatnot
    return {"tai":1, "run":1, "camcol":1, "filter":'i', "field":1,
            "x1":1, "y1":1, "x2":2, "y2":2}

tmp = parse("")

f = Frame(tmp["run"], tmp["camcol"], tmp["filter"], tmp["field"])
t = LineTime(tmp["tai"])
session.add_all([f, t])
session.commit()

line = Line.fromCoords(tmp["x1"], tmp["y1"], tmp["x2"], tmp["y2"],
                       tmp["camcol"], tmp["filter"], frame_id=f.id,
                       linetime_id=t.id)


#with Timer() as t1:
#    for i in range(1000000):
#        line.x1
#
#with Timer() as t2:
#    for i in range(1000000):
#        line.x2
#
#print """\n\n################################
#Difference between Basic and Point attribute lookup
#1 mil. calculations
#################################"""
#print "                     seconds"
#print "Point:           ", t1.msecs/1000.
#print "Basic:           ", t2.msecs/1000.
#print "diff:            ", ((t1.msecs-t2.msecs) if (t1.msecs > t2.msecs) else (t2.msecs-t1.msecs))/1000.
#print "speedup:         ", t1.msecs/t2.msecs if (t1.msecs > t2.msecs) else t2.msecs/t1.msecs
#

                


session.add(line)
#session.commit()





##
##import sqlalchemy as sa
##from sqlalchemy import Column, Integer
##from sqlalchemy.orm import relationship, sessionmaker
##from sqlalchemy.ext.declarative import declarative_base
##
##Base = declarative_base()
##
##class LineTime(Base):
##    __tablename__ = "linetimes"
##    id = Column(Integer, primary_key=True)
##    # add other columns here for your line time data, such as tai
##    # you should use unique constraints to make sure there is only one LineTime object with the same corresponding time.
##    lines = relationship('Line', back_populates="linetime")
##
##class Line(Base):
##    __tablename__ = "lines"
##    id = Column(Integer, primary_key=True)
##    frame_id = Column(Integer, sa.ForeignKey('frames.id'), nullable=False)
##    linetime_id = Column(Integer, sa.ForeignKey('linetimes.id'), nullable=False)
##    #add other columns here for your line data, such as coordinates
##    frame = relationship('Frame', back_populates='lines')
##    linetime = relationship('LineTime', back_populates="lines")
##
##frame_frametimes_t = sa.Table(
##    "frame_frametimes", Base.metadata,
##    sa.Column('frame_id', sa.Integer, sa.ForeignKey('frames.id'), nullable=False),
##    sa.Column('frametime_id', sa.Integer, sa.ForeignKey('frametimes.id'), nullable=False),
##)
##
##class FrameTime(Base):
##    __tablename__ = "frametimes"
##    id = Column(Integer, primary_key=True)
##
##    frames = relationship('Frame', secondary=frame_frametimes_t, back_populates="frametimes")
##
##
##class Frame(Base):
##    __tablename__ = "frames"
##    id = Column(Integer, primary_key=True)
##
##    run = sa.Column("run", sa.Integer)
##    camcol = sa.Column("camcol", sa.Integer)
##    filter = sa.Column("filter", sa.String)
##    field = sa.Column("field", sa.Integer)
##
##    lines = relationship("Line", back_populates="frame")
##    frametimes = relationship("FrameTime", secondary=frame_frametimes_t, back_populates='frames')
##
##
##import os
##if os.path.isfile("foo1.db"):
##    os.remove("foo1.db")
##    
##engine = sa.create_engine('sqlite:///foo1.db', echo=True)
##Base.metadata.create_all(engine)
##
##session = sessionmaker()
##session.configure(bind=engine)
##session = session()
##
##def parse(data):
##    #some file reading and whatnot
##    return {"tai":1, "run":1, "camcol":1, "filter":'1', "field":1,
##            "x1":1, "y1":1, "x2":1, "y2":1}
##
##tmp = parse("")
##
##f = Frame(run=1, camcol=1, field=1, filter='i')
##t = LineTime()
##session.add_all([f, t, l])
##session.commit()
##
##l = Line(frame_id = f.id, linetime_id = t.id)
##session.add(l)
##session.commit()
