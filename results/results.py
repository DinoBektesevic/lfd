from .line import Line
from .base import Base
from .frame import Frame
from .linetimes import LineTime
from .point import Point

import os

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, column_property

if os.path.isfile("foo1.db"):
    os.remove("foo1.db")

engine = sa.create_engine('sqlite:///foo1.db', echo=False)
Base.metadata.create_all(engine)

session = sessionmaker()
session.configure(bind=engine)



def parseString(string):
    s = string.split(" ")

    parsed = dict()
    parsed["run"]   = int(s[0])
    parsed["camcol"]= int(s[1]) #parsed["camcol"]= s[2]
    parsed["filter"]= str(s[2]) #parsed["filter"]= s[3]
    parsed["field"] = int(s[3]) #parsed["field"] = s[1]
#    if float(s[4]) == 0:
#        parsed["tai"]   = float(s[5])
#    else:
    parsed["tai"] = float(s[4])
    parsed["crpix1"]= float(s[5])
    parsed["crpix2"]= float(s[6])
    parsed["crval1"]= float(s[7])
    parsed["crval2"]= float(s[8])
    parsed["cd11"] = float(s[9])
    parsed["cd12"] = float(s[10])
    parsed["cd21"] = float(s[11])
    parsed["cd22"] = float(s[12])
    parsed["x1"]    = float(s[13])
    parsed["y1"]    = float(s[14])
    parsed["x2"]    = float(s[15])
    parsed["y2"]    = float(s[16])
    return parsed





class Result(object):
    def __init__(self, tuples):
        frame, line, linetime = tuples
        self.f = frame

        self.l = line
        setattr(self.l, "p1", Point(self.l._fx1, self.l._fy1, self.f.camcol,
                                    self.f.filter))
        setattr(self.l, "p2", Point(self.l._fx2, self.l._fy2, self.f.camcol,
                                    self.f.filter))
        setattr(self.l, "coordsys", "frame")

        self.lt = linetime

    def __getattr__(self, attr):
        try:
            return getattr(self.f, attr)
        except:
            pass
        try:
            return getattr(self.l, attr)
        except:
            pass
        return getattr(self.lt, attr)



#join_on_all = sa.join(Frame, Line, LineTime)
#class Result2(Base):
#    __table__ = join_on_all

#    id = column_property(Frame.id, Line.id)
#    line_id = Line.id




class Results(object):

    def __init__(self, res=None, alex=False):
        pass
        #self.initResults(res)

    @classmethod
    def fromFile(cls, path):

        Session = session()

        f = []
        t = []

#        File = open(path)
        with open(path) as File:
            for line in File.readlines():
                tmp = parseString(line)
                f.append(Frame(tmp["run"], tmp["camcol"], tmp["filter"],
                               tmp["field"], tmp["crpix1"], tmp["crpix2"],
                               tmp["crval1"], tmp["crval2"], tmp["cd11"],
                               tmp["cd12"], tmp["cd21"], tmp["cd22"])
                )
                t.append(LineTime(tmp["tai"], tmp["tai"]))


        Session.add_all(f)
        Session.add_all(t)
        Session.commit()

        lines = []
        i = 0
        with open(path) as File:
            for line in File.readlines():
                tmp = parseString(line)
                lines.append(Line.fromCoords(tmp["x1"], tmp["y1"], tmp["x2"],
                                             tmp["y2"], tmp["camcol"],
                                             tmp["filter"], frame_id=f[i].id,
                                             linetime_id=t[i].id))
                i += 1


        Session.add_all(lines)
        Session.commit()
        Session.close()

        return cls()


    @classmethod
    def fromExistingDB(cls, path):
        global engine
        global session
        print path

        if os.path.isfile("foo1.db"):
            os.remove("foo1.db")

        if os.path.isfile(path):
            engine = sa.create_engine('sqlite:///foo1.db', echo=False)
            Base.metadata.create_all(engine)

            session = sessionmaker()
            session.configure(bind=engine)
            return cls()
        else:
            raise ValueError("Path is not a file.")


    def __parseString(self, string):
        s = string.split(" ")

        parsed = dict()
        parsed["run"]   = int(s[0])
        parsed["camcol"]= int(s[1]) #parsed["camcol"]= s[2]
        parsed["filter"]= str(s[2]) #parsed["filter"]= s[3]
        parsed["field"] = int(s[3]) #parsed["field"] = s[1]
        parsed["tai"] = float(s[4])
        parsed["crpix1"]= float(s[5])
        parsed["crpix2"]= float(s[6])
        parsed["crval1"]= float(s[7])
        parsed["crval2"]= float(s[8])
        parsed["cd11"] = float(s[9])
        parsed["cd12"] = float(s[10])
        parsed["cd21"] = float(s[11])
        parsed["cd22"] = float(s[12])
        parsed["x1"]    = float(s[13])
        parsed["y1"]    = float(s[14])
        parsed["x2"]    = float(s[15])
        parsed["y2"]    = float(s[16])
        return parsed


    def get(self, columns=None, **values):
        Session  = session()
        if columns is None:
            query = Session.query(Frame, Line, LineTime).join(Line).join(LineTime)
        else:
            attrs = [getattr(Result, x) for x in columns]
            query = Session.query(*attrs)
        execute = query.filter_by(**values)
        return map(Result, execute.all())
