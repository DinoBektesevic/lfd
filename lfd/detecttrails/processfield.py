"""Processfield is the image analysis workhorse module behind detecttrails. It
contains all the functionality required to detect lines independend of the
source of data, only the ingoing format and type.

Wrapping the functionality in this module for various different catalog and
image sources so that the correct order of operations is ensured for different
directory structures is what makes detecttrails capable of processing variety
of different images.
"""
import cv2
import numpy as np
import os as os


__all__ = ["process_field_bright", "process_field_dim", "pathBright"]


pathBright = None
pathDim = None


def setup_debug():
    """Sets up the module global variables - paths to where the debug output is
    saved. Invoked when 'debug' key is set to True for any of the detection
    steps. Generally there would be no need to call this function otherwise.
    """
    try:
        global pathBright
        global pathDim
        pathBright = os.environ["DEBUG_PATH"]
        pathDim = os.environ["DEBUG_PATH"]
    except KeyError:
        pass


def check_theta(hough1, hough2, navg, dro, thetaTresh, lineSetTresh, debug):
    """
    Comapres colinearity between lines in each set of lines provided and
    between the two sets. If the lines in each set are nearly parallel and the
    two sets are nearly parallel and if the lines are intersecting the x axis
    at nearly the same point then they are nearly colinear.

    .. warning::

       Function returns True when a test is satisfied - this means that the
       lines are not colinear.

    Calculates the difference between max and min angle values of each set of
    fitted lines. If these diffs. are larger than thetaTresh, returns True.

    .. code-block:: python

       dtheta = abs(theta.max()-theta.min())
       if  dtheta2> theta_tresh:  return True

    Difference of averages of angles in both sets are compared with
    linesetTresh. If the diff. is larger than linesetTresh a True is returned.

    .. code-block:: python

       dtheta = abs(numpy.average(theta1-theta2))
       if numpy.average(dtheta)> lineset_tresh: return True

    If the average x axis intersection of the two line sets are not close
    enough True is returned

    .. code-block:: python

        if abs(np.average(ro1)-np.average(ro2))>dro: return True

    Parameters
    ----------
    hough1 : cv2.HoughLines
        2D array of line parameters representing the first set of lines that
        will be compared. Line parameters are stored as tuples, i.e.
        hough1[0][i] --> tuple(ro, theta)
    hough2 : cv2.HoughLines
        second set of lines to be compared
    navg : int
        number of lines that will be averaged together
    thetaTresh : float
        treshold, in radians, that each line set must not be bigger than
    linesetTresh : float
        treshold, in radians, that the difference of the two line sets should
        not be bigger than.
    debug : bool
        produces a verboose output of calculated values.
    """
    ro1 = np.zeros((navg, 1))
    ro2 = np.zeros((navg, 1))
    theta1 = np.zeros((navg, 1))
    theta2 = np.zeros((navg, 1))
    for i in range(0, navg):
        try:
            # changed with opencv 3, the shape is (N, 1, 2) where N is number
            # of detected lines, 1 is just cause, and 2 for (ro, theta pairs)
            ro1[i] = hough1[i][0][0]
            ro2[i] = hough2[i][0][0]
            theta1[i] = hough1[i][0][1]
            theta2[i] = hough2[i][0][1]
        except IndexError:
            pass

    if debug:
        print("RO:"
              f"Ro_tresh:    {dro}\n"
              "  PROCESSED IMAGE:\n"
              f"    ro1:    {ro1.tolist()}\n"
              f"    avg(ro1):    {np.average(ro1)}\n"
              "  MINAREARECT IMAGE:\n"
              f"    ro2:    {ro2.tolist()}\n"
              f"    avg(ro2):    {np.average(ro2)}\n"
              "------------------------------------------\n"
              f"avg1 - avg2 =    {abs(np.average(ro1) - np.average(ro2))}")

    if abs(np.average(ro1) - np.average(ro2)) > dro:
        if debug:
            print("Ro test:    FAILED")
        return True

    if debug:
        print("\nTHETA:"
              f"Theta_tresh:     {thetaTresh}\n"
              f"Lineset_tresh:   {lineSetTresh}\n"
              "  PROCESSED IMAGE: \n"
              f"    theta1:    {theta1.tolist()}\n"
              f"    max1 - min1:     {abs(theta1.max() - theta1.min())}"
              "  MINAREARECT IMAGE:\n"
              f"    theta2:    {ro2.tolist()}\n"
              f"    max2 - min2:    {abs(theta2.max() - theta2.min())}\n"
              "------------------------------------------\n"
              f"Avg(theta)1 - theta2) =    {abs(np.average(theta1 - theta2))}")

    dtheta1 = abs(theta1.max() - theta1.min())
    if dtheta1 > thetaTresh:
        if debug:
            print("Theta1 tresh test:    FAILED")
        return True

    dtheta2 = abs(theta2.max() - theta2.min())
    if dtheta2 > thetaTresh:
        if debug:
            print("Theta2 tresh test:    FAILED")
        return True

    dtheta = abs(theta1 - theta2)
    if np.average(dtheta) > lineSetTresh:
        if debug:
            print("Lineset tresh test:    FAILED")
        return True


def draw_lines(hough, image, nlines, name, path=pathDim,
               compression=0, color=(255, 0, 0)):
    """
    Draws hough lines on a given image and saves it as a png.

    Parameters
    ----------
    hough : cv2.HoughLines
        2D array of line parameters, line parameters are stored in [0][x] as
        tuples.
    image : np.array or cv2.image
        image will now be altered
    nlines : int
        number of lines to draw
    name : str
        name of the file without extension
    path : str
        the path will be set by default when DetectTrails debug params are set
        to True. Otherwise supply your own.
    compression : int
        cv2.IMWRITE_PNG_COMPRESSION parameter from 0 to 9. A higher value means
        a smaller size and longer compression time. Default value is 0.
    """
    n_x, n_y = image.shape
    # convert to color image so that you can see the lines
    draw_im = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    for houghparams in hough[:nlines]:
        try:
            rho, theta = houghparams[0]
            x0 = np.cos(theta) * rho
            y0 = np.sin(theta) * rho
            pt1 = (
                int(x0 - (n_x + n_y) * np.sin(theta)),
                int(y0 + (n_x + n_y) * np.cos(theta))
            )
            pt2 = (
                int(x0 + (n_x + n_y) * np.sin(theta)),
                int(y0 - (n_x + n_y) * np.cos(theta))
            )
            cv2.line(draw_im, pt1, pt2, color, 2)
        except Exception:
            pass

    cv2.imwrite(os.path.join(path, name+".png"), draw_im,
                [cv2.IMWRITE_PNG_COMPRESSION, compression])


def fit_minAreaRect(img, contoursMode, contoursMethod, minAreaRectMinLen,
                    lwTresh, debug):
    """
    Fits minimal area rectangles to the image. If no rectangles can be
    fitted it returns False. Otherwise returns True and an image with drawn
    rectangles.

    1. finds edges using canny edge detection algorithm
    2. finds all contours among the edges
    3. fits a min. area rectangle to a contour only if:

        a. both sides of the rect. are longer than minAreaRectMinLen
        b. the ratio of longer vs, shorter rect. side is smaller than lwTresh

    5. if no rectangles satisfying sent conditions are found function returns
    False and an empty (black) image

    For more details on the parameters see documentation.

    Parameters
    ----------
    img : np.array
        numpy array representing gray 8 bit 1 chanel image.
    lwTresh : float
        ratio of longer/shorter rectangle side that needs to be satisfied
    contoursMode : cv2.const
        cv2.RETR_LIST should be used, but any of the contour return modes
    contoursMethod : cv2.const
        cv2.CHAIN_APPROX_NONE should be used, but any of the contour return
        modes supported by OpenCV can be used
    minAreaRectMinLen : int
        length, in pixels, of allowed shortest side to be fitted to contours
    """
    detection = False
    box_img = np.zeros(img.shape, dtype=np.uint8)
    canny = cv2.Canny(img, 0, 255)

    # in in cv2.8something it was contours, hierarchy
    # then in 3 it was image, contours, hierarchy, and
    # then in 4.0 it's again contours, hierarchy....
    try:
        contoursimg, contours, hierarchy = cv2.findContours(canny, contoursMode,
                                                            contoursMethod)
    except ValueError:
        contours, hierarchy = cv2.findContours(canny, contoursMode,
                                               contoursMethod)

    for cnt in contours:
        rect = cv2.minAreaRect(cnt)
        if (rect[1][0] > rect[1][1]):
            length = rect[1][0]
            width = rect[1][1]
        else:
            width = rect[1][0]
            length = rect[1][1]
        if (length > minAreaRectMinLen) and (width > minAreaRectMinLen):
            if (length/width > lwTresh):
                detection = True
                box = cv2.boxPoints(rect)
                box = np.asarray(box, dtype=np.int32)
                cv2.fillPoly(box_img, [box], (255, 255, 255))

    return detection, box_img


def dictify_hough(shape, houghVals):
    """Function converts from hough line tuples (rho, theta) into a dictionary
    of pixel coordinates on the image.

    Parameters
    ----------
    shape : tuple, list
        shape (dimensions) of the image. Used in order to scale Hough-space
        coordinates into pixel-space coordinates
    houghVals : tuple, list
        (rho, theta) values of lines
    """
    rho, theta = houghVals
    n_x, n_y = shape

    x0 = np.cos(theta) * rho
    y0 = np.sin(theta) * rho
    x1 = int(x0 - (n_x + n_y) * np.sin(theta))
    y1 = int(y0 + (n_x + n_y) * np.cos(theta))
    x2 = int(x0 + (n_x + n_y) * np.sin(theta))
    y2 = int(y0 - (n_x + n_y) * np.cos(theta))

    return {"x1": x1, "y1": y1, "x2": x2, "y2": y2}


def process_field_bright(img, lwTresh, thetaTresh, dilateKernel, contoursMode,
                         contoursMethod, minAreaRectMinLen, houghMethod,
                         nlinesInSet, lineSetTresh, dro, debug):
    """
    Function detects bright trails in images. For parameters explanations see
    DetectTrails documentation for help.

    1.  pixels with values bellow minFlux are set to 0
    2.  Scale the image to 8 bit integer, 1 channel
    3.  histogram equalization
    4.  dilate to expand features
    5.  fit minimal area rectangles. Function aborts if no
        minAreaRect are found, see: fit_minAreaRect help
    6.  fit Hough lines on image and on found rectangles
    7.  compare lines, see: check_theta help
    8. if evaluation passed write the results into file and return
       True, else returns False.

    Parameters
    ----------
    img : np.array
        numpy array representing gray 32 bit 1 chanel image.
    lwTresh : float
        treshold for the ratio of rectangle side lengths that has to be
        satistfied
    thetatresh : float
        treshold for the difference of angles, in radians, that each fitted set
        of lines has to satisfy
    dilateKernel : np.array
        kernel used to dilate the image
    contoursMode : cv2.const
        cv2.RETR_LIST should be used, but any return type of fitted contours
        supported by OpenCV is allowed
    contoursMethod : cv2.const
        cv2.CHAIN_APPROX_NONE should be used, but any return type of fitted
        contours supported by OpenCV is allowed
    minAreaRectMinLen : int
        treshold for minimal allowed length of fitted minimal area rectangles
    houghMethod : int
        treshold for minimum number of votes lines need to get in Hough space
        to be returned
    nlinesInSet : int
        number of most voted for lines that will be considered for colinearity
        tests
    lineSetTresh : float
        treshold for maximal allowed angle deviation between two sets of fitted
        lines
    dro : int
        treshold for maximal allowed distance between the average x-axis
        intersection coordinates of the two sets of lines
    """
    img[img < 0] = 0

    # FITS files are usually 1 channel 32 bit float images, we need
    # 1 channel 8 bit int images for OpenCV
    gray_image = cv2.convertScaleAbs(img)
    equ = cv2.equalizeHist(gray_image)

    if debug:
        cv2.imwrite(os.path.join(pathBright, "1equBRIGHT.png"), equ,
                    [cv2.IMWRITE_PNG_COMPRESSION, 3])
        print("BRIGHT: saving EQU with removed stars")

    equ = cv2.dilate(equ, dilateKernel)

    if debug:
        cv2.imwrite(os.path.join(pathBright, "2dilateBRIGHT.png"), equ,
                    [cv2.IMWRITE_PNG_COMPRESSION, 3])
        print("BRIGHT: saving dilated image.")

    detection, box_img = fit_minAreaRect(equ, contoursMode, contoursMethod,
                                         minAreaRectMinLen, lwTresh, debug)

    if debug:
        cv2.imwrite(os.path.join(pathBright, "3contoursBRIGHT.png"), box_img,
                    [cv2.IMWRITE_PNG_COMPRESSION, 3])
        print("BRIGHT: saving contours")

    if detection:
        equhough = cv2.HoughLines(equ, houghMethod, np.pi/180, 1)
        boxhough = cv2.HoughLines(box_img, houghMethod, np.pi/180, 1)

        if debug:
            draw_lines(equhough, equ, nlinesInSet, "5equhoughBRIGHT",
                       path=pathBright)
            draw_lines(boxhough, box_img, nlinesInSet, "4boxhoughBRIGHT",
                       path=pathBright)
            print("BRIGHT!")

        if check_theta(equhough, boxhough, nlinesInSet, dro, thetaTresh,
                       lineSetTresh, debug):
            return (False, None)
        else:
            return (True, dictify_hough(equ.shape, equhough[0][0]))
    else:
        if debug:
            print("BRIGHT: no boxes found")
        return (False, None)


def process_field_dim(img, minFlux, addFlux, lwTresh, thetaTresh, erodeKernel,
                      dilateKernel, contoursMode, contoursMethod,
                      minAreaRectMinLen, houghMethod, nlinesInSet,
                      dro, lineSetTresh, debug):
    """
    Function detects dim trails in images. See DetectTrails documentation for
    more detailed explanation of parameters

    1.  pixels with values bellow minFlux are set to 0
    2.  addFlux is added to remaining pixels
    3.  Scale the image to 8 bit 1 chanel
    4.  histogram equalization
    5.  erode to kill noise
    6.  dilate to expand features that survived
    7.  fit minimal area rectangles. Function aborts if no minAreaRect are
        found, see: fit_minAreaRect help
    8.  fit Hough lines on image and on found rectangles
    9.  compare lines, see: help(check_theta)
    10. if evaluation passed write the results into file and return True, else
        returns False.


    Parameters
    ----------
    img : np.array
        numpy array representing gray 32 bit 1 chanel image.
    minFlux : float
        treshold for maximal allowed pixel brightness value under which pixel
        values will be set to zero
    addFlux : float
        the brightness that will be added to all pixels above minFlux
    lwTresh : float
        treshold for the ratio of rectangle side lengths that has to be
        satistfied
    thetatresh : float
        treshold for the difference of angles, in radians, that each fitted set
        of lines has to satisfy
    dilateKernel : np.array
        kernel used to erode the image
    dilateKernel : np.array
        kernel used to dilate the image
    contoursMode : cv2.const
        cv2.RETR_LIST should be used, but any return type of fitted contours
        supported by OpenCV is allowed
    contoursMethod : cv2.const
        cv2.CHAIN_APPROX_NONE should be used, but any return type of fitted
        contours supported by OpenCV is allowed
    minAreaRectMinLen : int
        treshold for minimal allowed length of fitted minimal area rectangles
    houghMethod : int
        treshold for minimum number of votes lines need to get in Hough space
        to be returned
    nlinesInSet : int
        number of most voted for lines that will be considered for colinearity
        tests
    lineSetTresh : float
        treshold for maximal allowed angle deviation between two sets of fitted
        lines
    dro : int
        treshold for maximal allowed distance between the average x-axis
        intersection coordinates of the two sets of lines
    """
    img[img < minFlux] = 0
    img[img > 0] += addFlux

    gray_image = cv2.convertScaleAbs(img)
    equ = cv2.equalizeHist(gray_image)

    if debug:
        print("DIM: saving EQU with stars removed")
        cv2.imwrite(os.path.join(pathDim, "6equDIM.png"), equ,
                    [cv2.IMWRITE_PNG_COMPRESSION, 0])

    opening = cv2.erode(equ, erodeKernel)

    if debug:
        print("DIM: saving eroded EQU with stars removed")
        cv2.imwrite(os.path.join(pathDim, '7erodedDIM.png'), opening,
                    [cv2.IMWRITE_PNG_COMPRESSION, 0])

    equ = cv2.dilate(opening, dilateKernel)

    if debug:
        print("DIM: saving dilated eroded EQU with stars removed")
        cv2.imwrite(os.path.join(pathDim, '8openedDIM.png'), equ,
                    [cv2.IMWRITE_PNG_COMPRESSION, 0])

    detection, box_img = fit_minAreaRect(equ, contoursMode,
                                         contoursMethod,
                                         minAreaRectMinLen, lwTresh,
                                         debug)
    if debug:
        cv2.imwrite(os.path.join(pathDim, "9contoursDIM.png"), box_img,
                    [cv2.IMWRITE_PNG_COMPRESSION, 0])
        print("DIM: saving contours")

    if detection:
        equhough = cv2.HoughLines(equ, houghMethod, np.pi/180, 1)
        boxhough = cv2.HoughLines(box_img, houghMethod, np.pi/180, 1)

        if debug:
            draw_lines(equhough, equ, nlinesInSet, "10equhoughDIM",
                       compression=4, path=pathDim)
            draw_lines(boxhough, box_img, nlinesInSet, "11boxhoughDIM",
                       compression=4, color=(0, 0, 255), path=pathDim)
            print("DIM!")

        if check_theta(equhough, boxhough, nlinesInSet, dro, thetaTresh,
                       lineSetTresh, debug):
            return (False, None)
        else:
            return (True, dictify_hough(equ.shape, equhough[0][0]))
    else:
        if debug:
            print("DIM: FALSE AT NO RECTANGLES MATCHING THE CONDITIONS FOUND!")
        return (False, None)
