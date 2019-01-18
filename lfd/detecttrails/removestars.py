"""Removestars module contains all the required functionality to read a catalog
source and blot out objects in the image. Currently only SDSS photoObj files
are supported as a catalog source. Old code supporting CSV catalog sources was
left as an example how its relatively simple to add a different catalog source.

"""

import os
import csv
import math

import numpy as np
import fitsio

from .sdss import astrom
from .sdss import files

__all__ = ["read_photoObj", "remove_stars"]


def CSV_read(path_to_CAS):
    """ .. deprecated:: 1.0
    Defines a function that reads CSV file given by path into a list of
    dictionaries. Function is deprecated in favor of photoObjRead.

    Returned list is arranged as
        {[ra:, dec:, u:, g:, r:, i:, z:],
            ...}.

    """
    labels=['ra', 'de', 'u', 'g', 'r', 'i', 'z']
    read = csv.DictReader(open(path_to_CAS), labels,
                          delimiter=',', quotechar='"')
    lines = list()
    for line in read:
        lines.append(line)
    return lines

def remove_stars_CSV(img, _run, _camcol, _filter, _field):
    """.. deprecated:: 1.0
    Function that removes all stars found in coordinates file from a given
    image. Requires the use of edited sdssFileTypes.par located in
    detect_trails/sdss/share. Function was deprecated in favor of RemoveStars.

    """
    Coord = CSVRead(files.filename('CSVCoord', run=_run,
                                          camcol=_camcol, field=_field))
    Coord = Coord[1:]
    conv = astrom.Astrom(run=_run, camcol=_camcol)

    for star in Coord:
        try:
            if (float(star[_filter])<23):
                ra = float(star['ra'])
                de = float(star['de'])
                xy = conv.eq2pix(_field, _filter, ra, de)
                x, y=xy[0], xy[1]
                img[x-30:x+30, y-30:y+30].fill(0.0)
        except ValueError as err:
            pass
    return img



class ResolveStatus:
    """Defines resolver flag values. See
    https://www.sdss.org/dr15/algorithms/bitmasks/#RESOLVE_STATUS
    """
    RUN_PRIMARY 	= 0
    RUN_RAMP        = 1
    RUN_OVERLAPONLY = 2
    RUN_IGNORE 	    = 3
    RUN_EDGE        = 4
    RUN_DUPLICATE 	= 5
    SURVEY_PRIMARY 	= 8
    SURVEY_BEST 	= 9
    SURVEY_SECONDARY= 10
    SURVEY_BADFIELD = 11
    SURVEY_EDGE 	= 12


def is_set(bitmask, flag):
    """Check whether desired flag is set in the bitmask.

    Parameters
    ----------
    bitmask : bin, hex, int
        bitmask to check (f.e. 0b10000000001, 0x401, 1025)
    flag : int
        what flag position to check
    """
    return bitmask >> flag & 1


def read_photoObj(path_to_photoOBJ):
    """Function that reads photoObj headers and returns read parameters as
    Python builtin types. 

    Returns
    -------
    row : list(dict)
        y coordinate of an object on the image. Each entry is a dictionary
        where keys are the filter designations and values the coordinates
    col : list(dict)
        x coordinate of an object on the image. Each entry is a dictionary
        where keys are the filter designations and values the coordinates
    petro90 : list(dict)
        This is the radius, in arcsec, from the center of the object that
        contains 90% of its Petrosian flux. Each entry is a dictionary where
        keys are the filter designations and values the radii. See:
        http://www.sdss3.org/dr10/algorithms/magnitudes.php#mag_petro and
        http://data.sdss3.org/datamodel/files/BOSS_PHOTOOBJ/RERUN/RUN/CAMCOL/photoObj.html
    nObserve : list(int)
        Number of times an area containing that object was imaged by SDSS.
    nDetect : list(int)
        Number of times the object was detected by SDSS.
    resflags : list(hex)
        Hexadecimal bitmask produced by the SDSS resolver. See
        https://www.sdss.org/dr15/algorithms/bitmasks/#RESOLVE_STATUS
        https://www.sdss.org/dr14/algorithms/resolve/ and
        https://www.sdss.org/dr15/algorithms/bitmasks/
        Only really used for debugging after this point.

    Parameters
    ----------
     path_to_photoOBJ : str
         path to a photoObj*.fits file
 
    """
    header1, header2 = fitsio.read(path_to_photoOBJ, header="True")

    rowf = list()
    colf = list()
    petro90f = list()
    resflags = list()

    nObserve = header1["NOBSERVE"]
    nDetect = header1["NDETECT"]

    for obj in header1:
        resolve_flags = hex(obj["RESOLVE_STATUS"])
        resflags.append(resolve_flags)

        # does the same as is_set function, except slightly faster
        is_set = lambda flag: int(resolve_flags, 16) >> flag & 1

        # I have no idea how these conditions make sense, but here we are
        bad = (is_set(ResolveStatus.RUN_PRIMARY) and
               is_set(ResolveStatus.SURVEY_BEST))
        not_good = (is_set(ResolveStatus.RUN_PRIMARY) and
                    is_set(ResolveStatus.SURVEY_PRIMARY))

        if not bad and not not_good:
            row = obj['ROWC']
            col = obj['COLC']
            petro90 = obj['PETROTH90']
            psfMag = obj['PSFMAG']

           #names are current object data structures, singular to mark 1 object
            rowf.append({'u':math.ceil(row[0]), 'g':math.ceil(row[1]),
                         'r':math.ceil(row[2]), 'i':math.ceil(row[3]),
                         'z':math.ceil(row[4])})

            colf.append({'u':math.ceil(col[0]), 'g':math.ceil(col[1]),
                         'r':math.ceil(col[2]), 'i':math.ceil(col[3]),
                         'z':math.ceil(col[4])})

            petro90f.append({'u':math.ceil(petro90[0]), 'g':math.ceil(petro90[1]),
                             'r':math.ceil(petro90[2]), 'i':math.ceil(petro90[3]),
                             'z':math.ceil(petro90[4])})

    return rowf, colf, petro90f,  nObserve, nDetect, resflags


def remove_stars(img, run, camcol, filter, field, defaultxy, maxxy, pixscale,
                 debug):
    """Removes all stars found in coordinate file from a given image by
    "blottings" out black circles at objects coordinates.

    Radius of the circle is, if possible, determined according to its petrosian
    magnitude. The radius is converted from arcsec to pixel size by scaling it
    by pixscale value. If the calculated radius is less than zero or bigger
    than maximal allowed size, a default radius is used.

    Parameters
    ----------
    img : np.array
        grayscale 8 bit image
    _run : int
        run identifier
    _camcol : int
        camera column identifier 1-6
    _filter : str
        filter identifier (u,g,r,i,z)
    _field : int
        field identifier
    defaultxy : int
        default length of half of the total length of square sides
    filter_caps : dict
        dictionary (u,g,r,i,z) that defines the limiting magnitude under
        which objects are not erased
    maxxy:
        maximal allowed length of the half the length of square side, int
    pixscale:
        pixel scale. 1 pixel width represents pixscale arcsec.
    dxy:
        default side dimension of drawn rectangle.
    magcount:
        maximal allowed number of filters with differences of mag. greater
        than maxmagdiff.
    maxmagdiff:
        maximal allowed difference between two magnitudes.

    """
    rows, cols, petro90, nObserve, nDetect, resflags = \
        read_photoObj(files.filename("photoObj", run=run, camcol=camcol,
                                     field=_field))

    if debug:
        # we really don't want to trample on original data at this point yet
        # so we make a copy and make objects in it more visible
        img2 = img.copy()
        img2[img2<0.02]=0
        img2[img2>0]+=0.5

        img2 = cv2.convertScaleAbs(img2)
        img2 = cv2.equalizeHist(img2)
        # reduce the img brightness so text is more readable
        img2[img2>0] -= 125

    for i in range(len(rows)):
        x = int(cols[i][_filter])
        y = int(rows[i][_filter])

        dxy = defaultxy
        if petro90[i][_filter] > 0:
            dxy = int(petro90[i][_filter]/pixscale) + 10
        if dxy > maxxy:
            dxy = defaultxy

        if nObserve[i] == nDetect[i]:
            img = cv2.circle(img, (x, y), 2*dxy, 0, thickness=cv2.FILLED)
            if debug:
                img2 = cv2.circle(img2, (x, y), dxy, 255, thickness=1)

                bottomLeftCornerOfText = (x,y)
                fontFace = cv2.FONT_HERSHEY_SIMPLEX
                fontScale = 0.5
                fontColor = (255, 255, 255)

                cv2.putText(img2,
                            str(resflags[i]), 
                            bottomLeftCornerOfText, 
                            fontFace, 
                            fontScale,
                            fontColor)
                
    if debug:
        cv2.imwrite("/home/dino/Desktop/test.png", img2)

    return img
