from contextlib import contextmanager

__all__ = ["from_file", "create_test_sample", "session_scope"]

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


def parse_result(string):
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
    from . import Frame, Event, BasicTime, LineTime, Session
    session = Session()

    tmp, frames, events = [], [], []
    with open(path) as File:
        for line in File.readlines():
            r = parse_result(line)
            tmp.append(r)
            frames.append(Frame(r["run"],    r["camcol"], r["filter"], r["field"],
                                r["crpix1"], r["crpix2"], r["crval1"], r["crval2"],
                                r["cd11"],   r["cd12"],   r["cd21"],   r["cd22"],
                                r["tai"]))

    session.add_all(frames)
    session.commit()

    i = 0
    for r in tmp:
        events.append(Event(r["x1"], r["y1"], r["x2"], r["y2"], frame=frames[i]))
        i+=1

    session.add_all(events)
    session.commit()
    session.close()



def create_test_sample():
    from . import Frame, Event, BasicTime, LineTime, Session
    session = Session()


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
#    session.add_all(tmp)
#    session.commit()

    #################################################
    tmp2 = list()
    tmp2.append(Event(x1=1, y1=1, x2=2, y2=2, frame=tmp[0]))
    tmp2.append(Event(x1=2, y1=2, x2=3, y2=3, frame=tmp[1]))
    tmp2.append(Event(x1=3, y1=3, x2=4, y2=4, frame=tmp[2]))
    tmp2.append(Event(x1=4, y1=4, x2=5, y2=5, frame=tmp[1]))



    ########################################

    # Add frames
    session.add_all(tmp2)
    session.commit()
    session.close()
