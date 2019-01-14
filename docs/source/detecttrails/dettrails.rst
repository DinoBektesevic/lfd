.. lfd documentation master file, created by
   sphinx-quickstart on Tue Jan  8 13:18:57 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Linear Feature detection
========================


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   detparams
   dtexamples
   paramsremovestars
   paramsbright
   paramsdim
   rmvstars
   detecttrails
   processfield


.. tip::

 Description of the algorithm's implementation, execution parameters and performance
 is availible in

   Bektesevic & Vinkovic, 2017, Linear feature detection algorithm for astronomical surveys - I. Algorithm description

 availible at arxiv.org/abs/1612.04748

.. automodule:: lfd.detecttrails

The :class:`~lfd.detecttrails.DetectTrails` is not SDSS data agnostic but the
processing functionality in :mod:`lfd.detecttrails.processfield` is. That way
this module can be used to run on other data given that the images are in FITS
format and that the catalog for each image is also given as a header table of a
FITS file. There should be one such fits catalog per image.             
Other catalog sources are possible but not impemented. It is instructive to see
:mod:`~lfd.detecttrails.removestars` module which should contain examples of
old deprecated CSV catalog functionality.
