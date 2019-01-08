"""
This module contains all the basic functionality required to execute the linear
feature detector interactively or in a sequential batch-like processing setup.
The module requires that all the required data exists and is linked to by the
following environmental variables:

* BOSS - the 'boss' dir which usually contains both 'photo' and 'photoObj' dirs
* BOSS_PHOTOOBJ - if the 'photoObj' directory is stored in a different location
    this can be overwritten to point to that location. In combination with
    PHOTO_REDUX, can be used to almost completely customize the data layout.
* PHOTO_REDUX - if the 'photo' directory is not in BOSS this should point to
    new location instead. The required files are 'photoRunAll' and 'runList'
    which should live inside the sub-directory 'redux'.

These variables should be set manually prior to importing the module or
post-import by calling the package setup function (i.e. detecttrails.setup).

Central construct of this module is the DetectTrails class which keeps track of
the execution parameters and targeted data on which to run detection on. On its
exact usage see help(DetectTrails). It is instructive to read the docstring of
process_field function to see th steps algorithm takes. For its exact
implementation see processfield module of the package.

The detection algorithm can be used to run on other sources of data given that
the images are in FITS format and that the catalog for each image is also given
as a header table of a FITS file. There should be one such fits catalog per
image and it should follow the naming convention adopted by SDSS
(i.e. 'photoObj...')..
Other catalog sources can also be used but not implemented. See removestars
module on several examples of old deprecated catalog functionality and how
different source catalogs could be adopted and used instead of SDSS catalog.

  Usage
---------
DetectTrails(run= , camcol={1-6}, field={all}, filter={ugriz})

    Defines a convenience class that holds various execution
    parameter and processes SDSS fields selected by various
    init parameters:
        foo = DetectTrails(run=2888)
        foo = DetectTrails(camcol=1)
        foo = DetecTrails(filter="i")
        foo = DetectTrails(run=2888, camcol=1)
        foo = DetectTrails(run=2888, camcol=1, filter='i')
        foo = DetectTrails(run=2888, camcol=1, filter='i', field=139)
    At least 1 keyword has to be sent!

    Broadly speaking the detection is a three step process:
    * Removal of all known objects
    * Detection of bright linear features
    * Detection of dim linear features.
    Each step is individually configurable through the 'params_<step>' dict of
    detection/execution parameters. For example, changing detection parameters:
        foo.params_removestars["pixscale"] = 10
        foo.params_bright["lwTresh"] = 5
        foo.params_dim["minFlux"] = 1

    See Exec params section for full list of execution/detection parameters and
    their explanation. A special 'debug' key can be set to True for any of the
    individual steps of the algorithm which will produce a very verbose output
    to stdout as well as save snapshots of the processed image in intermediate
    steps to a location pointed to by DEBUG_PATH environmental variable.
        foo.params_dim["debug"] = True
    By default all debugs are set to false. If 'debug' keyword is supplied at
    instantiation time all 'debug' values will be set to the supplied value.

    To start the detection process call the process method:
        foo.process()
    Some of the data selection above select as much as 1/5th of all existing
    SDSS images which can lead to very long execution times so care is advised.

      Exec params:
    ################
        params_bright
      -----------------
          dilateKernel: np.ones((4,4), np.uint8)
              Kernel that dilates the image before processing.
          countoursMode: cv2.RETR_LIST
              See OpenCV documentation for findContours. By default
              all edges are returned.
          contoursMethod: cv2.CHAIN_APPROX_NONE (see OpenCV Canny help)
              All edge points are returned without any approximations.
          minAreaRectMinLen: 1
              Once contours have been returned minimal area rectangles are
              fitted. Length of its sides are determined. If either side is
              shorter than minAreaRectMinLen value, in pixels, the detection is
              dismissed.
          lwTresh: 5
              ratio that longer/shorter rectangle side has to satisfy to be
              considered a possibly valid detection.
          houghMethod: 20 (see OpenCV Hough help)
              Minimal number of votes required in Hough space to be considered
              a valid line
          nlinesInSet: 3
              Hough trans. returns a list of all possible lines, only the top
              voted nlinesInSet number of lines are taken into consideration
              for consistency checks. This is called a "set" of lines because
              one set is fitted to the raw image and the other to the
              rectangles on the "reconstructed" image.
          thetaTresh: 0.15 (angle in radians)
              if within a single set the dispersion of maximal-minimal theta is
              larger than thetaTresh, detection is dismissed as False.
          linesetTresh: 0.15 (angle in radians)
              if both line sets pass thetaTresh, but their respective average
              theta's are larger than linesetTresh detection is dismissed.
          dro: 20 (distance in pixels)
              if r averages of both Hough line sets are larger than dro then
              detection is dismissed as false.
          debug: False
              verboose output of steps including saving image snapshots:
              1) equBRIGHT      - equalized 8bit int image with known objects
                                  masked out
              2) dilateBRIGHT   - equalized and dilated image
              3) contoursBRIGHT - rectangles that pass the tests are drawn
                                  on the image
              4) boxhoughBRIGHT - rectangles with corresponding fitted lines
                                  (set 1)
              5) equhoughBRIGHT - processed image with second set of fitted lines
                                  (set 2)
              Errors are printed to standard out but still silenced. Images are
              saved to the DEBUG_PATH environmental folder

        params_dim
      -----------------
          minFlux: 0.02
              for BRIGHT processing, all negative values are set to 0 before
              processing. For dim processing, all values of pixel brighteness
              above minFlux are set to zero. This is an educated guess of the
              noise-ceiling in the image.
          addFlux: 0.5
              value added to all remaining pixels with values still above 0.
              This is equivalent to brightness increase.
          erodeKernel: np.ones((3,3), np.uint8)
              image is eroded to destroy noise (defined as isolated pixels).
          dilateKernel: np.ones((9,9), np.uint8)
              image is dilated to restore features.
          countoursMode: cv2.RETR_LIST (see above)
          contoursMethod: cv2.CHAIN_APPROX_NONE (see above)
          minAreaRectMinLen: 1 (see above)
          lwTresh: 5 (see above)
          houghMethod: 1 (see above)
          nlinesInSet: 3 (see above)
          thetaTresh: 0.1 (see above)
          linesetTresh: 0.15 (see above)
          dro: 20 (see above)
          debug: False
              The output is similar to debug BRIGHT option with additional
              saved snapshots:
            6)  equDIM      - equ, 8bit img, removed obj. increased brightness
            7)  erodedDIM   - 6 + erosion
            8)  openedDIM   - 7 + dilation (combo. is called opening operator)
            9)  contoursDIM - rectangles that pass the tests
            10) equhoughDIM - processed img with with a set of fitted lines
            11) boxhoughDIM - rectangles image with second set of fitted lines

        params_removestars
      ----------------------
          pixscale: 0.396
            SDSS pixel scale is 0.396 arcseconds/pixel. Used to convert the
            petrosian radius to pixel dimensions.
          defaultxy: 20 (in pixels)
            Half of the length of squares that are drawn over stars. Used if
            there is no petrosian radius availible or if the length/2 of square
            sides are larger than maxxy.
          maxxy: 60 (in pixels)
            maximal allowed half-length of square side. Maximal covered area on
            the image is therefore 120x120px
          filter_caps: {'u': 22, 'g': 22,'r': 22, 'i':22,'z': 22},
            stars on the image that are dimmer than filter caps will not be
            removed.
          magcount: 3
            maximal allowed number of filters in which magnitude difference is
            larger than maxmagdiff
          maxmagdiff: 3
            max allowed diff. in magnitude between two filters

    To get a better understanding of detection parameters contoursMode/Method,
    minAreaRectMinLen and lwTresh see doc of _fit_minAreaRect in processfield.
    For nlinesInSet, thetaTresh, linesetTresh see _check_theta in processfield.
    For removestars params see doc of remove_stars function in removestars.
    For more details algorithm see process_field_dim and process_field_bright
    functions from process_field module.

  Dependencies
----------------
-numpy, openCV for python, fitsio
-enviroment has to be set up properly. See start.sh file.
-SDSS folder/file structure has to be mirrored.
-To process a single frame following files are needed:
     frame-run-camcol-filter-field.fits.tar.bz2
     photoObj-run-camcol-field.fits
"""

# Make sure these path point to the correct folders
# BOSS       - folder where SDSS data is kept
# SAVE_PATH  - folder where results will be stored
# DEBUG_PATH - folder where images and other debugging files are stored,
#              not mandatory

from lfd import BOSS, BOSS_PHOTOOBJ, PHOTO_REDUX

DEBUG_PATH = None
def setup(bosspath, photoobjpath, photoreduxpath, debugpath):
    """Sets up the required environmental paths for detecttrails module. If
    only BOSS is supplied it is assumed that SDSS conventions are followed and
    that the folder structure resembles:
    boss
      /photo
        /redux
          photoRunAll-dr##.par
          runList.par
      /photoObj
        /301
          /{dirs named by run they belong to}
            /{dirs named 1-5 for camcol}
              /photoObj-{paddded run}-camcol-{padded field}.fits
        /frames
          /301
            /{dirs named by run they belong to}
              /{dirs named 1-5 for camcol}
                /frame-{ugriz}-{padded run}-camcol-{padded field}.fits.bz2

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
    global BOSS, DEBUG_PATH, PHOTO_REDUX, BOSS_PHOTOOBJ
    import os

    # default to expected SDSS locations for all the values that are not sent
    if photoobjpath is None:
        photoobjpath   = BOSS_PHOTOOBJ
    if photoreduxpath is None:
        photoreduxpath = PHOTO_REDUX
    if debugpath is None:
        # default to invocation directory
        debugpath = os.path.abspath(os.path.curdir)

    # declare the env vars
    os.environ["BOSS"]          = bosspath
    os.environ["BOSS_PHOTOOBJ"] = photoobjpath
    os.environ["PHOTO_REDUX"]   = photoreduxpath
    os.environ["DEBUG_PATH"]    = debugpath

    # if the paths were changed through the function call signature, update the
    # global vars here
    BOSS          = bosspath
    DEBUG_PATH    = debugpath
    BOSS_PHOTOOBJ = photoobjpath
    PHOTO_REDUX   = photoreduxpath


from .removestars import *
from .processfield import *
from .detecttrails import *
