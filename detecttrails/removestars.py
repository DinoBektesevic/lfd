import numpy as np
import csv
import os
import fitsio
from sdss import astrom
from sdss import files
import math

def CSV_read(path_to_CAS):
    """     ***DEPRECATED***
    Defines a function that reads CSV file given by
    path into a list of dictionaries. Function is deprecated in
    favor of photoObjRead.
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
    """     ***DEPRECATED***
    Function that removes all stars found in coordinates file
    from a given image. Requires the use of edited sdssFileTypes.par
    located in detect_trails/sdss/share
    Function was deprecated in favor of RemoveStars."""
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


def photoObj_read(path_to_photoOBJ):
    """
    Function that reads photoObj headers and returns following lists:
        row, col, psfMag, petro90, objctype, types, nObserve, nDetect

    row      -"y" coordinate of an object on the image.
              Each entry is a dictionary {u:, g:, r:, i:, z:}.
    col      -"x" coordinate of an object on the image.
              Each entry is a dictionary {u:, g:, r:, i:, z:}
    psfMag   -http://www.sdss3.org/dr10/algorithms/magnitudes.php#mag_psf
              Each entry is a dictionary {u:, g:, r:, i:, z:}
    nObserve -Number of times that object was imaged by SDSS.
    objctype -Number of times that object was detected by frames pipeline.
    petro90  -http://www.sdss3.org/dr10/algorithms/magnitudes.php#mag_petro.
              http://data.sdss3.org/datamodel/files/BOSS_PHOTOOBJ/RERUN/RUN/CAMCOL/photoObj.html
              Specifically this is the radius, in arcsec, from the center of
              the object that contains 90% of its Petrosian flux.  
              Each entry is a dictionary {u:, g:, r:, i:, z:}

    Each entry in the list represents a different object that was dete-
    cted by the frames pipeline.
    
    containing row, col in pix coordinates, psf magnitudes per band
    and radii (arcsec) containing 90% of Petrosian flux.
    Returned list is arranged as
        {[row[{u: g: r: i: z:}], col[{u: g: r: i: z:}],
          psfMag[{u: g: r: i: z:}], petro90[{u: g: r: i: z:}]}.

    init params.
   -----------------
    Keywords:
    
        path_to_photoOBJ:
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
    """
    DEPRECATED
    Used to colorize the image for debugging purposes.
    """
    if np.shape(array)[-1] != len(tuple_val):
        raise ValueError("Tuple len is not the same as array element len")

    for i in xrange(len(array)):
        for j in xrange(len(array[i])):
            array[i,j] = tuple_val
    return array
        

def remove_stars(img, _run, _camcol, _filter, _field, defaultxy, filter_caps,
                maxxy, pixscale, magcount, maxmagdiff):
    """
    Function that removes all stars found in coordinate file
    from a given image.

    Function "blots" out black squares, pixel value 0.0, on the image.
    Size of the square is, if possible, determined with petro90 radius
    retrieved with photoObjRead function. Scaling factor pixscale is
    applied (petro90 values are in arcsec).
    If the calculated radius is less than zero a default square size is used.
    If the calculated radius is longer than maxxy a default square size is used.

    Trails are often extracted as parent-child mix of galaxies/stars by the
    frames pipeline and are written as such in the photoObj fits files.
    Aditionally to determining size of the blocked out square, function tries to
    discriminate actual sources from false ones.
    
    Squares will only be drawn:
        - if there is a valid psfMag value.
        - for those psfMag values that are under a certain user-set cap.
        - if differences in measured magnitudes of all filters are less than
          user-set value, maxmagdiff, in more than or equal to a user-set
          number of filters, magcount.
          i.e: set maxmagdiff = 5, magcount = 3
               won't pass: [2,8,8,8,8], [2,2,8,8,8], [1,1,7,8,9]
               will pass: [5,6,7,8,9], [3,6,7,8,9], [3,3,7,8,9]

    Idea is that psfMag values that contain only "opposite" extreme values
    (very bright/very dim) are  most likely a false detection, they exist in
    one of the filters but not in any others. Such objects are not removed.
    
    init params.
    -----------------
    Keywords:

        img:
            numpy array representing gray 8 bit image with
            pre-removed stars.
        _run:
            run number
        _camcol:
            camera column number
        _filter:
            filter identifier (u,g,r,i,z)
        _field:
            field number
        defaultxy:
            default length of half of total length of square sides, int
        filter_caps:
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
        photoObj_read(files.filename("photoObj", run=_run, camcol=_camcol,
                                    field=_field))

    for i in range(len(rows)):
        x = int(rows[i][_filter])
        y = int(cols[i][_filter])

        if psfMag[i] and psfMag[i][_filter] < filter_caps[_filter]:
            diffs = []
            a = [val for val in psfMag[i].itervalues()]
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
