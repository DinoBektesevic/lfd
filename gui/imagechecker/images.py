import os
from results import Results
from gui.utils import expandpath
from detecttrails.sdss import files

class Images(object):
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
