"""A collection of carious miscelaneous functionality that helps visualize the
profiles and results of convolutions and their numerical values.

"""
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

from lfd.analysis.profiles.convolutionobj import ConvolutionObject
from lfd.analysis.profiles.convolution import convolve
from lfd.analysis.profiles.objectprofiles import *
from lfd.analysis.profiles.seeing import *

__all__ = ["plot_profiles"]

def plot_profiles(ax, profiles, *args, normed=True, **kwargs):
    """Normalizes all given profiles and then plots them on a given axis. Set
    normed to False if normalization is not desired. Lables are determined from
    the name attribute of the profile. `*args` and `**kwargs` are forwarded to
    the matplotlib plot function.

    """
    for profile in profiles:
        if normed:
            profile.norm()
        ax.plot(profile.scale, profile.obj, label=profile.name, *args, **kwargs)
    return ax


#def create_table()

#def tableRabina():
#    for h in heights:
#        o = RabinaProfile("Rabina/img15_r.png", h)
#        d = FluxPerAngle(h, *sdss)
#
#        ofwhm = o.calc_fwhm()
#
#        c = convolve(o, d)
#        dfwhm1 = c.calc_fwhm()
#
#        o = o = RabinaProfile("Rabina/img15_r.png", h)
#        s = GausKolmogorov(sdssseeing)
#        d = FluxPerAngle(h, *sdss)
#
#        c = convolve(o, s, d)
#        obsfwhm1 = c.calc_fwhm()
#
#
#
#        o = RabinaProfile("Rabina/img15_r.png", h)
#        d = FluxPerAngle(h, *lsst)
#
#        c = convolve(o, d)
#        dfwhm2 = c.calc_fwhm()
#
#        o = RabinaProfile("Rabina/img15_r.png", h)
#        s = GausKolmogorov(lsstseeing)
#        d = FluxPerAngle(h, *lsst)
#
#        c = convolve(o, s, d)
#        obsfwhm2 = c.calc_fwhm()
#
#
#        res = "{0}&\t{1:.2f}&\t{2:.2f}&\t{3:.2f}&\t{4:.2f}&\t{5:.2f}\\\\"
#        print res.format(int(h), ofwhm, dfwhm1, obsfwhm1, dfwhm2, obsfwhm2)
#
