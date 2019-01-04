import numpy as np
import warnings
from scipy import misc, signal, interpolate, stats

class ConvolutionObject(object):
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
    ------------------
    obj                   - brightness values of the object, its profile
    scale                 - the "x" coordinates against which obj was evaluated
    __guessf              - the function used for interpolation in case
                            analytical form is unknown
    scaleleft, scaleright - left and rightmost points of the scale
    objleft, objright     - left and rightmost points at which the obj > 0
    step                  - the difference between two scale points (fineness
                            of the coordinates)
    """
    @classmethod
    def fromConvolution(cls, obj, scale):
        """From given arrays obj and scale create a ConvolutionObject."""
        lendiff = len(obj) - len(scale)
        half = lendiff/2

        obj = obj[half:-half]

        if len(obj) > len(scale):
            obj = obj[:len(scale)]
        elif len(obj) < len(scale):
            tmp = np.zeros((len(scale), ))
            tmp[:len(obj)] += obj
            obj = tmp
        else:
            pass
        return ConvolutionObject(obj, scale)

    def __init__(self, obj, scale):
        self.obj = obj
        self.scale = scale
        self._guessf = interpolate.interp1d(scale, obj)
        self.update()

    def f(self, r=None):
        """Returns the value of the profile function at a point/array of points
        r. If analytical expression is not know interpolation between nearest
        points is attempted. If this occurs a warning is raised.
        """
        warnings.warn(("Required value estimated by interpolation - this is
                       usually not correct."))
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
            self.scale = np.arange(x, y, step)
        elif y is not None and step is None:
            self.scale = np.arange(x, y, self.step)
        else:
            self.scale = x

        self.obj = self.f(self.scale)
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

    def norm(self):
        """Renormalizes values so that maximal value is 1."""
        self.obj = self.obj/self.obj.max()

    def calc_fwhm(self):
        """Calculates Full-Width-Half-Maximum of the object."""
        if len(self.obj) != len(self.scale):
            errormsg = "Expected equal length object and scale arrays, " + \
                       "got {0} and {1} instead. Run rescale method " + \
                       "for possible fix"
            raise ValueError(errormsg.format(len(self.obj), len(self.scale)))

        left = np.where(self.obj >= max(self.obj)/2.)[0][0]
        right = np.where(self.obj >= max(self.obj)/2.)[0][-1]

        if left == right:
            return 0.0

        fwhm1 = self.scale[left]
        fwhm2 = self.scale[right]
        fwhm = abs(fwhm2) + abs(fwhm1)

        return fwhm
