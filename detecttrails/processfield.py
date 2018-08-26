import cv2
import numpy as np
import os as os

pathBright = None
pathDim = None
def setup_debug():
    try:
        global pathBright
        global pathDim
        pathBright = os.environ["DEBUG_PATH"]
        pathDim = pathBright
    except:
        pass

def _check_theta(hough1, hough2, navg, dro, thetaTresh, lineSetTresh, debug):
    """
    See: detecttrails docstring for more clarifications. Intended for comparing
    line angles of hough lines fited on minAreaRect and processed image (equHough).
    Number of lines in each set is navg, navg is determined by nlinesInSet.

    Calculates the difference between max and min angle values of each set of
    fitted lines. If these diffs. of theta's are larger than thetaTresh, function
    returns True. That means that the detection is False!

    dtheta = abs(theta.max()-theta.min())
    if  dtheta2> theta_tresh:  return True

    Differences of averages of angles in both sets are compared with linesetTresh.
    If the difference is larger than linesetTresh a True value is returned. That
    means the detection is False!

    dtheta = abs(numpy.average(theta1-theta2))
    if numpy.average(dtheta)> lineset_tresh:
        return True

    init params.
    -----------------
    Keywords:
        hough1, hough2:
           cv2.HoughLines object. 2D array of line parameters.
           Line parameters are stored in [0][x] as tuples.
           i.e. hough[0][i] --> tuple(ro, theta)
        navg:
           number of lines to to average.
        thetaTresh:
           difference treshold in radians per hough line set.
        linesetTresh:
           difference treshold in radians of the two line sets
        debug:
           produces a verboose output of calculated values.
    """
    ro1 = np.zeros((navg,1))
    ro2 = np.zeros((navg,1))
    theta1 = np.zeros((navg,1))
    theta2 = np.zeros((navg,1))
    for i in range(0, navg):
        try:
            ro1[i] = hough1[0][i][0]
            ro2[i] = hough2[0][i][0]
            theta1[i] = hough1[0][i][1]
            theta2[i] = hough2[0][i][1]
        except:
            pass

    if debug:
        print ("RO: "                                                 )
        print ("Ro_tresh:    ", dro                                   )
        print ("  PROCESED IMAGE: "                                   )
        print ("    ro1:    ", ro1.tolist()                           )
        print ("    avg(ro1):    ", np.average(ro1)                   )
        print ("  MINAREARECT IMAGE: "                                )
        print ("    ro2:    ", ro2.tolist()                           )
        print ("    avg(ro2):    ", np.average(ro2)                   )
        print ("------------------------------------------"           )
        print ("avg1-avg2:    ", abs(np.average(ro1)-np.average(ro2)) )

    if abs(np.average(ro1)-np.average(ro2))>dro:
        if debug: print("Ro test:    FAILED")
        return True


    if debug:
        print ("\nTHETA: "                                                 )
        print ("Theta_tresh:    ", thetaTresh                              )
        print ("Lineset_tresh    ", lineSetTresh                           )
        print ("  PROCESED IMAGE: "                                        )
        print ("    theta1    ", theta1.tolist()                           )
        print ("    max1-min1    ", abs(theta1.max()-theta1.min())         )
        print ("  MINAREARECT IMAGE: "                                     )
        print ("    theta2    ", theta2.tolist()                           )
        print ("    max2-min2    ", abs(theta2.max()-theta2.min())         )
        print ("------------------------------------------"                )
        print ("Average(theta1-theta2):    ",abs(np.average(theta1-theta2)))

    dtheta1=abs(theta1.max()-theta1.min())
    if dtheta1> thetaTresh:
        if debug: print("Theta1 tresh test:    FAILED")
        return True

    dtheta2=abs(theta2.max()-theta2.min())
    if dtheta2> thetaTresh:
        if debug: print ("Theta2 tresh test:    FAILED")
        return True


    dtheta = abs(theta1-theta2)
    if np.average(dtheta)> lineSetTresh:
        if debug: print ("Lineset tresh test:    FAILED")
        return True



def _draw_lines(hough, image, nlines, name, path=pathDim,
                compression=0, color=(255,0,0)):
    """
    For debuging purposes, draw hough lines on a given image and save as png.

    init params.
    -----------------
    Keywords:
        hough:
            cv2.HoughLines object. 2D array of line parameters.
            Line parameters are stored in [0][x] as tuples.
            i.e. hough[0][i] --> tuple(ro, theta)
        image:
            image to draw on. Image will now be altered.
        nlines:
            number of lines to draw.
        name:
            _just_ the name of the file. No ".png".

    Optional:
        path:
            pathDim is set by default. Send as kwarg to change.
        compression:
            cv2.IMWRITE_PNG_COMPRESSION parameter, int from 0 to 9.
            A higher value means a smaller size and longer compression
            time. Default value is 0.
    """
    n_x, n_y=image.shape
    #convert to color image so that you can see the lines
    draw_im = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    for (rho, theta) in hough[0][:nlines]:
        try:
             x0 = np.cos(theta)*rho
             y0 = np.sin(theta)*rho
             pt1 = ( int(x0 + (n_x+n_y)*(-np.sin(theta))),
                     int(y0 + (n_x+n_y)*np.cos(theta)) )
             pt2 = ( int(x0 - (n_x+n_y)*(-np.sin(theta))),
                     int(y0 - (n_x+n_y)*np.cos(theta)) )
             cv2.line(draw_im, pt1, pt2, color, 2)
        except:
            pass

    cv2.imwrite(os.path.join(path, name+".png"), draw_im,
                [cv2.IMWRITE_PNG_COMPRESSION, compression])

def _fit_minAreaRect(img, contoursMode, contoursMethod, minAreaRectMinLen,
                     lwTresh, debug):
    """
    Function fits minimal area rectangles to the image. If no rectangles can be
    fitted it returns False. Otherwise returns True and an image with drawn
    rectangles.

      init params.
    -----------------
    Keywords:
        img:
            numpy array representing gray 8 bit 1 chanel image.
        lwTresh, contoursMode, contoursMethod, minAreaRectMinLen:
            see detecttrails module docstring for more details.

      Function:
    --------------
        1) finds edges using canny edge detection algorithm
        2) finds all contours among the edges
        3) fits a min. area rectangle to a contour only if:
        4) both sides of the rect. are longer than minAreaRectMinLen
           4.1) the ratio of longer vs, shorter rect. side is smaller
                than lwTresh 
        5) if no rectangles satisfying sent conditions are found function
           returns False and an empty (black) image
    """
    detection = False
    box_img = np.zeros(img.shape, dtype=np.uint8)
    canny = cv2.Canny(img, 0, 255)

    contoursimg, contours, hierarchy = cv2.findContours(canny, contoursMode,
                                                        contoursMethod)

    boxes = list()
    for cnt in contours:
        rect = cv2.minAreaRect(cnt)
        if (rect[1][0]>rect[1][1]):
            l = rect[1][0]
            w = rect[1][1]
        else:
            w = rect[1][0]
            l = rect[1][1]
        if l>minAreaRectMinLen and w>minAreaRectMinLen:
            if (l/w>lwTresh):
                detection = True
                box = cv2.boxPoints(rect)
                box = np.asarray(box, dtype=np.int32)
                cv2.fillPoly(box_img, [box], (255, 255,255))

    return detection, box_img

def _dictify_hough(shape, houghVals):
    """
    Function converts from hough line tuples (rho, theta) into scaled pixel
    coordinates on the image. Returned value is a space separated string:
    "x1 y1 x2 y1"
    """
    rho, theta = houghVals
    n_x, n_y = shape

    x0 = np.cos(theta)*rho
    y0 = np.sin(theta)*rho
    x1 = int(x0 - (n_x+n_y)*np.sin(theta))
    y1 = int(y0 + (n_x+n_y)*np.cos(theta))
    x2 = int(x0 + (n_x+n_y)*np.sin(theta))
    y2 = int(y0 - (n_x+n_y)*np.cos(theta))

    return {"x1":x1, "y1":y1, "x2":x2, "y2":y2}


def process_field_bright(img, lwTresh, thetaTresh, dilateKernel, contoursMode,
                         contoursMethod, minAreaRectMinLen, houghMethod,
                         nlinesInSet, lineSetTresh, dro, debug):
    """
    Function detects bright trails in images.
    Please use RemoveStars class as some pre-processing takes place.

      init params.
    -----------------
    Keywords:
        results:
            file in which a possible detection is stored
        img:
            numpy array representing gray 32 bit 1 chanel image.
        lwTresh, thetaTresh, dilateKernel, contoursMode,
        contoursMethod, minAreaRectMinLen, houghMethod, nlinesInSet,
        linesetTresh, dro, debug:
            see detecttrails module docstring for more details.

      Function:
    --------------
        1)  pixels with values bellow minFlux are set to 0
        2)  Scale the image to 8 bit integer, 1 channel
        3)  histogram equalization
        4)  dilate to expand features
        5)  fit minimal area rectangles. Function aborts if no
            minAreaRect are found, see: _fit_minAreaRect help
        6)  fit Hough lines on image and on found rectangles
        7)  compare lines, see: _check_theta help
        8) if evaluation passed write the results into file and return
           True, else returns False.
    """
    img[img<0] = 0

    #FITS files are usually 1 channel 32 bit float images, we need
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


    detection, box_img = _fit_minAreaRect(equ, contoursMode, contoursMethod,
                                          minAreaRectMinLen, lwTresh,
                                          debug)

    if debug:
        cv2.imwrite(os.path.join(pathBright, "3contoursBRIGHT.png"), box_img,
                    [cv2.IMWRITE_PNG_COMPRESSION, 3])
        print ("BRIGHT: saving contours")

    if detection:
        equhough = cv2.HoughLines(equ, houghMethod, np.pi/180, 1)
        boxhough = cv2.HoughLines(box_img, houghMethod, np.pi/180, 1)

        if debug:
            _draw_lines(equhough, equ, nlinesInSet, "5equhoughBRIGHT",
                        path=pathBright)
            _draw_lines(boxhough, box_img,  nlinesInSet, "4boxhoughBRIGHT",
                        path=pathBright)
            print("BRIGHT!")

        if _check_theta(equhough, boxhough, nlinesInSet, dro, thetaTresh,
                        lineSetTresh, debug):
            return (False, None)
        else:
            return (True, _dictify_hough(equ.shape, equhough[0][0]))
    else:
        if debug: print("BRIGHT: no boxes found")
        return (False, None)


def process_field_dim(img, minFlux, addFlux, lwTresh, thetaTresh, erodeKernel,
                      dilateKernel, contoursMode, contoursMethod,
                      minAreaRectMinLen, houghMethod, nlinesInSet,
                      dro, lineSetTresh, debug):
    """
    Function detects dim trails in images.
    Please use RemoveStars class as some pre-processing takes place.

      init params.
    -----------------
    Keywords:
        results:
            file in which a possible detection is stored
        img:
            numpy array representing gray 32 bit 1 chanel image.
        minFlux, addFlux, lwTresh, thetaTresh, erodeKernel,
        dilateKernel, contoursMode, contoursMethod, minAreaRectMinLen,
        houghMethod, nlinesInSet, dro, linesetTresh, debug:
            see detecttrails module docstring for more details.

      Function:
    --------------
        1)  pixels with values bellow minFlux are set to 0
        2)  addFlux is added to remaining pixels
        3)  Scale the image to 8 bit 1 chanel
        4)  histogram equalization
        5)  erode to kill noise
        6)  dilate to expand features that survived
        7)  fit minimal area rectangles. Function aborts if no
            minAreaRect are found, see: _fit_minAreaRect help
        8)  fit Hough lines on image and on found rectangles
        9)  compare lines, see: help(_check_theta)
        10) if evaluation passed write the results into file and return
            True, else returns False.
    """
    img[img<minFlux]=0
    img[img>0]+=addFlux

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

    detection, box_img = _fit_minAreaRect(equ, contoursMode,
                                          contoursMethod,
                                          minAreaRectMinLen, lwTresh,
                                          debug)
    if debug:
        cv2.imwrite(os.path.join(pathDim, "9contoursDIM.png"), box_img,
                    [cv2.IMWRITE_PNG_COMPRESSION, 0])
        print("DIM: saveamo konture")

    if detection:
        equhough = cv2.HoughLines(equ, houghMethod, np.pi/180, 1)
        boxhough = cv2.HoughLines(box_img, houghMethod, np.pi/180, 1)

        if debug:
            _draw_lines(equhough, equ, nlinesInSet, "10equhoughDIM",
                        compression=4)
            _draw_lines(boxhough, box_img, nlinesInSet, "11boxhoughDIM",
                        compression=4, color=(0,0,255))
            print("DIM")


        if _check_theta(equhough, boxhough, nlinesInSet, dro, thetaTresh,
                        lineSetTresh, debug):
            return (False, None)
        else:
            return (True, _dictify_hough(equ.shape, equhough[0][0]))
    else:
        if debug: print("DIM: FALSE AT NO RECTANGLES MATCHING THE CONDITIONS FOUND!")
        return (False, None)
