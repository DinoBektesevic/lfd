"""Contains various utilities that expand and suplement the results module
functionality and make it easier to work with.
"""

from contextlib import contextmanager
import sqlalchemy

__all__ = ["from_file", "create_test_sample", "session_scope", "pprint",
           "deep_expunge", "deep_expunge_all"]


def deep_expunge(item, session):
    """For a given item, expunges all first order sql relationships from given
    session.

    Parameters
    ----------
    item : object
      any OO mapped sqlalchemy ORM object to be expunged completely (Event,
      Frame etc..)
    session : sql.Session()
      active session from which we want to expunge the item from

    """
    insp = sqlalchemy.inspect(item)
    relationships = insp.mapper.relationships.keys()
    for relative in relationships:
        session.expunge(getattr(item, relative))
    session.expunge(item)

def deep_expunge_all(items, session):
    """For a given list of items, expunges all first order sql
    relationships from given session.

    Parameters
    ----------
    items : list(object) or tuple(object)
      set of OO mapped sqlalchemy ORM object to be expunged completely (Event,
      Frame etc..)
    session : sql.Session()
      active session from which we want to expunge the items from

    """
    for item in items:
        deep_expunge(item, session)

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    from . import Session

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


def create_test_sample():
    """Creates a test sample of mock Events for testing, demonstration and
    learning purposes.

    """
    from . import Frame, Event, BasicTime, LineTime

    # First we create the Frames we want so that we can link them to Events.
    tmp = list()
    tmp.append(Frame(run=1, camcol=3, filter='i', field=1, crpix1=1, crpix2=1,
                     crval1=1, crval2=1, cd11=1, cd12=1, cd21=1, cd22=1,
                     t=4412911074.78)
    )
    tmp.append(Frame(run=1, camcol=5, filter='r', field=1, crpix1=1, crpix2=1,
                     crval1=1, crval2=1, cd11=1, cd12=1, cd21=1, cd22=1,
                     t=4412911084.78)
    )
    tmp.append(Frame(run=3, camcol=4, filter='i', field=1, crpix1=1, crpix2=1,
                     crval1=1, crval2=1, cd11=1, cd12=1, cd21=1, cd22=1,
                     t=4412911074.78)
    )


    # Then we create Events, link them with created frames
    tmp2 = list()
    tmp2.append(Event(x1=1, y1=1, x2=2, y2=2, frame=tmp[0]))
    tmp2.append(Event(x1=2, y1=2, x2=3, y2=3, frame=tmp[1]))
    tmp2.append(Event(x1=3, y1=3, x2=4, y2=4, frame=tmp[2]))
    tmp2.append(Event(x1=4, y1=4, x2=5, y2=5, frame=tmp[1]))


    # Only at the end when we are completely done do we make a transaction to
    # the DB. It is enough to add only the second list (of events) as the
    # cascade relationship to frames will make sure they are persisted too.
    with session_scope() as session:
        session.add_all(tmp2)
        session.commit()


def __pprintEvents(events, short=True, digits=2):
    """Prints a list of events as a string in a table-like format.
    The default layout when short is True is given by:
        run camcol filter field time x1 y1 x2 y2
    if short is false, the long table format is printed:
        run camcol filter field time x1 y1 x2 y2 cx1 cy1 cx2 cy2

    The param 'digits' selects the number of significant digits the coordinates
    are rounded to. Set to 2 by default.
    """
    headerf = ("{0:<4}{1:<7}{2:<7}{3:<5}{4:>12}{5:>17}{6:>10}{7:>8}{8:>8}"
               "{9:>5}{10:>5}{11:>5}{12:>5}")
    rowf = ("{0:<6}{1:<3}{2:>6}{3:>7}{4:>25}{5:>9.{d}f}{6:>9.{d}f}{7:>9.{d}f}"
            "{8:>9.{d}f}{9:>10.{d}f}{10:>10.{d}f}{11:>10.{d}f}{12:>10.{d}f}")
    if short:
        headerf = headerf[:-27]
        rowf = rowf[:-51]

    header = headerf.format("run", "camcol", "filter", "field", "time",
                            "x1", "y1", "x2", "y2", "cx1", "cy1", "cx2", "cy2")

    print(header)
    for e in events:
        print(rowf.format(e.run, e.camcol, e.filter, e.field, e.frame.t.iso,
                         e.x1, e.y1, e.x2, e.y2, e.cx1, e.cy1, e.cx2, e.cy2,
                         d=digits))

def __pprintFrames(frames):
    headerf = ("{0:<4}{1:<7}{2:<7}{3:<5}{4:>12}")
    header = headerf.format("run", "camcol", "filter", "field", "time")
    print(header)

    rowf = ("{0:<6}{1:<3}{2:>6}{3:>7}{4:>25}")
    for f in frames:
        print(rowf.format(f.run, f.camcol, f.filter, f.field, f.t.iso))

def pprint(objlist, *args, **kwargs):
    """Pretty-prints a list of Frame or Event objects in a table-like format.

    Parameters
    ----------
    short : bool
      True by default. The shortened format corresponds to::

        run camcol filter field time x1 y1 x2 y2

      if short is false, the long table format is printed::

        run camcol filter field time x1 y1 x2 y2 cx1 cy1 cx2 cy2

    digits : int
      2 by default. Controls the number of printed significant digits,
    """
    if not isinstance(objlist, list):
        raise ValueError("Can only pretty-print lists of Events and Frames.")

    from lfd.results import Frame, Event
    if isinstance(objlist[0], Event):
        __pprintEvents(objlist, *args, **kwargs)
    elif isinstance(objlist[0], Frame):
        __pprintFrames(objlist, *args, **kwargs)
    else:
        raise ValueError(("Type not recognized. Expected Frame or Event, got "
                          "{} instead").format(type(objlist[0])))


def parse_result_row(string):
    """Parse a single row of a space separated CSV file formatted to the output
    standard of detecttrails package (see detecttrails package for details) and
    returns a dictionary with the column names as keys.

    """
    s = string.split(" ")

    parsed = dict()
    parsed["run"]   = int(s[0])
    parsed["camcol"]= int(s[1])
    parsed["filter"]= str(s[2])
    parsed["field"] = int(s[3])
    parsed["tai"]   = float(s[4])
    parsed["crpix1"]= float(s[5])
    parsed["crpix2"]= float(s[6])
    parsed["crval1"]= float(s[7])
    parsed["crval2"]= float(s[8])
    parsed["cd11"]  = float(s[9])
    parsed["cd12"]  = float(s[10])
    parsed["cd21"]  = float(s[11])
    parsed["cd22"]  = float(s[12])
    parsed["x1"]    = float(s[13])
    parsed["y1"]    = float(s[14])
    parsed["x2"]    = float(s[15])
    parsed["y2"]    = float(s[16])
    return parsed


def from_file(path):
    """Read a detecttrails formatted CSV file into a database."""
    from . import Frame, Event, BasicTime, LineTime

    frames, events = [], []
    with open(path) as File:
        for line in File.readlines():
            r = parse_result_row(line)
            frames.append(Frame(r["run"],    r["camcol"], r["filter"], r["field"],
                                r["crpix1"], r["crpix2"], r["crval1"], r["crval2"],
                                r["cd11"],   r["cd12"],   r["cd21"],   r["cd22"],
                                r["tai"]))
            events.append(Event(frames[-1], r["x1"], r["y1"], r["x2"], r["y2"]))

    with session_scope() as session:
        session.add_all(events)
        session.commit()



