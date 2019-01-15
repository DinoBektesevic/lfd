"""
In interactive use it is not very likely detecttrails will output unmanageable
quantities of results. However, it LFD was designed to be able to reprocess the
entire SDSS database of images in which case the size of the results can become
hard to handle if left in its original CSV output format.

Main purpose of results package is to allow collating the default outputs and
easy interactive inspection of the results. 

It is written using SQLAlchemy, a Python SQL toolkit and a ORM. Because of this
before beginning to work with the module it is neccessary to create, or connect
to, a database. See `connect2db` function from this module or the `setup_db`
from lfd library root on how to do that.

Results module is more than just a ORM interface to a DB. It is aware of the
complex SDSS camera array geometry and capable of translating raw result
on-image coordinates to on-ccdarray coordinates without loss of consistency of
the data, it provides wrappers between the modified SDSS MJD and other time
formats as well as various results-colating, table-printing and database
utilities.
"""
import os
#from contextlib import contextmanager

from sqlalchemy.ext.declarative import declarative_base as _declarative_base
from sqlalchemy.orm import sessionmaker as _sessionmaker
from sqlalchemy import create_engine as _create_engine
import sqlalchemy

__query_aliases = {
    "Event" : "events",
    "event" : "events",
    "Frame" : "frames",
    "frame" : "frames",
    "x1"    : "_x1"   ,
    "y1"    : "_y1"   ,
    "x2"    : "_x2"   ,
    "y2"    : "_y2"   ,
    "cx1"   : "_cx1"  ,
    "cy1"   : "_cy1"  ,
    "cx2"   : "_cx2"  ,
    "cy2"   : "_cy2"
}

Base = _declarative_base()

from lfd.results.event import *
from lfd.results.frame import *
from lfd.results.point import *

from lfd.results.basictime import *
from lfd.results.ccd_dimensions import *
from lfd.results.coord_conversion import *

Session, engine = None, None
def connect2db(uri, echo=False):
    """Connects to an existing DB or creates a new empty DB to connect too.
    The DB has to be mappable by the results package.

    Parameters
    ----------
    URI : an URI used to connect to a DB. By default set to:
        'sqlite:///$USER_HOME/foo.db'.
    name : the name of the existing, or newly created, DB. Default: 'foo.db'
    echo : verbosity of the DB. False by default.

    """
    global Session, engine

    # create the engine that hooks to an existing or creates a new DB
    engine  = _create_engine(uri, echo=echo)
    if uri[:5] == "sqlite":
        engine.execute("PRAGMA FOREIGN_KEYS=ON")

    # map to existing or create new tables in the DB
    Base.metadata.create_all(engine)

    # create a Session object so transactions can be made
    Session = _sessionmaker(bind=engine)

from lfd.results.utils import *

del event, frame, point, basictime
del ccd_dimensions, coord_conversion
