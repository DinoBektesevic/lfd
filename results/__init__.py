from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
#:memory:
engine = create_engine('sqlite:////home/dino/Desktop/foo.db', echo=True)
engine.execute('pragma foreign_keys=on')
Base = declarative_base()

from .event import *
from .frame import *
from .point import *

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

from .basictime import *
from .ccd_dimensions import *
from .coord_conversion import *
from .result import *
