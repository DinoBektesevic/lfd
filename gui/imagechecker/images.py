import os

import lfd.results as res
from lfd.gui.utils import expandpath
#from lfd.detecttrails.sdss import files

from PIL import Image, ImageTk

class Images:
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
            self.current = self.events.index(eventid)
        elif (self.current is not None and
              self.current > -1 and
              self.current < self.maxindex):
            eventid = self.events[self.current]
        else:
            raise IndexError(("Events index out of range! Expected [0, {}], "
                              "got {}").format(self.maxindex, self.current))
        imgpath = self.eventId2Filename(eventid)
        if imgpath is None:
            self.image = None
        else:
            self.image = Image.open(imgpath)

    def loadEvent(self, eventid=None):
        if eventid is not None:
            self.current = self.events.index(eventid)
        elif (self.current is not None and
              self.current > -1 and
              self.current < self.maxindex):
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
        self.loadEvent()

    def getPrevious(self):
        if self.current == None:
            self.current = None
        elif self.current == -1:
            self.current = -1
        else: # self.current > 0:
            self.current -= 1
        self.loadEvent()

    def commit():
        with res.session_scope() as session:
            session.add(self.event)
            session.commit()



class Images2(object):
    def __init__(self, parent, respath=None, imgpath=None):
        self.current = None
        self.maxindex = None
        self.results = None
        self.keys = None
        self.images = None
        self.parent = parent
        self.cache = []

        self.setResults(respath)
        self.setImages(imgpath)

    def setResults(self, respath):
        tmppath = expandpath(respath)
        if tmppath[0]:
            self.results = Results(tmppath[1])
            self.keys = self.results.keys

    def setImages(self, imgpath):
        tmppath = expandpath(imgpath)
        if tmppath[0]:
            images = self._getImages(tmppath[1])
            if len(images) > 0:
                self.images = images
                self.current = 0
                self.maxindex = len(images)


    def _getImages(self, imgpath):
        images = []
        self.cache = []
        for (dirpath, dirnames, filenames) in os.walk(imgpath):
            for filename in filenames:
                if os.path.splitext(filename)[1] == ".png":
                    images.append(os.path.join(dirpath, filename))
                    self.cache.append(filename)
        return images


    def getImageData(self):
        if self.current not in [-1, self.maxindex]:
            frame = self.results.getFrameFromImgPath(self.images[self.current])
            imgdata = self.results.get(**frame)
            if len(imgdata) == 1:
                imgdata = imgdata[0]
            elif len(imgdata) == 0: #DB doesn't contain requested row
                imgdata = None
            else:
                raise ValueError("Multiple Result objects returned."+
                             "Please specify unique Frame identifiers")
        else:
            return None

        return imgdata

    def updateImageData(self, what):
        frame = self.results.getFrameFromImgPath(
            self.images[self.current])
        try:
            self.results.update(what, **frame)
        except:
            pass

    def find(self, run, camcol, filter, field):
        filename = files.filename("frame", run=run, camcol=camcol,
                                  filter=filter, field=field)
        filename = filename.split("/")[-1]
        filename += ".png"
        try:
            index = self.cache.index(filename)
        except ValueError:
            index = None
        return index

    def skip(self, index=None, run=None, camcol=None, filter=None,
             field=None):
        if index is None and None not in (run, camcol, filter, field):
            index = self.find(run, camcol, filter, field)

        if index is None:
            raise ValueError("Send valid run, camcol, filter"+
                             " and field to find desired frame.")
        if index < self.maxindex:
            self.current = index
        else:
            raise IndexError("Index out of range.")
        self.parent.update()

    def getImage(self):
        if self.images is not None and self.current not in [-1, self.maxindex]:
            return self.images[self.current]
        return None

    def getNext(self):
        if self.current == None:
            self.current = None
        elif self.current == self.maxindex:
            self.current = self.maxindex
        else: # self.current < self.maxindex:
            self.current += 1

    def getPrevious(self):
        if self.current == None:
            self.current = None
        elif self.current == -1:
            self.current = -1
        else: # self.current > 0:
            self.current -= 1
