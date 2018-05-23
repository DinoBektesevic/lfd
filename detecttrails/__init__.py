"""
Package:
    detecttrails
Modules:
    sdss          --isn't explicitly imported
    detect_trails --DetectTrails class is explicitly imported
    process_field --isn't explicitly imported


  Classes:
-------------
DetectTrails(run= , camcol={1-6}, field={all], filter={ugriz})

    Defines a convenience class that holds various execution
    parameter and processes SDSS fields selected by various
    init parameters
    I.e.
        foo = DetectTrails(run=2888)
        foo = DetectTrails(run=2888, camcol=1)
        foo = DetectTrails(run=2888, camcol=1, filter='i')
        foo = DetectTrails(run=2888, camcol=1, filter='i', field=139)

    It is also possible to change detection/execution parameters
    of class object foo:
        foo.params_bright["debug"] = True
        foo.params_removestars["filter_caps"]["i"] = 20
    See Exec params for full list of execution/detection parameters and
    their explanation.

    To start the detection process call for the process method:
        foo.process()

      Exec params:
    -----------------
        results: file that stores results as txt file
                 with following order:
                     run field camcol filter tai crpix1 \\nonewline
                     crpix2 crval1 crval2 cd1_1 cd1_2 \\nonewline
                     cd2_1 cd2_2 x1 x2 y1 y2 \\n
                 Set to "results.txt" by default

        errors: file that stores execution errors as txt file.
                Errors are formatted as:
                    run,camcol,field,filter
                    TRACEBACK (3 stacks deep)
                    Error message of 1st stack.

        kwargs: filled in by run camcol filter field parameters.

        Following parameters influence detection sensitivity.
        They are listed here with their default values.

        params_bright = {
            "dilateKernel": np.ones((4,4), np.uint8)
                Kernel that dilates the image before processing.
            "countoursMode": cv2.RETR_LIST
                See OpenCV documentation for findContours. By default
                all edges are returned.
            "contoursMethod": cv2.CHAIN_APPROX_NONE
                See OpenCV documentation for Canny. By default edges
                aren't being approximated but returned as is.
            "minAreaRectMinLen": 1
                Once contours have been returned minimal area
                rectangles are fitted. Length of sides is determined.
                If either side is shorter than this value, in pixels,
                rectangle is dismissed as faulty and isn't drawn.
            "lwTresh": 5
                limiting ratio of lengths of sides, such that
                l is always the longer side. If the ratio is less
                than lwTresh minAreaRect isn't drawn.
            "houghMethod": 1
                Pick a hough method of fit. This is a remnant of old
                OpenCV and has no impact today.
            "nlinesInSet": 3
                Defines number of fitted lines that are taken into
                account for averaging when thetaTresh is checked.
            "thetaTresh": 0.15
                in radians. nlinesInSet lines are averaged by their
                thetas, if either set of lines excedes thetaTresh
                detection is dismissed as false.
            "linesetTresh": 0.15
                If both Hugh lines (reconstructed and processed img)
                sets pass the thetaTresh, but their respective theta
                averages are larger than linesetTresh detection is
                dismissed as false.
            "dro": 20
                If r averages of both Hough lines sets (reconstructed
                and processed img) are larger than dro then detection
                is dismissed as false.
            "debug": False
                verboose output of various steps is/n't done,
                including saving various processed images:
                1) equBRIGHT - equalized image for BRIGHT
                2) contoursBRIGHT - drawn minAreaRect that pass the lw
                                    tests for BRIGHT
                3) equhoughBRIGHT - nlinesInSet hough lines drawn on 1
                4) boxhoughBRIGHT - nlinesInSet hough lines on 2
                5) equDIM - equalized image for DIM
                6) erodedDIM - eroded 5)
                7) openedDIM - dilated 6)
                8) contoursDIM - drawn minAreaRect that pass the lw
                                 tests for DIM
                9) equhoughDIM - nlinesInSet hough lines drawn on 7
               10) boxhoughDIM - nlinesInSet hough lines drawn on 8

                Errors are printed to standard out but still silenced.
                Images are saved to pathBright and pathDim paths defined
                in global processfield vars.
            }

        params_dim = {
            "minFlux": 0.02
                for bright processing, all negative values are set to
                0 before processing. For dim processing, all values of
                pixel brighteness above minFlux are set to zero.
            "addFlux": 0.5
                is added to all remaining pixels with brightness value
                above 0. This increases brightness and contrast.
            "erodeKernel": np.ones((3,3), np.uint8)
                image is eroded to destroy noise.
            "dilateKernel": np.ones((9,9), np.uint8)
                image is dilated to restore image features.
            "countoursMode": cv2.RETR_LIST
            "contoursMethod": cv2.CHAIN_APPROX_NONE
            "minAreaRectMinLen": 1
            "lwTresh": 5
            "houghMethod": 1, #CV_HOUGH_STANDARD
            "nlinesInSet": 3,
            "thetaTresh": 0.15
            "linesetTresh": 0.15,
            "dro": 20,
            "debug": False
            }

        params_removestars = {
            "pixscale": 0.396,
                SDSS pixel scale is 0.396 arcseconds/pixel. Used to
                convert the petrosian radius to pixel dimensions.
            "defaultxy": 20,
                Half of the length, in pixels, of the side of a square
                that is drawn over stars. Used if there is no petro.
                radius or if the half-length of square side is larger
                than maxxy.
            "maxxy": 60,
                maximal allowed half-length of square side. Maximal
                covered area on the image is 120x120px.
            "filter_caps": {'u': 22, 'g': 22,'r': 22, 'i':22,'z': 22},
                stars on the image that are dimmer than filter caps
                will not be removed.
            "magcount": 3,
                maximal allowed number of filters in which magnitude
                difference is larger than maxmagdiff
            "maxmagdiff": 3,
                max allowed diff. in magnitude between two filters
            }

    To get a better understanding of detection parameters
    contoursMode/Method, minAreaRectMinLen and lwTresh see doc of
    _fit_minAreaRect in processfield. For nlinesInSet, thetaTresh,
    linesetTresh see _check_theta in processfield. To get a better
    understanding of removestars params see doc of RemoveStars
    function in removestars.
    For an more detailed algorithm see process_field_dim and
    process_field_bright from process_field module.

  Functions:
--------------
process_field(results, errors, run, camcol, filter, field,
              params_bright, params_dim)

  Dependencies:
-------------
-numpy, openCV for python, fitsio
-enviroment has to be set up properly. See start.sh file.
-SDSS folder/file structure has to be mirrored.
-To process a single frame following files are needed:
     frame-run-camcol-filter-field.fits.tar.bz2
     photoObj-run-camcol-field.fits
"""

import sys as _sys

#try:
from   .detecttrails import DetectTrails
#import .processfield as _processfield
#import .removestars as _removestars
#import .sdss as _sdss
#except:
#    _sys.stderr.write("DetectTrails not imported.\n")
#del removestars, processfield, sdss, detecttrails
