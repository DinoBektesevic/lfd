"""A slight missnomer of the module hides the fact that seeing contains both
the 1D seeing profiles that reproduce the effects of atmospheric seeing on a
object integrated brightness profile but also the defocus function as used and
described in::

  Bektesevic & Vinkovic et. al. 2017 (arxiv: 1707.07223)
"""
import numpy as np

from lfd.analysis.profiles.convolutionobj import ConvolutionObject
from lfd.analysis.profiles.consts import RAD2ARCSEC


__all__ = ["FluxPerAngle"]


class FluxPerAngle(ConvolutionObject):
    """The defocusing model as given by Equation (6) in::

        Bektesevic & Vinkovic et. al. 2017 (arxiv: 1707.07223)

    Parameters
    ----------
    h : float
      Distance to the object in kilometers.
    instrument : tuple
        Tuple of flot values (Ro, Ri) describing the diameter of primary and
        secondary mirror of used instrument, in milimeters.
    scale : list, tuple or np.array
      if scale is not given, appropriate scale will be created from d, Ro and
      Ri
    units : str
      in arcseconds by default - not very well supported
    res : float
      desired resolution in arcseconds, if scale is not given
    """
    def __init__(self, h, instrument, scale=None, units="arcsec", res=0.001,
                 **kwargs):
        if scale is None:
            self.h = h
            self.Ro, self.Ri = instrument
            thetao = self.Ro / (h * 1000000.)
            radscale = np.arange(-2*thetao, 2*thetao, thetao*res)
            scale = np.multiply(radscale, RAD2ARCSEC)
        obj = self.f(scale, h, instrument, units=units)

        ConvolutionObject.__init__(self, obj, scale)

    def f(self, r, h=None, instrument=None, units="arcsec"):
        """Estimate the value of the function at a point r. For convenience and
        quick calculations d, Ro, Ri and units can be provided too, otherwise
        the values used when creating an object are used.
        """
        # a 98% speedups were achieved for the case of self.rescale function
        # or equivalently a 1371 times faster execution - Jan 2018

        # standardize the output format
        if any((isinstance(r, int), isinstance(r, float), isinstance(r, complex))):
            rr = np.array([r], dtype=float)
        else:
            rr = np.array(r, dtype=float)

        # we check more explicitly here than in others because the default unit
        # is arcsec instead of RAD like elsewhere, but calculations are in RAD
        if units.upper() not in ("RAD", "ARCSEC"):
            raise ValueError("Unrecognized units. Options: 'rad'"
                             f"or 'arcsec' instead recieved {units}")

        if units.upper() == "ARCSEC":
            rr = rr / RAD2ARCSEC

        if instrument is None:
            Ro, Ri = None, None
        else:
            Ro, Ri = instrument

        if not all([h, Ro, Ri]):
            h = self.h
            Ro = self.Ro
            Ri = self.Ri

        thetao = Ro / (h * 1000000.)
        thetai = Ri / (h * 1000000.)
        thetao2 = thetao * thetao
        thetai2 = thetai * thetai

        # Solving the equation involves sometimes taking a square root of very
        # small negative numbers, We silence that warning.
        with np.errstate(invalid='ignore'):
            def defocusf(x):
                lambda x: 2./(np.pi*(thetao2 - thetai2)) * (
                    np.nan_to_num(np.sqrt(thetao2-x*x))
                    - np.nan_to_num(0.5*(np.sign(thetai-x)+1) * np.sqrt(thetai2-x*x))
                )
            res = defocusf(rr)

        return res
