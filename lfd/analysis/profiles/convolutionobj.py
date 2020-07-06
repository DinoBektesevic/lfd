import numpy as np
import warnings
from scipy import misc, signal, interpolate, stats


class ConvolutionObject:
    """Represents an object that can be convolved with other ConvolutionObjects
    or functions. Practical because the objects can be created with or without
    knowing their analytical expressions.
    ConvolutionObject can be instantiated from two arrays - scale and obj.
    Scale represents the "x-axis" and the obj array the function value at some
    x-coordinate. The function is then constructed by interpolating between the
    obj points.
    If an object's analytical light-curve is known then user can override the
    method 'f' such that it returns the value of the analytical expression at
    a given coordinate.

    Attributes
    ----------
    obj : list, tuple or np.array
      brightness values of the object, its profile
    scale : list, tuple or np.array
       the "x" coordinates against which obj was evaluated, note that objects
       "center" (central maximal value) is generally centered on the 0 of the
       scale
    __guessf : np.interp1d
       the function used for interpolation in case analytical form is unknown
    scaleleft : float
      leftmost points of the scale
    scaleright : float
      rightmost points of the scale
    objleft : float
      rightmost points at which obj>0
    objright : float
      rightmost points at which obj>0
    step : float
      the difference between two scale points (fineness of the coordinates)
    name : str
      by default assigned to the class name instantiating this object. Useful
      to keep track of the function it represents but also for plotting.

    Parameters
    ----------
    obj : list, tuple or np.array
      brightness values of the object, its profile
    scale : list, tuple or np.array
       the "x" coordinates against which obj was evaluated, note that objects
       "center" (central maximal value) is generally centered on the 0 of the
       scale

    """
    @classmethod
    def fromConvolution(cls, obj, scale, name=None):
        """From given arrays obj and scale create a ConvolutionObject."""
        if name is None:
            name = "convolved"

        lendiff = len(obj) - len(scale)
        half = int(lendiff/2)

        obj = obj[half:-half]

        if len(obj) > len(scale):
            obj = obj[:len(scale)]
        elif len(obj) < len(scale):
            tmp = np.zeros((len(scale), ))
            tmp[:len(obj)] += obj
            obj = tmp
        else:
            pass
        return ConvolutionObject(obj, scale, name=name)

    def __init__(self, obj, scale, name=None):
        if name is None:
            self.name = self.__class__.__name__
        else:
            self.name = name
        self.obj = obj
        self.scale = scale
        self.__guessf = interpolate.interp1d(scale, obj)
        self.update()

    def _guessf(self, r):
        """Estimates the value of the profile in new points r via interpolation
        when possible. Interpolation is only allowed within the scale range of
        the original scale used to create the object. Values outside that
        scale are assumed to be zero.

        Parameters
        ----------
        r : `np.array` or `list`
            Scale on which the profile is to be evaluated.
        """
        try:
            warnings.warn("Required value estimated by interpolation.")
            return self.__guessf(r)
        except ValueError:
             warnings.warn("Interpolation performed for value outside scale range. "
                          "This can occur when extending profiles into tails of "
                          "their distribution where they are assumed to be 0. "
                          "Is this the case?")
             newobj = np.zeros(len(r))
             overlap = (r>self.scaleleft) & (r < self.scaleright)
             newobj[overlap] += self.__guessf(r[overlap])
             return newobj

    def f(self, r=None):
        """Returns the value of the profile function at a point/array of points
        r. If analytical expression is not know interpolation between nearest
        points is attempted. If this occurs a warning is raised.
        """
        return self._guessf(r)

    def rescale(self, x, y=None, step=None):
        """Given a scale x recalculate the brightness values of obj over the
        new points.
        If only x and y are supplied, then a new scale is created with the
        new boundaries [x, y> and previously used step
        If x, y and step are provided then a new scale is created with new
        boundaries [x, y> where the distance between two points equals to step.
        """
        if y is not None and step is not None:
            newscale = np.arange(x, y, step)
        elif y is not None and step is None:
            newscale = np.arange(x, y, self.step)
        else:
            newscale = x

        # must be called before update so that scaleleft and scaleright
        # remain unchanged from the original
        self.obj = self.f(newscale)
        self.scale = newscale
        self.update()

    def update(self):
        """Check and update the scale left and rightmost points. Find the
        first and last coordinate at which object is still brighter than 0.
        Recalcualtes step.
        """
        self.scaleleft = self.scale[0]
        self.scaleright = self.scale[-1]
        self.objleft = np.where(self.obj > 0.0)[0][0]
        self.objright = np.where(self.obj > 0.0)[0][0]
        self.step = self.scale[1]-self.scale[0]
        self.peak = self.obj.max()

    def norm(self):
        """Renormalizes values so that maximal value is 1."""
        self.obj = self.obj/self.peak
        self.peak = 1

    def __str__(self):
        m = self.__class__.__module__
        n = self.__class__.__name__
        self.update()
        tmpstr = "<{0}.{1}(scale=[{2:.2}...{3:.2}], step={4:.3}, width={5}>"
        return tmpstr.format(m, n, self.scaleleft, self.scaleright, self.step,
                             self.objright-self.objleft)

    def calc_fwhm(self):
        """Calculates Full-Width-Half-Maximum of the object."""
        if len(self.obj) != len(self.scale):
            errormsg = ("Expected len(obj) == len(scale) but got, "
                       "len({0}) != len({1}) instead. Run rescale method "
                       "for possible fix.")
            raise ValueError(errormsg.format(len(self.obj), len(self.scale)))

        #maxobj = max(self.obj)
        left = np.where(self.obj >= self.peak/2.)[0][0]
        right = np.where(self.obj >= self.peak/2.)[0][-1]

        if left == right:
            return 0.0

        fwhm1 = self.scale[left]
        fwhm2 = self.scale[right]
        fwhm = abs(fwhm2) + abs(fwhm1)

        return fwhm
