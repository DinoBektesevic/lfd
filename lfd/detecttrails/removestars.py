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


def read_photoObj(path_to_photoOBJ):
    """Function that reads photoObj headers and returns following lists:

   Returns
   -------
   row : list(dict)
       y coordinate of an object on the image. Each entry is a dictionary
       where keys are the filter designations and values the coordinates
   col : list(dict)
       x coordinate of an object on the image. Each entry is a dictionary
       where keys are the filter designations and values the coordinates
   psfMag : list(dict)
       Each entry is a dictionary where keys are the filter designations and
       values the magnitudes. See: http://www.sdss3.org/dr10/algorithms/magnitudes.php#mag_psf
   nObserve : list(int)
       Number of times that object was imaged by SDSS.
   objctype : list(int)
       SDSS type identifier, see cas.sdss.org/dr7/de/help/browser/enum.asp?n=ObjType
   petro90 : list(dict)
       This is the radius, in arcsec, from the center of the object that
       contains 90% of its Petrosian flux. Each entry is a dictionary where
       keys are the filter designations and values the radii. See: http://www.sdss3.org/dr10/algorithms/magnitudes.php#mag_petro
       and http://data.sdss3.org/datamodel/files/BOSS_PHOTOOBJ/RERUN/RUN/CAMCOL/photoObj.html

   Parameters
   ----------
    path_to_photoOBJ : str
        string type system path to a photoObj*.fits file

    """
    header1, header2 = fitsio.read(path_to_photoOBJ, header="True")

    #variable names are lowercase fits field names, optionally an "s" is added
    #at the end to mark a collection of another data set (dictionary/list)
    objctype = header1['OBJC_TYPE']
    types = header1['TYPE']
    rows = header1['ROWC']
    cols = header1['COLC']
    petro90s = header1['PETROTH90']
    psfMags = header1['PSFMAG']
    nObserve = header1["NOBSERVE"]
    nDetect = header1["NDETECT"]

    #names of fits field names with an f at the end signalizing "final"
    #these are the lists that get returned
    rowf = list()
    colf = list()
    petro90f = list()
    psfMagf = list()
    for i in range (0, len(rows)):
        #names are current object data structures, singular to mark 1 object
        row = rows[i]
        rowf.append({'u':math.ceil(row[0]), 'g':math.ceil(row[1]),
                     'r':math.ceil(row[2]), 'i':math.ceil(row[3]),
                     'z':math.ceil(row[4])})
        col = cols[i]
        colf.append({'u':math.ceil(col[0]), 'g':math.ceil(col[1]),
                     'r':math.ceil(col[2]), 'i':math.ceil(col[3]),
                     'z':math.ceil(col[4])})
        psfMag = psfMags[i]
        psfMagf.append({'u':math.ceil(psfMag[0]), 'g':math.ceil(psfMag[1]),
                        'r':math.ceil(psfMag[2]), 'i':math.ceil(psfMag[3]),
                        'z':math.ceil(psfMag[4])})
        petro90 = petro90s[i]
        petro90f.append({'u':math.ceil(petro90[0]), 'g':math.ceil(petro90[1]),
                         'r':math.ceil(petro90[2]), 'i':math.ceil(petro90[3]),
                         'z':math.ceil(petro90[4])})

    return rowf, colf, psfMagf, petro90f, objctype, types, nObserve, nDetect



def fill(array, tuple_val):
    """.. deprecated:: 1.0
    Used to colorize the image for debugging purposes.
    """
    if np.shape(array)[-1] != len(tuple_val):
        raise ValueError("Tuple len is not the same as array element len")

    for i in range(len(array)):
        for j in range(len(array[i])):
            array[i,j] = tuple_val
    return array


def remove_stars(img, _run, _camcol, _filter, _field, defaultxy, filter_caps,
                 maxxy, pixscale, magcount, maxmagdiff, debug):
    """Removes all stars found in coordinate file from a given image by
    "blottings" out black squares at objects coordinats.

    Size of the square is, if possible, determined according to its petrosian
    magnitude. The square is up/down-scaled by a scaling factor converting the
    object size from arcsec to pixel size. If the calculated radius is less
    than zero or bigger than maximal allowed size, a default square size is
    used.

    Aditionally to determining size of the blocked out square, function tries to
    discriminate actual sources from false ones.

    Squares will only be drawn:

    * if there is a valid psfMag value.
    * for those psfMag values that are under a certain user-set cap.
    * if differences in measured magnitudes of all filters are less maxmagdiff
      in more than or equal to magcount filters. F.e. for maxmagdiff=5 magcount=3

      | won't pass: [2,8,8,8,8], [2,2,8,8,8], [1,1,7,8,9]
      | will pass: [5,6,7,8,9], [3,6,7,8,9], [3,3,7,8,9]

    Idea is that psfMag values that contain only "opposite" extreme values
    (very bright/very dim) are  most likely a false detection, they exist in
    one of the filters but not in any others. Such objects are not removed.

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

    rows, cols, psfMag, petro90, objctype, types, nObserve, nDetect = \
        read_photoObj(files.filename("photoObj", run=_run, camcol=_camcol,
                                    field=_field))

    for i in range(len(rows)):
        x = int(rows[i][_filter])
        y = int(cols[i][_filter])

        if psfMag[i] and psfMag[i][_filter] < filter_caps[_filter]:
            diffs = []
            a = [val for key, val in psfMag[i].items()]
            for j in range(len(a)):
                for k in range(j+1, len(a)):
                    diffs.append(a[j]-a[k])
            diffs = np.absolute(diffs)

            if magcount >= np.count_nonzero(diffs>maxmagdiff):
                dxy = defaultxy
                if petro90[i][_filter] > 0:
                    dxy = int(petro90[i][_filter]/pixscale) + 10
                if dxy > maxxy:
                    dxy = defaultxy
                if nObserve[i] == nDetect[i]:
                    img[x-dxy:x+dxy, y-dxy:y+dxy].fill(0.0)

    return img
