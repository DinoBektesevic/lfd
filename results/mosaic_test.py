import results as res
import time
from point import Point
from line import Line
from basic_line import BasicLine

class Timer(object):
    def __init__(self, verbose=False):
        self.verbose = verbose

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.end = time.time()
        self.secs = self.end - self.start
        self.msecs = self.secs * 1000  # millisecs
        if self.verbose:
            print 'elapsed time: %f ms' % self.msecs



r = res.Results(respath = "~/Desktop/mosaic_test/results.txt")

first = r.get(camcol=3, field=429, filter="u")[0]

x1 = first.x1
y1 = 2*first.y1 -first.y2
x2 = first.x2
y2 = first.y2
camcol = 3
filter = "u"

print x1, y1, x2, y2, camcol, filter

m = (y2-y1)/(x2-x1)
b = y1-m*x1

################################################################################
##########################    BASIC  TESTS    ##################################
################################################################################

p1 = Point(x1, y1, camcol=2, filter="g")
p2 = Point(x2, y2, camcol=2, filter="g")



l = Line(p1, p2)
print l.getCCDChips()
#l.showLine()

bl = BasicLine(first)
print l.getCCDChips()



################################################################################
##########################    SPEED  TESTS    ##################################
################################################################################
million = range(1000000)
ten_million = range(10000000)
"""
Difference between BasicLine and Line instantiation
1 mil. instantiations
"""
with Timer() as t1:
    for i in million:
#        first = r.get(camcol=3, field=429, filter="u")[0]
#        p1 = Point(x1, y1, camcol=2, filter="g")
#        p2 = Point(x2, y2, camcol=2, filter="g")
        Line(Point(x1, y1, camcol=2, filter="g"),
             Point(x2, y2, camcol=2, filter="g"))

        
with Timer() as t2:
    for i in million:
#        first = r.get(camcol=3, field=429, filter="u")[0]
        BasicLine(first)

print """################################
Difference between BasicLine and Line instantiation
1 mil. calculations
################################"""
print "                     seconds"
print "Line:            ", t1.msecs/1000.
print "BasicLine:       ", t2.msecs/1000.
print "diff:            ", ((t1.msecs-t2.msecs) if (t1.msecs > t2.msecs) else (t2.msecs-t1.msecs))/1000.
print "speedup:         ", t1.msecs/t2.msecs if (t1.msecs > t2.msecs) else t2.msecs/t1.msecs






"""
Difference between BasicLine and Line attribute lookups
1 mil. loops, 4 lookups per loop & 2 CoordSys changes per loop
"""

with Timer() as t1:
    for i in million:
        l.m
        l.b
        l.useCoordsys("ccd")
        l.m
        l.b
        l.useCoordsys("frame")

        
with Timer() as t2:
    for i in million:
        bl.m
        bl.b
        bl.useCoordsys("ccd")
        bl.m
        bl.b
        bl.useCoordsys("frame")


print """\n\n################################
Difference between BasicLine and Line attribute lookup
1 mil. calculations
################################"""
print "                     seconds"
print "Line:            ", t1.msecs/1000.
print "BasicLine:       ", t2.msecs/1000.
print "diff:            ", ((t1.msecs-t2.msecs) if (t1.msecs > t2.msecs) else (t2.msecs-t1.msecs))/1000.
print "speedup:         ", t1.msecs/t2.msecs if (t1.msecs > t2.msecs) else t2.msecs/t1.msecs






"""
Difference between point calculations for collections and individual
x coordinates for Line
10 mil. calculations
"""
with Timer() as t1:
    for i in ten_million:
        l(i)

with Timer() as t2:
    l(ten_million)


print """\n\n################################
Difference between point calculations for collections and individual
x coordinates for Line
10 mil. calculations
###############################"""
print "                     seconds"
print "individual loop: ", t1.msecs/1000.
print "map loop:        ", t2.msecs/1000.
print "diff:            ", ((t1.msecs-t2.msecs) if (t1.msecs > t2.msecs) else (t2.msecs-t1.msecs))/1000.
print "speedup:         ", t1.msecs/t2.msecs if (t1.msecs > t2.msecs) else t2.msecs/t1.msecs






"""
Difference between point calculations for collections and individual
x coordinates for BasicLine
1 mil. calculations
"""
with Timer() as t3:
    for i in ten_million:
        bl(i)

with Timer() as t4:
    bl(ten_million)


print """################################
Difference between point calculations for collections and individual
x coordinates for BasicLine
10 mil. calculations
###############################"""
print "                     seconds"
print "individual loop: ", t3.msecs/1000.
print "map loop:        ", t4.msecs/1000.
print "diff:            ", ((t3.msecs-t4.msecs) if (t3.msecs > t4.msecs) else (t3.msecs-t4.msecs))/1000.
print "speedup:         ", t3.msecs/t4.msecs if (t3.msecs > t4.msecs) else t4.msecs/t3.msecs



print """################################
Difference between point calculations for collections and individual
x coordinates between Line and BasicLine
###############################"""
print "                     seconds"
print "Per diff:        ", (t1.msecs-t3.msecs if (t1.msecs > t3.msecs) else t3.msecs-t1.msecs)/1000.
print "Per speedup:     ", t1.msecs/t3.msecs if (t1.msecs > t3.msecs) else t3.msecs/t1.msecs
print ""
print "Map diff:        ", (t2.msecs-t4.msecs if (t2.msecs > t4.msecs) else t4.msecs-t2.msecs)/1000.
print "Map speedup:     ", t2.msecs/t4.msecs if (t2.msecs > t4.msecs) else t2.msecs/t4.msecs






"""
When Does It Pay Off To Use Collections:
"""
nelements = range(1, 11)
nelements.extend((100, 1000, 10000))

lt = []
for j in nelements:
    with Timer() as t:
        for i in range(j):
            l(i)
    lt.append(t.msecs)

ltc = []
for j in nelements:
    span = range(j)
    with Timer() as t:
        l(span)
    ltc.append(t.msecs)

bt = []
for j in nelements:
    with Timer() as t:
        for i in range(j):
            bl(i)
    bt.append(t.msecs)

btc = []
for j in nelements:
    span = range(j)
    with Timer() as t:
        bl(span)
    btc.append(t.msecs)


print """\n\n################################
When Does It Pay Off To Use Collections for Line and BasicLine:
(Table in miliseconds)
###############################"""
print "{0:^42}|{1:^36}".format("Line", "BasicLine")
print "{0:6}{1:10}{2:10}{3:9}{4:8}|{5:10}{6:10}{7:9}{8:8}".format(
    "N", "Indiv.", "Coll.", "Diff", "Sp.Up",
    "Indiv.", "Coll.", "Diff", "Sp.Up")
for n, i, lc, j, bc in zip(nelements, lt, ltc, bt, btc):
   print "{0:<6}{1:<10.5}{2:<10.5}{3:<9.3}{4:<8.5}|{5:<10.5}{6:<10.5}{7:<9.3}{8:<8.5}".format(
       n, i, lc, i-lc if (i > lc) else lc-i, i/lc if (i > lc) else lc/i,
       j, bc, j-bc if (j > bc) else bc-j, j/bc if (j > bc) else bc/j)






"""
Times and differences for __call__ calculations over gety
10 mil. calculations, in seconds
"""
with Timer() as t1:
    for i in ten_million:
        l(i)

with Timer() as t2:
    for i in ten_million:
        bl(i)

with Timer() as t3:
    for i in ten_million:
        l.gety(i)

with Timer() as t4:
    for i in ten_million:
        bl.gety(i)

print """\n\n################################
Times and differences for gety calculations over __call__
10 mil. calculations, in seconds
################################"""
print "          {0:^15}{1:^15}".format("Line", "BasicLine")
print "__call__: {0:^15.5}{1:^15.5}".format(t1.msecs/1000., t2.msecs/1000.)
print "gety:     {0:^15.5}{1:^15.5}".format(t3.msecs/1000., t4.msecs/1000.)
print "diff:     {0:^15.5}{1:^15.5}".format( (t1.msecs-t3.msecs if t1.msecs > t3.msecs else t3.msecs-t1.msecs) / 1000.,
                                       (t2.msecs-t4.msecs if t2.msecs > t4.msecs else t4.msecs-t2.msecs) / 1000.
                                    )
print "speedup:  {0:^15.5}{1:^15.5}".format( t1.msecs/t3.msecs if (t1.msecs > t3.msecs) else t3.msecs/t1.msecs,
                                       t2.msecs/t4.msecs if (t2.msecs > t4.msecs) else t4.msecs/t2.msecs
                                    )






################################################################################
##########################    META  EVENT    ###################################
##########################       TEST        ###################################
################################################################################


#first = r.get(camcol=2, field=425, filter="g")[0]
#x1 = first.x1
#y1 = 2*first.y1 -first.y2 + 279
#x2 = first.x2
#y2 = first.y2 + 279
#p1 = Point(x1, y1, camcol=2, filter="g")
#p2 = Point(x2, y2, camcol=2, filter="g")
#l = Line(p1, p2)
#test =  l.getCCDChips()
#l.showLine() #blue
#
#first = r.get(camcol=2, field=424, filter="g")[0]
#x1 = first.x1
#y1 = 2*first.y1 -first.y2 + 279
#x2 = first.x2
#y2 = first.y2 + 279
#p1 = Point(x1, y1, camcol=2, filter="g")
#p2 = Point(x2, y2, camcol=2, filter="g")
#l = Line(p1, p2)
#l.showLine() #blue
#
#first = r.get(camcol=3, field=430, filter="i")[0]
#x1 = first.x1
#y1 = 2*first.y1 -first.y2 + 279
#x2 = first.x2
#y2 = first.y2 + 279
#p1 = Point(x1, y1, camcol=3, filter="i")
#p2 = Point(x2, y2, camcol=3, filter="i")
#l = Line(p1, p2)
#l.showLine(color=(0,255,0)) #green
#
#
#first = r.get(camcol=4, field=432, filter="r")[0]
#x1 = first.x1
#y1 = 2*first.y1 -first.y2 + 279
#x2 = first.x2
#y2 = first.y2 + 279
#p1 = Point(x1, y1, camcol=4, filter="r")
#p2 = Point(x2, y2, camcol=4, filter="r")
#l = Line(p1, p2)
#l.showLine(color=(0,0,255)) #red
#
#
#first = r.get(camcol=3, field=429, filter="u")[0]
#x1 = first.x1
#y1 = 2*first.y1 -first.y2 + 279
#x2 = first.x2
#y2 = first.y2 + 279
#p1 = Point(x1, y1, camcol=3, filter="u")
#p2 = Point(x2, y2, camcol=3, filter="u")
#l = Line(p1, p2)
#l.showLine(color=(255, 255, 0)) #turqua
#
#
#first = r.get(camcol=3, field=428, filter="u")[0]
#x1 = first.x1
#y1 = 2*first.y1 -first.y2 + 279
#x2 = first.x2
#y2 = first.y2 + 279
#p1 = Point(x1, y1, camcol=3, filter="u")
#p2 = Point(x2, y2, camcol=3, filter="u")
#l = Line(p1, p2)
#l.showLine(color=(255, 255, 0)) #turqua