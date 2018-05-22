import sqlalchemy as sa
from sqlalchemy.orm import relationship, sessionmaker
from .base import Base
import os

frame_frametimes_t = sa.Table(
    "frame_frametimes", Base.metadata,
    sa.Column('frame_id', sa.Integer, sa.ForeignKey('frames.id'), nullable=False),
    sa.Column('frametime_id', sa.Integer, sa.ForeignKey('frametimes.id'), nullable=False),
)

class FrameTime(Base):
    __tablename__ = "frametimes"
    id = sa.Column(sa.Integer, primary_key=True)

    tai = sa.Column(sa.Float())
    mjd = sa.Column(sa.Float())

    frames = relationship('Frame', secondary=frame_frametimes_t, back_populates="frametimes")

    def __init__(self, t, t_format="tai"):
        self.t = BasicTime(t, t_format)
        self.tai = t.tai
        self.mjd = t.mjd

class Frame(Base):
    __tablename__ = "frames"
    id = sa.Column(sa.Integer, primary_key=True)

    run = sa.Column(sa.Integer)
    camcol = sa.Column(sa.Integer)
    filter = sa.Column(sa.String)
    field = sa.Column(sa.Integer)

    crpix1 = sa.Column(sa.Float)
    crpix2 = sa.Column(sa.Float)

    crval1 = sa.Column(sa.Float)
    crval2 = sa.Column(sa.Float)

    cd11 = sa.Column(sa.Float)
    cd12 = sa.Column(sa.Float)
    cd21 = sa.Column(sa.Float)
    cd22 = sa.Column(sa.Float)


    lines = relationship("Line", back_populates="frame")
    frametimes = relationship("FrameTime", secondary=frame_frametimes_t, back_populates='frames')

    def __init__(self, run, camcol, filter, field, crpix1, crpix2,
                 crval1, crval2, cd11, cd12, cd21, cd22):
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
