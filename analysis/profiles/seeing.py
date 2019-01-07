import numpy as np

from .convolutionobj import ConvolutionObject
from .consts import *

import copy

__all__ = ["GausKolmogorov", "FluxPerAngle"]

class GausKolmogorov(ConvolutionObject):
    """Simple Gaus-Kolmogorov seeing. Convolving with this function has the
    effect of blurring the original object.

        init params
    ------------------
    fwhm  - FWHM of the GK 
    scale - if scale is given then GK will be evaluated over it
    res   - if it is not given a scale will be created from the estimated width
            of the GK and resolution res
    """
    def __init__(self, fwhm, scale=None, res=0.001):

        self.sigma = 1.035/FWHM2SIGMA*fwhm
        self.sigma2 = 2.*self.sigma

        if scale is None:
            scale = np.arange(-4*self.sigma2, 4*self.sigma2, res)
            obj = self.f(scale)
        else:
            scale = scale
            obj = self.f(scale)
        ConvolutionObject.__init__(self, obj, scale)


    def f(self, r, sigma=None):
        """Evaluates the GK at a point r. Providing sigma estimates GK at r for
        a different GK distribution with a FWHM= sigma*2.436/1.035 - for
        convenience only.
        """
        if sigma is None:
            sigma = self.sigma
        sigma2 = sigma
        gk = lambda x: 0.909*( 1/(2*np.pi*sigma*sigma) * \
                               np.exp( -1.0 * (x*x / (2*sigma*sigma)) ) + \
                               0.1*( 1/(2*np.pi*sigma2*sigma2) * \
                                     np.exp( -1.0 * (x*x / (2*sigma2*sigma2)))
                                   )
                              )

        try:
            return gk(r)
        except TypeError:
            return gk(np.asarray(r))


class FluxPerAngle(ConvolutionObject):
    """The defocusing model as given by Equation (6) in
        Bektesevic & Vinkovic et. al. 2017 (arxiv: 1707.07223)

        init params
    ------------------
    d     - the width of the object 
    Ro    - the diameter of the primary mirror of used instrument
    Ri    - the diameter of secondary mirror of the used instrument
    scale - if scale is not given, appropriate scale will be created from d, Ro
            and Ri, otherwise provided scale is used
    units - in arcseconds by default
    res   - desired resoltion if scale is not given
    """
    def __init__(self, d, Ro, Ri, scale=None, units="arcsec", res=0.001):

        if scale is None:
            self.d = d
            self.Ro = Ro
            self.Ri = Ri
            thetao = Ro / (d * 1000000.)
            thetai = Ri / (d * 1000000.)
            radscale = np.arange(-2*thetao, 2*thetao, thetao*res)
            scale = np.multiply(radscale, RAD2ARCSEC)
        obj = self.f(scale, d, Ro, Ri, units=units)

        ConvolutionObject.__init__(self, obj, scale)

    def f(self, r, d=None, Ro=None, Ri=None, units="arcsec"):
        """Estimate the value of the function at a point r. For convenience and
        quick calculations d, Ro, Ri and units can be provided too, otherwise
        the values used when creating an object are used.
        """
        # a 98% speedups were achieved for the case of self.rescale function
        # or equivalently a 1371 times faster execution - Jan 2018

        # standardize the output format
        if any((isinstance(r, int), isinstance(r, float),
               isinstance(r, complex))):
            rr = np.array([r], dtype=float)
        else:
            rr = np.array(r, dtype=float)

        # we check more explicitly here than in others because the default unit
        # is arcsec instead of RAD like elsewhere, but calculations are in RAD
        if units.upper() not in ("RAD", "ARCSEC"):
            raise ValueError("Unrecognized units. Options: 'rad'" + \
                             "or 'arcsec' instead recieved {0}".format(units))

        if units.upper() == "ARCSEC":
            rr = rr/RAD2ARCSEC
        
        if not all([d, Ro, Ri]):
            d = self.d
            Ro = self.Ro
            Ri = self.Ri

        thetao = Ro / (d * 1000000.)
        thetai = Ri / (d * 1000000.)
        thetao2 = thetao*thetao
        thetai2 = thetai*thetai
        defocusf = lambda x: 2./(np.pi*(thetao2 - thetai2)) * \
                   (
                        np.nan_to_num(np.sqrt(thetao2-x*x)) -
                        np.nan_to_num(0.5*(np.sign(thetai-x)+1) * np.sqrt(thetai2-x*x))
                    )

        return defocusf(rr)


        
