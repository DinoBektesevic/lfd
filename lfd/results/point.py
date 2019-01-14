"""Point class provides a more comfortable interface for handling coordinates
and coord transformations. Point is capable of moving and setting of new
coordinate values in any frame while maintaning consistency across all
coordinates.

There are two coordinate systems to manage: 'frame' and 'ccd'. Both are
expressed in units of pixels and both have an inverted y axis (increases from
from top to bottom such that the y coordinate remains positive within the CCD
array).

* 'ccd' coordinate system represents the whole CCD array, the area from (0, 0)
  to (MAX_W_CCDARRAY, MAX_H_CCDARRAY). This area contains all CCDs. One CCD is
  defined by (camcol, filter). There are 6 camcols and 5 filters. A point
  *anywhere* in this area can be represented in the 'ccd' coordinate system.
  The names of 'ccd' coordinates are (cx, cy).
* The 'frame' coordinate system is used to represent image-coordinates. These
  are the values measured by the detecttrails package. The origin of the
  coordinate system is set to be reference CCD's upper left corner. Coordinates
  (x, y) change if the chosen reference CCD changes. The 'frame' coordinate
  system is a slight misnomer as within each CCD there can be up to 3
  frames-xxxx-xx-x-xxx.fits images at once. The frame dimensions are 2048x2048
  but images are cut to 1489px height with 139px of overlap between following
  images. A point *within* any CCD can be represented in the 'frame' coordinate
  system.

To see the values defining both coordinate systems and how to convert between
them look at the ccd_dimensions and coord_conversion modules.

Warnings will be produced in an inconsistent situations to warn that,
logically, the performed operations do not make sense, but will not enforce
consistency at all times.

Important Notes
---------------

Point is capable of interpreting the coordinates in two different context. One
is as an absolute coordinate, usually in ccd coordinate system, and the other
as a frame-referenced coordinates in which case the coordinates remember a
reference to the frame they're defined in. In the latter case it is possible to
have 'frame' coordinates with numerically determined values even when they are
not within a CCD bounary, while in the former it is not because no reference
frame has been set. This can be bit confusing:

.. code-block:: python

   p = res.Point(3790, 5415, coordsys="ccd")
   <lfd.results.point.Point(x=None, y=None, cx=3790, cy=5415)>

   p2 = res.Point(-1, -1, camcol=2, filter="u")
   <lfd.results.point.Point(x=-1, y=-1, cx=3790.820956, cy=5415.8870802)>

Both points reference approximately the same coordinate except that the
frame-referenced Point understands which frame's (0, 0) point to use to
calculate the 'frame' coordinates x and y from. The same point can be expressed
referenced from a different frame:

.. code-block:: python

   p2 = res.Point(-7584.64, 2707, camcol=4, filter="i")
   <lfd.results.point.Point(x=-7584, y=2707, cx=3790.88, cy=5415.44)>

This makes more sense in the context of using the Point class to represent
the linear feature in the Event class, but it has some merrits as a feature
on its own.

"""

import warnings
warnings.simplefilter('always', SyntaxWarning)

from sqlalchemy.ext.mutable import MutableComposite

from lfd.results.coord_conversion import (convert_ccd2frame, convert_frame2ccd,
                                          CoordinateConversionError)

__all__ = ["Point"]

class Point(MutableComposite):
    """Provides a more comfortable interface for handling coordinates and coord
    transformations while  maintaning consistency across all coordinates.

    Parameters
    ----------

    x : float
      'ccd' or 'frame' coordinate, depending on coordsys
    y : float
      'ccd' or 'frame' coordinate, depending on coordsys
    coordsys : str
      'ccd' or 'frame', designation of coordinate system
    inCcd : bool
      True if the current coordinate is within a CCD
    camcol : int
      the camera column of reference frame
    filter :
      the filter row of the reference frame

    Example
    -------

    >>> p = Point(10, 10, coordsys="ccd")
    >>> p = Point(10, 10, camcol=2, filter='r')

    To switch between coordinate system:

    >>> p.useCoordSys('ccd')
    >>> p.switchSys()

    Check if current Point is in CCD or not

    >>> p.inCcd

    Moving the point can be by assignment or method. Method will try to resolve
    intended coordsys, or default to current coordsys, but assignment always
    uses currentl coordsys. Mixing coord. sys. is possible:

    >>> p.move(x=10, y=10)
    >>> p.move(cx=100, y=10)
    >>> p.y = 100

    """

    def __init__(self, x=None, y=None, cx=None, cy=None, camcol=None,
                 filter=None, coordsys="frame"):
        """p = Point(x, y, cx, cy, camcol, filter, coordsys)

        x, y     - point coordinates in 'frame' coord sys
        cx, cy   - point coordinates in 'ccd' coord sys
        coordsys - coordsys to be used
        camcol   - camera column, if 'frame' coord sys
        filter   - filter row, if 'filter' coord sys

        >>>  p = Point(10, 10) # assumes 'ccd'
        >>>  p = Point(3790, 5415, coordsys='ccd')
        >>>  p = Point(-1, -1, camcol=2, filter='u') # assumes 'filter'
        >>>  p = Point(-1, -1, camcol=2, filter='u', coordsys='frame')

        """

        self.coordsys = coordsys.lower()

        # assume we are inside CCD, will be set to False in conversions if we
        # are not
        self.inCcd = True

        if coordsys == "ccd" or (all([x, y]) and not any([camcol, filter])):
            cx, cy = x, y
            x, y = None, None

        # For the last elif - it's impossible to use the all([x, y, camcol, filter])
        # because x and y might have the value of 0 which is falsy. 
        if all([x, y, camcol, filter, cx, cy]):
            self._initAll(x, y, cx, cy, camcol, filter)
        elif self.coordsys == "ccd" and all((cx, cy)):
            self._initCCD(cx, cy)
        elif self.coordsys == "frame" and camcol is not None and \
             filter is not None and x is not None and y is not None:
            self._initFrame(x, y, camcol, filter)
        else:
            errmsg = "Expected (x,y, coordsys='ccd') or "
            errmsg += "(x, y, camcol, filter). Got ({0}, {1}, {2}, {3}, {4}) "
            errmsg += "instead."
            raise TypeError(errmsg.format(x, y, camcol, filter, coordsys))

    def _initAll(self, x, y, cx, cy, camcol, filter, check=True):
        # check for consistency when defaulting to immediate _initAll
        # do provided CCD coordinates actually match the given 'frame' coords.
        if check:
            tmpcx, tmpcy = convert_frame2ccd(x, y, camcol, filter)
            if tmpcx != cx or tmpcy != cy:
                msg = ("Supplied coordinates between two coordinate systems are "
                       "inconsistent. Received 'frame' (x={0}, y={1}, "
                       "camcol={2}, filter={3}) and 'ccd' (cx={4}, cy={5}) "
                       "coordinates, but calculated (cx={6}, cy={7}) 'ccd' "
                       "coordinates. Attempt a rollback.")
                raise ValueError(msg.format(x, y, camcol, filter, cx, cy,
                                            tmpcx, tmpcy))
        self._x = x
        self._y = y
        self._cx = cx
        self._cy = cy

        self._camcol = camcol
        self._filter = filter

        self.changed()

    def _initFrame(self, x, y, camcol, filter):
        # consistency check is not needed because conversion was done
        cx, cy = convert_frame2ccd(x, y, camcol, filter)
        self._initAll(x, y, cx, cy, camcol, filter, check=False)

    def _initCCD(self, cx, cy):
        # if we can't convert to frame system, inCcd == False then
        # we check if we are in frame-reference mode
        try:
            x, y, camcol, filter = convert_ccd2frame(cx, cy)
            self.inCcd = True
        except CoordinateConversionError:
            self.inCcd = False
            try:
                # if however there is no prior _x or _camcol we are not in frame
                # reference mode 
                x = self._x - (self._cx - cx)
                y = self._y - (self._cy - cy)
                camcol = self._camcol
                filter = self._filter
            except AttributeError:
                # and we default to a 'ccd' absolute position mode 
                x, y, camcol, filter = None, None, None, None
        # checks are again not needed as we are guaranteed consistency through
        # conversions
        self._initAll(x, y, cx, cy, camcol, filter, check=False)

    def __repr__(self):
        m = self.__class__.__module__
        n = self.__class__.__name__
        retrstr = "<{0}.{1}(x={2}, y={3}, cx={4}, cy={5})>"
        return retrstr.format(m, n, self._x, self._y, self._cx, self._cy)

    def __str__(self):
        return "Point(x={0}, y={1})".format(self.x, self.y)

    def __composite_values__(self):
        # order of variables is very important and has to match that of Event
        return self._x, self._y, self._cx, self._cy

    def _check_sensibility(self, attr):
        """For a given attribute attr checks for a series of conditions that
        indicate an illogical operation or in some cases operations that could
        leave an Event in an inconsistent state. Is not always correct, but
        that's why it's a warning not Error.

        +---------------+-----------------------------------------------------+
        |     Attrs     |                   Conditions                        |
        +---------------+-----------------------------------------------------+
        | camcol, filter| if coord. sys. is ccd providing these makes no sense|
        +---------------+-----------------------------------------------------+
        | frame         | if frame is sent as attr and self.inCcd is False    |
        |               | the frame coordinate system coordinates are not     |
        |               | defined.                                            |
        +---------------+-----------------------------------------------------+

        """
        msg = "Attribute {0} should only be accessed when coordsys={1}"
        if attr in (["camcol", "filter"]) and self.coordsys == "ccd":
            warnings.warn(msg.format(attr, "frame"), SyntaxWarning)
        if attr == "frame" and not self.inCcd:
            msg = ("Used coordinates are not within the boundary of any CCD: "
                   "(cx={0}, cy={1})")
            warnings.warn(msg.format(self._cx, self._cy))

    def useCoordSys(self, coordsys):
        """Use a particular coordinate system, either 'frame' or 'ccd'.

        Parameters
        ----------

        coordsys : str
          coordsys designation, 'frame' or 'ccd'

        """
        self._check_sensibility(coordsys)
        if coordsys.lower() in ["frame", "ccd"]:
            self.coordsys = coordsys.lower()

    def switchSys(self):
        """Switch to the other coordinate system ('frame'-> 'ccd' and
        vice-versa). Not particularily useful as both are usually accessible,
        but practical to state which coordinate system we are currently in.

        """
        if self.coordsys == "frame":
            self.useCoordSys("ccd")
        elif self.coordsys == "ccd":
            self.useCoordSys("frame")

    def move(self, *args, **kwargs):
        """Move a point to different coordinates. Supports a more flexible way
        to change Point coordinates than direct assignment. Checks are
        are performed and if the ingoing coordiantes do not match the coordsys,
        the Point is *NOT* moved and a warning is issued. This makes move very
        oppinionated and annoying, but it forces explicit statements about
        where and how the point is moved in the code.

        Example
        -------
        Implicitly resolves coordinates

        >>> move(1, 1, "frame") # --> x=1, y=1
        >>> move((1, 1), "frame") # --> x=1, y=1
        >>> move(1, 1, "ccd") # --> cx=1, cy=1
        >>> move((1, 1), "ccd") # --> cx=1, cy=1

        Refuses to work without coordsys specification

        >>> move(1, 1) # --> will always fail with error, no coordsys sent

        Missmatched coordinates and coordinate systems issue warnings

        >>> move(x=1, y=1, coordsys="ccd") # --> not moved, warning issued
        >>> move(cx=1, cy=1, coordsys="frame") # --> not moved, warning issued

        Partially specified coordinates will work only if coordsys is properly
        matched to the given coordiante which must be explicitly specified

        >>> move(1, "frame") # --> fails
        >>> move(x=1, coordsys="frame") # --> moves the x coordinate only
        >>> move(cx=1, coordsys="frame") # --> isses a warning, doesn't move x


        Parameters
        ----------
        **kwargs : dict
          x, y or cx, cy or coordsys  and their values

        **kwargs : dict
          x, y or cx, cy and coordsys  and their values

        """
        if not kwargs:
            try: x, y, coordsys = args
            except: pass
            try: (x, y), coordsys = args
            except: pass
            if coordsys == 'ccd':
                cx, cy = x, y
        else:
            x = kwargs.pop("x", self.x)
            y = kwargs.pop("y", self.y)
            cx = kwargs.pop("cx", self.cx)
            cy = kwargs.pop("cy", self.cy)
            coordsys = kwargs.pop("coordsys", self.coordsys)

        if coordsys == "frame":
            warn= True if (x==self.x) and (y==self.y) else False
            self._initFrame(x, y, self._camcol, self._filter)
        elif coordsys == "ccd":
            warn= True if (cx==self.cx) and (cy==self.cy) else False
            self._initCCD(cx, cy)
        else:
            warn = True

        if warn:
            warnings.warn("Unmantched coordinates and coordsys. Point not "
                          "moved.")

    @property
    def camcol(self):
        self._check_sensibility("camcol")
        return self._camcol

    @property
    def filter(self):
        self._check_sensibility("filter")
        return self._filter

    @property
    def x(self):
        if self.coordsys == "frame":
            return self._x
        elif self.coordsys == "ccd":
            return self._cx

    @x.setter
    def x(self, val):
        if self.coordsys == "frame":
            self._initFrame(val, self._y, self._camcol, self._filter)
        elif self.coordsys == "ccd":
            self._initCCD(val, self._cy)

    @property
    def y(self):
        if self.coordsys == "frame":
            return self._y
        elif self.coordsys == "ccd":
            return self._cy

    @y.setter
    def y(self, val):
        if self.coordsys == "frame":
            self._initFrame(self._x, val, self._camcol, self._filter)
        elif self.coordsys == "ccd":
            self._initCCD(self._cx, val)

