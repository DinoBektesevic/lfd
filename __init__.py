"""
Linear Feature Detector (LFD) library is a collection of packages that enable
users to detect and analyze linear features on SDSS images. LFD was designed to
run interactively or at scale on a cluster that uses a PBS scheduler/workload
manager. Appart from the linear feature detection algorithm, the detecttrails
package, the library contains additional packages that createjobs package that
helps with creating and managing PBS jobs, results package for result analysis,
a GUI interface that can facilitate job creation and visual inspection of the
results, a package for on-scale execution error management and a series of
common case plotting tools are provided.

Some of the LFD packages require that additional data is exists and is
availible. For example, the module containing the SDSS data requires that the
data exists localy and that it follows the SDSS organisational conventions.
These paths ca be set manually prior to using detecttrails or they can be set
up post-import by invoking the setup function in the module itself or the
setup_<package> function from LFD library.
For more details on prerequisites see that package help.

  Dependencies
----------------
* Python 3+
* OpenCv 3+
* fitsio 0.9+
* numpy
* SqlAlchemy
* Astropy

Erin Sheldon's SDSS utilities come bundled with the provided code.
"""
import os as _os
from .createjobs import *

def setup_detecttrails(bosspath = _os.path.join(_os.path.expanduser("~"),
                                                "Desktop/boss"),
                       photoobjpath = None,
                       photoreduxpath = None,
                       debugpath = None):
    """Sets up the environmental paths BOSS, BOSS_PHOTOOBJ, PHOTO_REDUX and
    DEBUG_PATH required for detecttrails package.

      Parameters
    --------------
    bosspath : The path to which BOSS environmental variable will be set to.
        This should be the "boss" home folder within which all SDSS data should
        live.
    photoobjpath : The path to which BOSS_PHOTOOBJ env. var. will be set to.
        If only bosspath is supplied it will default to BOSS/photoObj but is
        configurable in the case SDSS conventions are not followed.
    photoreduxpath : The path to which PHOTO_REDUX env. var. will be set to.
        If only bosspath is suplied it will default to BOSS/photoObj but is
        left configurable if SDSS conventions are not followed.
    debugpath : The path to which DEBUG_PATH env. var. will be set to. It can
        be left as None in which case it will default to the current directory.
        See detecttrails help to see how to turn on debug mode, not used by
        default.
    """
    from . import detecttrails
    detecttrails.setup(bosspath, debugpath, photoobjpath, photoreduxpath)


def setup_db(URI="sqlite:///", dbpath="~", name="foo.db", echo=False):
    """Either connects to an existing DB (that has to be mappable by results
    package) or creates a new empty DB with the required tables.

      Parameters
    --------------
    URI : an URI to the DB. By default 'sqlite:///$USER_HOME/food.db' is  used.
    dbpath : location of a directory with an existing DB, or a directory where
        a new DB will be saved. Set to users home folder by default.
    name : the name of the existing, or newly created, DB. Default: 'foo.db'
    echo : verbosity of the DB. True by default.
    """
    from os import path
    from . import results

    dbpath = path.expanduser(dbpath)
    db_uri = path.join(URI+dbpath, name)
    results.connect2db(uri=db_uri, echo=echo)

