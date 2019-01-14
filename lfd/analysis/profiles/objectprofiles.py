"""Object profiles contains commonly used profiles of different types of source
objects such as PointSource, Disk etc...

"""
import copy

import numpy as np
from scipy import stats
import cv2

from lfd.analysis.profiles.convolutionobj import ConvolutionObject
from lfd.analysis.profiles.consts import *

__all__ = ["PointSource", "GaussianSource", "DiskSource", "RabinaSource"]

class PointSource(ConvolutionObject):
    """Simple point like source. Point-like sources are not resolved, therefore
    regardless of scale and size only a single element of obj will have a value

    Parameters
    ----------
    h : float
      height of the object, in meters
    res : float
      desired resolution in arcseconds. The scale step (the difference between
      two neighbouring "x-axis" points) is then determined by scaling the
      appropriate angular size of the object by the resolution, so that the
      object remains unresolved at the required resolution.
    """
    def __init__(self, h, res=0.001):
        theta = 1.0/(h*1000.) * RAD2ARCSEC
        scale = np.arange(-theta, theta, theta*res)

        obj = self.f(scale)
        ConvolutionObject.__init__(self, obj, scale)

    def f(self, r):
        """Returns the intensity value of the object at a point. Evaluating a
        point source over only handfull of points is not well defined. The
        function may not behave properly if number of points is very small,
        i.e. 2 or 3 points only.
        """
        if hasattr(r, "__iter__"):
            # if PointSource is evaluated over an array with finer grid than
            # scale and we calculate the values we would get max value for all
            # points closer than current scale step - this wouldn't be a point
            # so instead a new array of same shape is returned with only 1
            # element at max - a point source. We make a check if r is ndarray
            # or just a list or tuple
            try:
                obj = np.zeros(r.shape)
            except AttributeError:
                obj = np.zeros(len(r))
            obj[int(len(obj)/2)] += 1.0
            return obj
        else:
            # in the case where we evaluate at a singular point 
            # if the position is closer to the location of the peak than the
            # resolution of our scale - we are looking at the source, otherwise
            # we are looking somewhere else
            peak = np.where(self.obj == self.obj.max())[0][0]
            if (r - self.scale[peak]) <= self.step:
                # standardize the output format to numpy array even in case of
                # a single number
                return np.array([self.obj.max()])
            else:
                return np.array([0.0])

class GaussianSource(ConvolutionObject):
    """Simple gaussian intensity profile.

    Parameters
    ----------
    h : float
      height of the object, in meters
    fwhm : float
      FWHM of the gaussian profile
    res : float
      desired resolution, in arcseconds
    units : string
      spatial units (meters by default) - currently not very well supported
    """
    def __init__(self, h, fwhm, res=0.001, units="meters"):

        self.theta = fwhm/(h*1000.)*RAD2ARCSEC
        self.sigma = fwhm/2.355
        self._f = stats.norm(scale=fwhm/2.355).pdf

        scale = np.arange(-1.7*self.theta, 1.7*self.theta, self.theta*res)
        obj = self.f(scale)
        ConvolutionObject.__init__(self, obj, scale)

    def f(self, r):
        """Evaluate the gaussian at a point."""
        # standardize the output format to numpy array even in case of a number
        if any((isinstance(r, int), isinstance(r, float),
               isinstance(r, complex))):
            rr = np.array([r], dtype=float)
        else:
            rr = np.array(r, dtype=float)

        return self._f(rr)


class DiskSource(ConvolutionObject):
    """Brightness profile of a disk-like source.

    Parameters
    ----------
    h : float
      height of the object, in meters
    radius : float
      radius of the objects disk, in meters
    res : float
      desired resolution, in arcseconds
    """
    def __init__(self, h, radius, res=0.001):
        self.r = radius
        self.theta = radius/(2*h*1000.) * RAD2ARCSEC

        scale = np.arange(-2*self.theta, 2*self.theta, self.theta*res)
        obj = self.f(scale)

        ConvolutionObject.__init__(self, obj, scale)


    def f(self, r, units="arcsec"):
        """Returns the brightness value of the object at a point. By default
        the units of the scale are arcseconds but radians are also accepted.
        """
        # 99% (578x) speedup was achieved refactoring this code - Jan 2018 

        # standardize the output format to numpy array even in case of a number
        if any((isinstance(r, int), isinstance(r, float),
               isinstance(r, complex))):
            rr = np.array([r], dtype=float)
        else:
            rr = np.array(r, dtype=float)

        if units.upper() == "RAD":
            rr = rr*RAD2ARCSEC

        theta = self.theta
        _f = lambda x: 2*np.sqrt(theta**2-x**2)/(np.pi*theta**2)

        # testing showed faster abs performs faster for smaller arrays and
        # logical_or outperforms abs by 12% for larger ones 
        if len(rr) < 50000:
            mask = np.abs(rr)>=theta
        else:
            mask = np.logical_or(rr>theta, rr<-theta)

        rr[mask] = 0
        rr[~mask] = _f(rr[~mask])

        return rr


    def width(self):
        """FWHM is not a good metric for measuring the end size of the object
        because disk-like profiles do not taper off towards the top. Instead
        width of the object (difference between first and last point with
        brightness above zero) is a more appropriate measure of the size of the
        object.

        """
        left = self.scale[np.where(self.obj > 0)[0][0]]
        right = self.scale[np.where(self.obj > 0)[0][-1]]
        return right-left


class RabinaSource(ConvolutionObject):
    """::

      Bektesevic & Vinkovic et. al. 2017 (arxiv: 1707.07223) Eq. (9)

    a 1D integrated projection of fiducial 3D meteor head model as given by::

      Rabina J., et al. 2016, J. Quant. Spectrosc. Radiat. Transf,178, 295

    The integration of this profile is complicated and depends on variety of
    parameters, such as the angle of the observer linesight and meteor
    direction of travel. It is not practical to preform the integration every
    time brightness value needs to be estimated (too slow).
    A set of pregenerated projections of this profile to a plane were created
    where the angle between meteor direction of travel and observer linesight
    varies in the range from 0-1.5 radians (0-86 degrees) which are then used
    to produce this 1D profile. The 1D profile is created from a crosssection
    perpendicular to the meteors direction of travel. 
    These 2D profiles are avilable as images in the rabina directory along with
    the required code to generate them.
    The default profile is then scaled appropriately to the desired height and
    any missing brightness values are then interpolated between the points.

    Parameters
    ----------
    h : float
      height of the object, in meters
    imgpath : str
      path to the image of the 2D integrated profile, the precalculated
      profiles can be found in lfd/analysis/profiles/rabina alongside with the
      code required to generate new ones.
    """
    xmin, xmax = -5., 5.
    ymin, ymax = -5., 5.
    zmin, zmax = -5., 5.
    N = 1000.

    def __init__(self, imgpath, h):
        #xmin, xmax = RabinaProfile.xmin, RabinaProfile.xmax
        #ymin, ymax = RabinaSource.ymin, RabinaSource.ymax

        #xstep = (xmax-xmin)/RabinaProfile.N
        ystep = (RabinaSource.ymax- RabinaSource.ymin)/RabinaSource.N

        imgneg = cv2.imread(imgpath, cv2.IMREAD_GRAYSCALE)
        white = 255.*np.ones(imgneg.shape)

        img = -1.*(imgneg-white)
        imgr = np.zeros(img.shape)
        imgr[2:-2, 2:-2] += img[2:-2, 2:-2]
        imgrn = imgr/imgr.max()

        #meterscalex = np.arange(xmin, xmax, xstep)
        meterscaley = np.arange( RabinaSource.ymin,  RabinaSource.ymax, ystep)

        #scalex = meterscalex/(h*1000.) * RAD2ARCSEC
        scaley = meterscaley/(h*1000.) * RAD2ARCSEC
        #self.distx = imgrn.sum(axis=0)
        disty = imgrn.sum(axis=1)

        self.raw = imgrn
        self.scaley = scaley

        ConvolutionObject.__init__(self, disty, scaley)

    def f(self, r, units="arcsec"):
        """Returns the brightness value at a desired point."""
        # 10x aster than previous impementation - Jan 2018

        # standardize the output format
        if any((isinstance(r, int), isinstance(r, float),
               isinstance(r, complex))):
            rr = np.array([r], dtype=float)
        else:
            rr = np.array(r, dtype=float)

        if units.upper() == "RAD":
            rr = rr*RAD2ARCSEC
        
        # testing showed faster abs performs faster for smaller arrays and
        # logical_or outperforms abs by 12% for larger ones 
        if len(rr) < 50000:
            mask = np.abs(rr)>=self.scaley[-1]
        else:
            mask = np.logical_or(rr>self.scaley[-1], rr<-scaley[-1])

        rr[mask] = 0
        rr[~mask] = self._guessf(rr[~mask])
        return rr


def exp_fwhms(tau, n, duration):
    """Generates series of n exponentially smaller FWHM values depending on the
    scale time tau for the desired temporal duration.

    Parameters
    ----------
    tau : float
      scale time of the decay
    n : int
      number of generated FWHM values
    duration : float
      total duration in which n FWHMs will be equaly spaced
    """
    times = np.linspace(0, duration, n)
    fwhms = np.exp(times/tau)
    return fwhms
