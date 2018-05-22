import os

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

if os.path.isfile("foo1.db"):
    os.remove("foo1.db")

engine = sa.create_engine('sqlite:///foo1.db', echo=False)

Base = declarative_base()
Base.metadata.create_all(engine)

session = sessionmaker()
session.configure(bind=engine)


class MetaEvent(Base):
    __tablename__ = "metaevent"

    id = sa.Column(sa.Integer, primary_key=True)
    events = relationship("Event", back_populates="metaevent")

class Event(Base):
    __tablename__ = "event"

    id = sa.Column(sa.Integer, primary_key=True)

    metaevent_id = sa.Column(sa.Integer, sa.ForeignKey("metaevent.id"))
    metaevent = relationship("MetaEvent", back_populates="event")

    frame_id = sa.Column(sa.Integer, sa.ForeignKey("frame.id"))
    frame = relationship("Frame", back_populates="event")

    eventtime = relationship("EventTime", back_populates="Event")

    line = relationship("Line", uselist=False, back_populates="event")

class EventTime(Base):
    __tablename__ = "eventtime"

    id = sa.Column(sa.Integer, primary_key=True)

    event_id = sa.Column(sa.Integer, sa.ForeignKey("event.id"))
    event = relationship("Event", back_populates="eventtime")


class Frame(Base):
    __tablename__ = "frame"

    id = sa.Column(sa.Integer, primary_key=True)
    event = relationship("Event", back_populates="frame")

class Line(Base):
    __tablename__ = "line"

    id = sa.Column(sa.Integer, primary_key=True)

    event_id = sa.Column(sa.Integer, sa.ForeignKey("events.id"))
    event = relationship("Event", back_populates="line")







def parse(data):
    #some file reading and whatnot
    return {"tai":1, "run":1, "camcol":1, "filter":'i', "field":1,
            "x1":1, "y1":1, "x2":2, "y2":2}


