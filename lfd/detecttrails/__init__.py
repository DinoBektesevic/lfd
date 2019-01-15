"""
This module contains all the basic functionality required to execute the linear
feature detector interactively or in a sequential batch-like processing setup.

The module requires that all the required data exists and is linked to as
described in the :func:`setup section <lfd.setup_detecttrails>`. 

Central construct of this module is the :class:`~lfd.detecttrails.DetectTrails`
class which keeps track of the execution parameters and targeted data.

Broadly speaking the detection is a three step process:

* Removal of all known objects
* Detection of bright linear features
* Detection of dim linear features.

Each step is individually configurable through the `params` dictionaries of the
class.

It is instructive to read the docstring of
:func:`~lfd.detecttrails.process_field` to see the steps algorithm does. For
its implementation or mode details see :mod:`lfd.detecttrails.processfield`
module of the package.

"""

# Make sure these path point to the correct folders
# BOSS       - folder where SDSS data is kept
# SAVE_PATH  - folder where results will be stored
# DEBUG_PATH - folder where images and other debugging files are stored,
#              not mandatory

import lfd

DEBUG_PATH = None
def setup(bosspath, photoobjpath, photoreduxpath, debugpath):
    """Sets up the required environmental paths for detecttrails module.

      Parameters
    --------------
    bosspath : str
        The path to which BOSS environmental variable will be set to. This is
        the "boss" top level directory.
    photoobjpath : str
        The path to which BOSS_PHOTOOBJ env. var. will be set to.
    photoreduxpath : str
        The path to which PHOTO_REDUX env. var. will be set to.
    debugpath : str
       The path to which DEBUG_PATH env. var. will be set to. Used when debug
       mode is turned on as a pointer to a file where the debug information is
       stored.
    """
    import os

    # declare the env vars
    os.environ["BOSS"]          = bosspath
    os.environ["BOSS_PHOTOOBJ"] = photoobjpath
    os.environ["PHOTO_REDUX"]   = photoreduxpath
    os.environ["DEBUG_PATH"]    = debugpath

    # if the paths were changed through the function call signature, update the
    # global vars here
    lfd.BOSS          = bosspath
    lfd.DEBUG_PATH    = debugpath
    lfd.BOSS_PHOTOOBJ = photoobjpath
    lfd.PHOTO_REDUX   = photoreduxpath


from lfd.detecttrails.removestars import *
from lfd.detecttrails.processfield import *
from lfd.detecttrails.detecttrails import *
