from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///:memory:', echo=False)
Base = declarative_base()

from .event import Event
from .frame import Frame

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

del create_engine
del sessionmaker
del declarative_base
