from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///:memory:', echo=False)
Base = declarative_base()

from .event import *
from .frame import *
from .point import *
from .basictime import *
from .ccd_dimensions import *
from .coord_conversion import *

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

del create_engine
del sessionmaker
del declarative_base
