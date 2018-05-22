from .point import Point
from .linetimes import LineTime
from .base import Base

from coord_conversion import get_filter_from_int
import ccd_dimensions as ccd

import sqlalchemy as sa
from sqlalchemy.orm import relationship, reconstructor
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method

class Line(Base):
    __tablename__ = "lines"

    id = sa.Column(sa.Integer, primary_key=True)

    frame_id = sa.Column(sa.Integer, sa.ForeignKey('frames.id'),
                         nullable=False)
    linetime_id = sa.Column(sa.Integer, sa.ForeignKey('linetimes.id'),
                            nullable=False)

    _fx1 = sa.Column(sa.Float)
    _fy1 = sa.Column(sa.Float)
    _fx2 = sa.Column(sa.Float)
    _fy2 = sa.Column(sa.Float)

    _cx1 = sa.Column(sa.Float)
    _cy1 = sa.Column(sa.Float)
    _cx2 = sa.Column(sa.Float)
    _cy2 = sa.Column(sa.Float)

    _fa = sa.Column(sa.Float)
    _fb = sa.Column(sa.Float)
    _fc = sa.Column(sa.Float)

    _ca = sa.Column(sa.Float)
    _cb = sa.Column(sa.Float)
    _cc = sa.Column(sa.Float)

    frame = relationship('Frame', back_populates='lines')
    linetimes = relationship('LineTime', back_populates="lines")

    def __init__(self, p1, p2, frame_id, linetime_id, coordsys="frame"):

        self.coordsys = coordsys.lower()
        p1.useCoordsys(coordsys)
        p2.useCoordsys(coordsys)

        self.p1 = p1
        self.p2 = p2

        self._initCoordinates()           

        self.frame_id = frame_id
        self.linetime_id = linetime_id


    @classmethod
    def fromCoords(cls, x1, y1, x2, y2, camcol, filter,
                   frame_id, linetime_id, coordsys="frame"):

        #y1 = 2*float(y1) - float(y2)

        p1 = Point(x1, y1, camcol, filter, coordsys=coordsys)
        p2 = Point(x2, y2, camcol, filter, coordsys=coordsys)

        return cls(p1, p2, frame_id, linetime_id, coordsys)

    @classmethod
    def fromIterableCoords(cls, p1, p2, camcol, filter, frame_id,
                           linetime_id, coordsys="frame"):

        t1 = Point(p1[0], p1[1], camcol, filter, coordsys=coordsys)
        t2 = Point(p2[0], p2[1], camcol, filter, coordsys=coordsys)

        return cls(t1, t2, frame_id, linetime_id, coordsys)

    def _initCoordinates(self):
        self.__initFrameCoordinates()
        self.__initCCDCoordinates()

        if self.a == 0:
            self.calcy = self.__horizontal_calcy
            self.calcx = self.__horizontal_calcx
        elif self.b == 0:
            self.calcy = self.__vertical_calcy
            self.calcx = self.__vertical_calcx
        else:
            self.calcy = self.__general_calcy
            self.calcx = self.__general_calcx

    def __initFrameCoordinates(self):
        p1 = self.p1
        p2 = self.p2
        self._fx1 = p1._fx
        self._fy1 = p1._fy
        self._fx2 = p2._fx
        self._fy2 = p2._fy

        self._fa = (p1._fy - p2._fy)
        self._fb = (p2._fx - p1._fx)
        self._fc = (p1._fx * p2._fy) - (p2._fx * p1._fy)


    def __initCCDCoordinates(self):
        p1 = self.p1
        p2 = self.p2
        self._cx1 = p1._cx
        self._cy1 = p1._cy
        self._cx2 = p2._cx
        self._cy2 = p2._cy

        self._ca = (p1._cy - p2._cy)
        self._cb = (p2._cx - p1._cx)
        self._cc = (p1._cx * p2._cy) - (p2._cx * p1._cy)

        
    @property
    def x1(self):
        return self.p1.x
        
    @x1.setter
    def x1(self, value):
        self.p1.x = value
        self._initCoordinates()
        
    @property
    def y1(self):
        return self.p1.y

    @y1.setter
    def y1(self, value):
        self.p1.y = value
        self._initCoordinates()
        
    @property
    def x2(self):
        return self.p2.x

    @x2.setter
    def x2(self, value):
        self.p2.x = value
        self._initCoordinates()

    @property
    def y2(self):
        return self.p2.y

    @y2.setter
    def y2(self, value):
        self.p2.y = value
        self._initCoordinates()

    def move(self, *args, **kwargs):
        if len(args) == 4:
            x1, y1, x2, y2 = args
        elif len(args) == 2:
            x1, y1 = args[0]
            x2, y2 = args[1]
        else:
            x1, y1 = kwargs["x1"], kwargs["y1"]
            x2, y2 = kwargs["x2"], kwargs["y2"]

        self.p1.move(x1, y1)
        self.p2.move(x2, y2)
        self._initCoordinates()
        
    @property
    def a(self):
        if self.coordsys == "frame":
            return self._fa
        elif self.coordsys == "ccd":
            return self._ca
        else:
            raise ValueError("Unrecognized coordinate system: " +
                             self.coordsys)
    @property
    def b(self):
        if self.coordsys == "frame":
            return self._fb
        elif self.coordsys == "ccd":
            return self._cb
        else:
            raise ValueError("Unrecognized coordinate system: " +
                             self.coordsys)

    @property
    def c(self):
        if self.coordsys == "frame":
            return self._fc
        elif self.coordsys == "ccd":
            return self._cc
        else:
            raise ValueError("Unrecognized coordinate system: " +
                             self.coordsys)

    def __call__(self, x):
        return self.calcy(x)
            
    def calcy(self, x):
        pass

    def __general_calcy(self, x):
        try:
            return -self.a/self.b * x - self.c/self.b 
        except TypeError:
            pass

        #to avoid evaluating self.m and self.b in every self.gety
        #call in a loop scenario we make local copies of variables
        #in case of an iterable input and map the function to the
        #iterable for a 10x speedup. --> from 25sec for 10mil points
        #to 2.5 sec for 10mil points.
        #Because we don't know the coordsys we make copies from properties
        try:
            a = self.a
            b = self.b
            c = self.c
            fast_calcy = lambda x: -a/b * x - c/b
            return map(fast_calcy, x)
        except TypeError:
            pass

    def __horizontal_calcy(self, x):
        try:
            y_intercept = -self.c/self.b
            return [y_intercept]*len(x)
        except TypeError:
            pass
            
        return -self.c/self.b

    def __vertical_calcy(self, x):
        raise ZeroDivisionError("Vertical lines have undefined y intercept.")
        

    def calcx(self, y):
        pass
        
    def __general_calcx(self, y):
        try:
            return -self.b/self.a * y - self.c/self.a
        except TypeError:
            pass
            
        try:
            a = self.a
            b = self.b
            c = self.c
            fast_calcx = lambda y: -b/a * y - c/a
            return map(fast_calcx, y)
        except TypeError:
            pass

    def __horizontal_calcx(self, y):
        raise ZeroDivisionError("Horizontal lines have undefined x intercept.")

    def __vertical_calcx(self, y):
        try:
            y_intercept = -self.c/self.a
            return [y_intercept]*len(y)
        except TypeError:
            pass

        return -self.c/self.a
            

    def useCoordsys(self, coordsys):
        if coordsys.lower() in ["frame", "ccd"]:
            self.coordsys = coordsys.lower()
            self.p1.useCoordsys(coordsys.lower())
            self.p2.useCoordsys(coordsys.lower())
        else:
            raise ValueError("Unrecognized Coordinate System: " +
                             self.coordsys)

    def findEdges(self):
        currentsys = self.coordsys
        self.useCoordsys("ccd")

        maxw = ccd.MAX_W_CCDARRAY
        maxh = ccd.MAX_H_CCDARRAY
        
        test = ""
        res = {"x": [], "y": []}
        
        y0 = self.calcy(0)
        ymax = self.calcy(maxw)
        
        x0 = self.calcx(0)
        xmax = self.calcx(maxh)

        if x0 > 0 and x0 < maxw:
            test = "top"
            res["x"].append(x0)
        else:
            res["x"].append(0)

        if xmax > 0 and xmax < maxw:
            test += " bot"
            res["x"].append(xmax)
        else:
            res["x"].append(maxw)
            
        if y0 > 0 and y0 < maxh:
            test += " left"
            res["y"].append(y0)
        else:
            res["y"].append(0)
            
        if ymax > 0 and ymax < maxh:
            test += " right"
            res["y"].append(ymax)
        else:
            res["y"].append(maxh)

        self.useCoordsys(currentsys)
        #print test
        
        return res


    def getCCDChips(self, step=1000):
        currentsys = self.coordsys
        self.useCoordsys("ccd")

        w_camcol = ccd.W_CAMCOL
        w_camcol_spacing = ccd.W_CAMCOL_SPACING
        
        h_filter = ccd.H_FILTER
        h_filter_spacing = ccd.H_FILTER_SPACING
        
        crossed = {1:[], 2:[], 3:[], 4:[], 5:[]}

        ranges = self.findEdges()
        if ranges["x"][0] > ranges["x"][1]:
            start = ranges["x"][1]
            stop = ranges["x"][0]
        else:
            start = ranges["x"][0]
            stop = ranges["x"][1]


        step = (stop-start)/float(step)
        
        x = range(start, stop, step)
        y = self.calcy(x)
                
        index = 0
        for xi in x:            
            for i in range(1, 7):
                left =  xi - (i-1) * (w_camcol + w_camcol_spacing)
                right = xi - (i-1) * (w_camcol + w_camcol_spacing) - w_camcol
                
                if (left >= 0 and left <= w_camcol and
                    right<= 0 and right >= -w_camcol):
                    
                    yi = y[index]
                    for j in range(1, 6):
                        top = yi - (j-1) * (h_filter + h_filter_spacing)
                        bot = yi - (j-1) * (h_filter + h_filter_spacing) - h_filter

                        if (top >= 0 and top <= h_filter and
                            bot <= 0 and bot >= -h_filter):
                            crossed[i].append(get_filter_from_int(j))
            index += 1

        self.useCoordsys(currentsys)
        for a in crossed:
            crossed[a] = set(crossed[a])
        return crossed
