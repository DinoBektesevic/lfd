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
units (units are more for personal reference than actually useful).

Convolving Sources with Seeing and/or Defocus profile produce a new Source,
which brightness profile corresponds to that of an source which is affected by
these efects. So a convolution of a PointSource and seeing represents a source
in focus observed through an atmoshere and PointSource convolved with Defocus
corresponds to a defocused point source in ideal seeing (no seeing effects) etc

The module also contains a more powerful generic sampler that produces profiles
and/or specific measurements in given points. 

Examples
--------

A simple convolution of a point profile with SDSS seeing and defocus:

.. code-block:: python

     from lfd.analysis import profiles

     point = profiles.PointSource(100)
     seeing = profiles.GausKolmogorov(profiles.SDSSSEEING)
     defocus = profiles.FluxPerAngle(100, *profiles.SDSS)

     a = profiles.convolve(point, seeing, defocus)


Simplest use of a generic sampler is just creating many point profiles at
different heights as seen by SDSS:

.. code-block:: python

     from lfd.analysis import profiles
     points = profiles.generic_sampler(profiles.PointSource, profiles.HEIGHTS)

A more complicated use case would be creating disk profilse of different radii
at many different seeings FWHMs and heights as seen by SDSS:

.. code-block:: python

     from lfd.analysis import profiles
     disks = profiles.generic_sampler(profiles.DiskSource,
                                      radius = (1, 2, 3),
                                      seeingFWHM=profiles.SEEINGS,
                                      h = profiles.HEIGHTS)

By default the generic sampler would return the actual profiles but it can also
return a strucutred array containing all information pertinent  (used profiles,
instrument, height radius, FWHM measurements etc...) to the created
profiles instead:

.. code-block:: python

     from lfd.analysis import profiles
     disks = profiles.generic_sampler(profiles.DiskSource,
                                      radius = (1, 2, 3),
                                      seeingFWHM=profiles.SEEINGS,
                                      h = profiles.HEIGHTS,
                                      returnType="grid")

As well as convenient functionality to convert the retrieved structured arrays
into something easily plottable with matplotlib for example (see meshgrid). 
"""


from lfd.analysis.profiles.utils import *
from lfd.analysis.profiles.seeing import *
from lfd.analysis.profiles.consts import *
from lfd.analysis.profiles.samplers import *
from lfd.analysis.profiles.defocusing import *
from lfd.analysis.profiles.convolution import *
from lfd.analysis.profiles.objectprofiles import *
from lfd.analysis.profiles.convolutionobj import ConvolutionObject

