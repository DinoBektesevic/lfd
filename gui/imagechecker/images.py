import os

import sqlalchemy.orm.exc

import lfd.results as res
from lfd.gui.utils import expandpath
#from lfd.detecttrails.sdss import files

from PIL import Image, ImageTk

class Data:
    def __init__(self, parent, respath=None, imgpath=None):
        self.dbtype = "sqlite:///"
        self.imgtype = "png"
        self.keys = res.Frame.__table__.columns.keys()
        self.parent = parent

        self.events = [None]
        self.current = None
        self.maxindex = len(self.events)
        self.event = None

        self.image = None
        self.imgdir = None

        if respath is not None:
            self.initResults(respath)
        if imgpath is not None:
            self.initImages(imgpath)

    def initEvents(self, respath):
        if os.path.exists(respath):
            self.respath = respath
        else:
            raise OSError(("Directory is empty or does not exists! "
                           "Got {}".format(respath)))

        res.connect2db(uri=self.dbtype+respath)
        with res.session_scope() as session:
            self.events = [id for id, in session.query(res.Event.id)]
        self.maxindex = len(self.events)
        self.current = 0

    def initImages(self, imgpath):
        if os.path.isdir(imgpath) and len(os.listdir(imgpath)) != 0:
            self.imgdir = imgpath
        else:
            raise OSError(("Directory is empty or does not exists! "
                           "Got {}".format(imgpath)))

        if self.current is None:
            for f in os.listdir(self.imgdir):
                if os.path.splitext(f)[-1] == "."+self.imgtype:
                    imgpath = os.path.join(imgpath, f)
                    break

            if imgpath is None:
                raise OSError(("Directory does not contain "
                               "files of type {}").format(self.imgtype))
        self.image = Image.open(imgpath)

    def frameId2Filename(self, run, camcol, filter, field):
        if not all([run, camcol, filter, field]):
            return None
        filename = "frame-{filter}-{run:06d}-{camcol}-{field:04}.fits.{type}"
        filename = filename.format(run=run, camcol=camcol, filter=filter,
                                   field=field, type=self.imgtype)
        return os.path.join(self.imgdir, filename)

    def eventId2FrameId(self, eventid):
        with res.session_scope() as session:
            ev = session.query(res.Event).filter_by(id=eventid).one()
            run, camcol, filter, field = ev.run, ev.camcol, ev.filter, ev.field
        return run, camcol, filter, field

    def eventId2Filename(self, eventid):
        run, camcol, filter, field = self.eventId2FrameId(eventid)
        return self.frameId2Filename(run, camcol, filter, field)

    def loadImage(self, eventid=None):
        if eventid is not None:
            try:
                self.current =  self.events.index(eventid)
            except ValueError:
                raise IndexError("Can't find eventid {}".format(eventid))
        elif self.current is not None:
            eventid = self.events[self.current]
        else:
            raise IndexError(("Events index out of range! Expected [0, {}], "
                              "got {}").format(self.maxindex, self.current))
        imgpath = self.eventId2Filename(eventid)
        if imgpath is None:
            self.image = None
        else:
            try:
                self.image = Image.open(imgpath)
            except FileNotFoundError:
                self.image = None
                raise

    def loadEvent(self, eventid=None):
        if eventid is not None:
            try:
                self.current =  self.events.index(eventid)
            except ValueError:
                raise IndexError("Can't find eventid {}".format(eventid))
        elif self.current is not None:
            eventid = self.events[self.current]
        else:
            raise IndexError(("Events index out of range! Expected [0, {}], "
                              "got {}").format(self.maxindex, self.current))

        with res.session_scope() as session:
            event = session.query(res.Event).filter_by(id=eventid).one()
            session.expunge(event.frame)
            session.expunge(event)
        self.event = event

    def getNext(self):
        if self.current == None:
            self.current = None
        elif self.current == self.maxindex:
            self.current = self.maxindex
        else: # self.current < self.maxindex:
            self.current += 1
#        self.loadEvent()

    def getPrevious(self):
        if self.current == None:
            self.current = None
        elif self.current == 0:
            self.current = 0
        else: # self.current > 0:
            self.current -= 1
#        self.loadEvent()

    def commit(self):
        self.event.verified = True
        with res.session_scope() as session:
            session.add(self.event)
            session.commit()

    def skip(self, run, camcol, filter, field, which=0):
        with res.session_scope() as session:
            query = session.query(res.Event.id).filter(res.Event.run==run,
                                                       res.Event.filter==filter,
                                                       res.Event.camcol==camcol,
                                                       res.Event.field==field)
            eventid = query.all()[which][0]
        self.loadEvent(eventid=eventid)
        self.loadImage(eventid=eventid)

