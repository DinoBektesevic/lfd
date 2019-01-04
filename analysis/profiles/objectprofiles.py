import numpy as np
import cv2
from .convolutionobj import ConvolutionObject

class PointSource(ConvolutionObject):
    """Simple point like source. Point-like sources are not resolved, therefore
    regardless of scale and size only a single element of obj will have a value

        init params
    -------------------
    h   - height of the object
    res - desired resolution, the scale (the difference between two
          neighbouring "x-axis" points is then determined by scaling the
          appropriate angular size of the object, so that it is still
          unresolved at the required resolution, by the desired resolution)
    """
    def __init__(self, h, res=0.001):
        theta = 1.0/(h*1000.) * RAD2ARCSEC
        scale = np.arange(-theta, theta, theta*res)

        obj = self.f(scale)
        ConvolutionObject.__init__(self, obj, scale)

    def f(self, r):
        """Returns the intensity value of the object at a point."""
        if hasattr(r, "__iter__"):
            obj = np.zeros(r.shape)
            obj[len(obj)/2] += 1.0
            return obj
        else:
            peak = np.where(self.obj == self.obj.max())[0][0]
            if (r - self.scale[peak]) <= self.step:
                return self.obj.max()
            else:
                return 0

class Gauss(ConvolutionObject):
    """Simple gaussian intensity profile.

         init params
    -------------------
    h     - height of the object
    fwhm  - FWHM of the gaussian profile
    res   - desired resolution
    units - spatial units (meters by default)
    """
    def __init__(self, h, fwhm, res=0.001, units="meters"):
        theta = fwhm/(h*1000.)*RAD2ARCSEC

        self.scale = np.arange(-1.7*theta, 1.7*theta, theta*res)
        self.sigma = fwhm/2.355
        self.f = stats.norm(scale=fwhm/2.355).pdf

        obj = self.f(self.scale)
        ConvolutionObject.__init__(self, obj, self.scale)

class DiskSource(ConvolutionObject):
    """Brightness profile of a disk-like source.

         init params
    -------------------
    h      - height of the object
    radius - radius of the objects disk
    res    - desired resolution
    """
    def __init__(self, h, radius, res=0.001):
        theta = radius/(2*h*1000.) * RAD2ARCSEC

        self.r = radius
        self.theta = theta
        self.scale = np.arange(-2*theta, 2*theta, theta*res)

        obj = self.f(self.scale)
        ConvolutionObject.__init__(self, obj, self.scale)

    def f(self, r, units="arcsec"):
        """Returns the brightness value of the object at a point. By default
        the units of the scale are arcseconds but radians are also accepted.
        """
        if units.upper() == "RAD":
            r = np.multiply(r, RAD2ARCSEC)
        if hasattr(r, "__iter__"):
            pass
        else:
            r = np.asarray(r)
        return np.asarray(map(self._f, r))

    def _f(self, x):
        theta = self.theta
        if abs(x) > theta:
            return 0
        else:
            return 2*np.sqrt(theta*theta-x*x)/(np.pi*self.theta*self.theta)

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


class RabinaProfile(ConvolutionObject):
    """ Rabina J., et al. 2016, J. Quant. Spectrosc. Radiat. Transf,178, 295
    provide a fiducial 3D model of the meteor head. The integration of this
    profile is complicated and depends on variety of parameters, such as the
    angle of the observer linesight and meteor direction of travel. It is not
    practical to preform the integration every time brightness value needs to
    be estimated (too slow).
    A set of pregenerated projections of this profile to a plane  were created
    where the angle between meteor direction of travel and observer linesight
    varies in the range from 0-1.5 radians (0-86 degrees) which are then used
    to produce this 1D profile. The 1D profile is created from a crosssection
    perpendicular to the meteors direction of travel. 
    These 2D profiles are avilable as images in the rabina directory along with
    the required code to generate them.
    The default profile is then scaled appropriately to the desired height and
    any missing brightness values are then interpolated between the points.

         init params
    -------------------
    h       - height of the object
    imgpath - path to the image of the 2D integrated profile
    """
    xmin, xmax = -5., 5.
    ymin, ymax = -5., 5.
    zmin, zmax = -5., 5.
    N = 1000.

    def __init__(self, imgpath, h):
        #xmin, xmax = RabinaProfile.xmin, RabinaProfile.xmax
        ymin, ymax = RabinaProfile.ymin, RabinaProfile.ymax

        #xstep = (xmax-xmin)/RabinaProfile.N
        ystep = (ymax-ymin)/RabinaProfile.N

        imgneg = cv2.imread(imgpath, cv2.IMREAD_GRAYSCALE)
        white = 255.*np.ones(imgneg.shape)

        img = -1.*(imgneg-white)
        imgr = np.zeros(img.shape)
        imgr[2:-2, 2:-2] += img[2:-2, 2:-2]
        imgrn = imgr/imgr.max()

        #meterscalex = np.arange(xmin, xmax, xstep)
        meterscaley = np.arange(ymin, ymax, ystep)

        #scalex = meterscalex/(h*1000.) * RAD2ARCSEC
        scaley = meterscaley/(h*1000.) * RAD2ARCSEC
        #self.distx = imgrn.sum(axis=0)
        disty = imgrn.sum(axis=1)

        self.raw = imgrn
        self.scaley = scaley

        ConvolutionObject.__init__(self, disty, scaley)

    def f(self, r, units="arcsec"):
        """Returns the brightness value at a desired point."""
        if units.upper() == "RAD":
            rarcsec = np.multiply(r, RAD2ARCSEC)
        else:
            if not hasattr(r, "__iter__"):
                rarcsec = np.asarray([r])
            else:
                rarcsec = r
        return np.asarray(map(self._f, rarcsec))


    def _f(self, x):
        if abs(x) >= self.scaley[-1]:
            return 0
        else:
            return self._guessf(x)

def exp_fwhms(tau, n, duration):
    """Generates series of n exponentially smaller FWHM values depending on the
    scale time tau for the desired temporal duration. 
    """
    times = np.linspace(0, duration, n)
    fwhms = np.exp(times/tau)
    return fwhms
