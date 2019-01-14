""" Linear Feature Detector (LFD) library is a collection of packages that
enable users to detect and analyze linear features on astronomical images. The
code was designed to be run interactively, or at scale on a cluster.

LFD is a more complete version of LFDS that contains all of the never-published
features of LFDS. Except for the linear feature detection code in the
detecttrails module, most of the LFDS code was recoded from scratch and made
compatible with Python 3 and OpenCv 3.0.

While most of the code is flexible enough to be appropriated for use with
various different data sources it's primarily intended to be used to analyize
SDSS images on a Sun Grid Engine (SGE) cluster for the purpose of detecting
meteor streaks. For more details on its application in this area of astronomy
refer to:

Bektesevic & Vinkovic, 2017, MNRAS, 1612.04748, Linear Feature Detection
Algorithm for Astronomical Surveys - I. Algorithm description

Some of the previoulsy unreleased features include GUI interfaces to the PBS
job creation module, a package for colation and analysis of results, a image
browser designed to speed up the verification of results, a package for
calculating and predicting the expected cross section of defocused trails and
other common case plotting and analysis tools are provided.

Dependencies
------------

* Python 3+
* OpenCv 3+
* fitsio 0.9+
* numpy
* SqlAlchemy
* Astropy

Erin Sheldon's SDSS utilities come bundled with the provided code.
"""

import os as _os

BOSS = None
PHOTO_REDUX = None
BOSS_PHOTOOBJ = None


from lfd import detecttrails
from lfd import createjobs
from lfd import gui
from lfd import results

def setup_detecttrails(bosspath=BOSS, photoobjpath=BOSS_PHOTOOBJ,
                       photoreduxpath=PHOTO_REDUX, debugpath=None):
    """Sets up the environmental paths BOSS, BOSS_PHOTOOBJ, PHOTO_REDUX and
    DEBUG_PATH required for detecttrails package.
    Defining custom BOSS, BOSS_PHOTOOBJ and PHOTO_REDUX variables allows data
    not to follow the SDSS convention.

    Parameters
    ----------
    bosspath : str
        The path to which BOSS environmental variable will be set to. This
        is the "boss" top directory. Default is set to ~/Desktop/boss
    photoobjpath : str
        The path to which BOSS_PHOTOOBJ env. var. will be set to. Default is
        $BOSS/photoObj.
    photoreduxpath : str
        The path to which PHOTO_REDUX env. var. will be set to. By default set
        to $BOSS/photo/redux-
    debugpath : str
        The path to which DEBUG_PATH env. var. will be set to. The current dir
        by default. Used to run detecttrails module in debug mode.

    """
    if bosspath is None:
        bosspath = _os.path.join(_os.path.expanduser("~"), "Desktop/boss")
    if photoobjpath is None:
        photoobjpath = _os.path.join(bosspath, "photoObj")
    if photoreduxpath is None:
        photoreduxpath = _os.path.join(bosspath, "photo/redux")
    if debugpath is None:
        # default to invocation directory
        debugpath = _os.path.abspath(_os.path.curdir)

    detecttrails.setup(bosspath, photoobjpath, photoreduxpath, debugpath)


def setup_createjobs(photoreduxpath=None):
    """Sets up the environmental path of PHOTO_REDUX only! Minimum environment
    required for certain createjobs package functionality.

    Parameters
    ----------
    photoreduxpath : str
        The path to which PHOTO_REDUX env. var. will be set to. Defaults to
        '~/Desktop/boss/photoredux'.

    """
    # see if BOSS was set previously and assume SDSS convention
    if (BOSS is not None) and (photoreduxpath is None):
        photoredux = _os.path.join(BOSS, "photo/redux")
    # otherwise assume both the SDSS convention and that BOSS is on ~/Desktop
    if (BOSS is None) and (photoreduxpath is None):
        bosspath = _os.path.join(_os.path.expanduser("~"), "Desktop/boss")
        photoredux = _os.path.join(bosspath, "photo/redux")
    # unless of course photoreduxpath was set manually
    createjobs.setup(photoreduxpath)


def setup_results(URI="sqlite:///", dbpath="~/Desktop", name="foo.db",
                  echo=False):
    """Either connects to an existing DB (that has to be mappable by results
    package) or creates a new empty DB with the required tables.

    Parameters
    ----------
    URI : str
        an URI to the DB. Defaults to 'sqlite:///$USER_HOME/food.db'.
    dbpath : str
        location of a directory with an existing DB, or a directory where
        a new DB will be created. Set to '~' by default.
    name : str
        name of the existing, or newly created, DB. Default: 'foo.db'
    echo : bool
        verbosity, Frue by default.

    """
    dbpath = _os.path.expanduser(dbpath)
    db_uri = _os.path.join(URI+dbpath, name)
    results.connect2db(uri=db_uri, echo=echo)

