"""
Profiles module consists of classes and functions neccessary to reproduce the
plots from Bektesevic & Vinkovic et. al. 2017 (arxiv: 1707.07223).

The module provides classes for various different types of object brightness
profiles (PointSource, GaussianSource, DiskSource, RabinaSource), seeing (Gaus-
Kolmogorov), and defocusing effects (FluxPerAngle).

Sources represent 1D integrated brightness profiles of different source
distributions  as well as various parameters describing these distributions
(such as FWHM, width, distance from instrument, variance etc.) in a common
lookalike interface. They usually carry with them their resolution, scale or
units.

Convolving Sources with Seeing and/or Defocus profile produce a new Source,
which brightness profile corresponds to that of an source which is affected by
these efects. So a convolution of a PointSource and seeing represents a source
in focus observed through an atmoshere and PointSource convolved with Defocus
corresponds to a defocused point source in ideal seeing (no seeing effects) etc

The module also provides a light wrapper around plotting utilities in
matplotlib (but this is by no means extensive).

    Usage
---------------
>>> from lfd.analysis import profiles

>>> point = profiles.PointSource(100)
>>> seeing = profiles.GausKolmogorov(profiles.SDSSSEEING)
>>> defocus = profiles.FluxPerAngle(100, *profiles.SDSS)

>>> a = profiles.convolve(point, seeing, defocus)

>>> import matplotlib.pyplot as plt
>>> fig, ax = plt.subplots(1, 1)
>>> profiles.plot_profiles(ax, (point, seeing, defocus, a))
>>> plt.legend()
>>> plt.show()
"""


from .seeing import *
from .consts import *
from .plotutils import *
from .convolution import *
from .objectprofiles import *
from .convolutionobj import ConvolutionObject

