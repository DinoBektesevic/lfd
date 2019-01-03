from contextlib import contextmanager
from os import path

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import sqlalchemy as sql

Base = declarative_base()

class Image(Base):
    """Provides an ORM map to the images table.

      Attributes
    ----------------
    id      - autoincremented unique id of the row
    run     - run id (Integer, composite PrimaryKey)
    camcol  - camcol id (Integer, composite PrimaryKey)
    filter  - filter id (Char, composite PrimaryKey)
    field   - field id (Integer, composite PrimaryKey)
    imgpath - path to the image corresponding to the frame identifiers
    """
    __tablename__ = "images"
    run    = sql.Column(sql.Integer)
    camcol = sql.Column(sql.Integer)
    filter = sql.Column(sql.String(length=1))
    field  = sql.Column(sql.Integer)

    id     = sql.Column(sql.Integer, primary_key=True, autoincrement=True)
    imgpath = sql.Column(sql.String, nullable=False)

    def __init__(self, run, camcol, filter, field, path):
        self.run = run
        self.camcol = camcol
        self.filter = filter
        self.field = field
        self.imgpath = path


def connect2db(uri="sqlite:///"+path.join(path.expanduser("~"), "Desktop/foo.db"),
               echo=False):
    """Connects to an existing DB or creates a new empty DB to connect too.
    The DB has to be mappable by the results package.

      Parameters
    --------------
    URI : an URI used to connect to a DB. By default set to:
        'sqlite:///$USER_HOME/foo.db'.
    name : the name of the existing, or newly created, DB. Default: 'foo.db'
    echo : verbosity of the DB. False by default.
    """
    global Session, engine

    # create the engine that hooks to an existing or creates a new DB
    engine = create_engine(uri, echo=echo)

    # map to existing or create new tables in the DB
    Base.metadata.create_all(engine)

    # create a Session object so transactions can be made
    Session = sessionmaker(bind=engine)

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    if Session is None:
        raise sqlalchemy.exc.InterfaceError("Not connected to a database," +\
                                            "Session does not exist", 0, 0)
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

Session, engine = None, None
