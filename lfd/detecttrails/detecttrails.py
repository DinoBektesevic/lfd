"""Detecttrails module is the SDSS oriented wrapper that will call the correct
order of operations on the targeted data to succesfully run LFD. The module also
handles the IO operations required to succesfully store results and wraps the
required functionality for easier debugging.

"""

import os
import traceback

import numpy as _np
import fitsio

import cv2
from cv2 import RETR_LIST, RETR_EXTERNAL, RETR_CCOMP, RETR_TREE
from cv2 import (CHAIN_APPROX_NONE , CHAIN_APPROX_SIMPLE, CHAIN_APPROX_TC89_L1,
                 CHAIN_APPROX_TC89_KCOS)

import bz2

from lfd.detecttrails.removestars import * #remove_stars
from lfd.detecttrails.processfield import * #process_field_bright, process_field_dim
from lfd.detecttrails.processfield import setup_debug
from lfd.detecttrails.sdss import files

__all__ = ["DetectTrails", "process_field"]

def process_field(results, errors, run, camcol, filter, field, params_bright,
                  params_dim, params_removestars):
    """Calls the correct order of actions needed to detect trails per frame.
    Writes  "results.txt" and "errors.txt".

    Order of operations:

      1. Check if .fits file exists

         a. If it doesn't see a compressed .bz2 version exists. If it does
         b. uncompress it to $FITS_DUMP env. var location. If the env. var.
            was not set, decompress to the fits_dump folder in the package

      2. Remove known object from the image by drawing squares over them
      3. Try detecting a bright trail (very fast). If successful write results
         and stop.
      4. if bright detection is not made, try detecting a dim trail. If found
         write results and stop, otherwise just stop.
      5. clean-up (remove unpacked fits, close files, dump silenced errors)

    Parameters
    ----------
    results : file
        a file object, a stream or any such counterpart to which results
        will be written
    errors : file
        a file object, stream, or any such counterpart to which errors will be
        written
    run : int
        run designation
    camcol : int
        camcol designation, 1 to 6
    filter : str
        filter designation, one of ugriz
    params_bright : dict
        dictionary containing execution parameters required by process_bright
    params_dim : dict
        dictionary containing execution parameters required by process_dim
    params_removestars : dict
        dictionary containing execution parameters required by remove_stars
    """
    removefits = False
    try:
        origfitspath = files.filename('frame', run=run, camcol=camcol,
                                      field=field, filter=filter)

        # downright sadness that fitsio doesn't support bz2 compressed fits'
        # if there is no .fits, but only .fits.bz2 you have to open, decompress,
        # save, and reopen with fitsio. We also don't want to delete existing
        # unpacked fits files so we set the removefits flag to True only when
        # *we* created a file by unpacking
        if not os.path.exists(origfitspath):

            bzpath = origfitspath+".bz2"
            if not os.path.exists(bzpath):
                raise FileNotFoundError(("File {0} or its bz2 compressed "
                "version not found. Are you sure they exist?"))

            with open(bzpath, "rb") as compressedfits:
                fitsdata = bz2.decompress(compressedfits.read())

                # see if user uncompressed fits dumping location is set
                try:
                    fitsdmp = os.environ["FITS_DUMP"]
                except KeyError:
                    # if not default to the fits_dump dir in the package
                    modloc = os.path.split(__file__)[0]
                    fitsdmp = os.path.join(modloc, "fits_dump/")

                fitspath = os.path.join(fitsdmp, os.path.split(origfitspath)[-1])

                # save the uncompressed fits
                with open(fitspath, "wb") as decompressed:
                    decompressed.write(fitsdata)

                # setting the flag here, after we have certainly written and
                # closed the file succesfully helps escape any errors later on
                # in case we try to remove unexsiting file
                removefits = True
        else:
            fitspath = origfitspath

        img = fitsio.read(fitspath)
        h   = fitsio.read_header(fitspath)

        printit = (
            "{} {} {} {} {} {} {} {} {} {} {} {} {} "
            ).format(run, camcol, filter, field, h['TAI'],    h['CRPIX1'],
                     h['CRPIX2'], h['CRVAL1'],   h['CRVAL2'], h['CD1_1'],
                     h['CD1_2'],  h['CD2_1'],    h['CD2_2'])

        img = remove_stars(img, run, camcol, filter, field,
                           **params_removestars)

        #WARNING mirror the image vertically
        #it seems CV2 and FITSIO set different pix coords
        img = cv2.flip(img, 0)

        detection, res = process_field_bright(img, **params_bright)

        if detection:
                results.write(printit+str(res["x1"])+" "+str(res["y1"])+" "+
                              str(res["x2"])+" "+str(res["y2"])+"\n")
        else:
            detection, res= process_field_dim(img, **params_dim)
            if detection:
                    results.write(printit+str(res["x1"])+" "+str(res["y1"])+" "+
                                  str(res["x2"])+" "+str(res["y2"])+"\n")

    except Exception as e:
        if params_bright["debug"] or params_dim["debug"]:
            traceback.print_exc(limit=3)
        errors.write(str(run)+","+str(camcol)+","+str(field)+","+str(filter)+"\n")
        traceback.print_exc(limit=3, file=errors)
        errors.write(str(e)+"\n\n")
        pass

    finally:
        if removefits:
            os.remove(fitspath)



class DetectTrails:
    """Convenience class that processes targeted SDSS frames.

    Example usage

    .. code-block:: python

       foo = DetectTrails(run=2888)
       foo = DetectTrails(run=2888, camcol=1, filter='i')
       foo = DetectTrails(run=2888, camcol=1, filter='i', field=139)
       foo.process()

    At least 1 keyword has to be sent!

    See documentation for full details on detection parameters. Like results
    and errors file paths, detection parameters are optional too and can be set
    after instantiation through provided dictionaries.

    .. code-block:: python

       foo.params_dim
       foo.params_bright["debug"] = True
       foo.params_removestars["filter_caps"]["i"] = 20

    All errors are silenced and dumped to error file. Results are dumped to
    results file.

    Parameters
    ----------
    run : int
        run designation
    camcol : int
        camcol designation, 1 to 6
    filter : str
        filter designation, one of ugriz filters
    field : int
        field designation
    params_dim : dict
         detection parameters for detecting dim trails. See docs for details.
    params_bright : dict
         detection parameters for bright trails. See docs for details.
    params_removestars : dict
         detection parameters for tuning star removal. See docs for details.
    debug : bool
         turns on verbose and step-by-step image output visualizing the
         processing steps for all steps simultaneously. If $DEBUGPATH env. var.
         is not set errors will be raised.
    results : str
         path to file where results will be saved
    errors : str
         path to file where errors will be stored
    """

    def __init__(self, **kwargs):
        savepth = (kwargs["savepath"] if "savepath" in kwargs else ".")
        self.kwargs=kwargs
        self.params_bright = {
            "lwTresh": 5,
            "thetaTresh": 0.15,
            "dilateKernel":_np.ones((4,4), _np.uint8),
            "contoursMode": RETR_LIST, #CV_RETR_EXTERNAL
            "contoursMethod": CHAIN_APPROX_NONE, #CV_CHAIN_APPROX_SIMPLE
            "minAreaRectMinLen": 1, ##HAS A BIG IMPACT ON FOUND COUNTOURS!
            "houghMethod": 20, #CV_HOUGH_STANDARD
            "nlinesInSet": 3,
            "lineSetTresh": 0.15,
            "dro": 25,
            "debug": False
            }
        self.params_dim = {
            "minFlux": 0.02,
            "addFlux": 0.5,
            "lwTresh": 5,
            "thetaTresh": 0.15,
            "erodeKernel":_np.ones((3,3), _np.uint8), #(3,3)
            "dilateKernel":_np.ones((9,9), _np.uint8),
            "contoursMode": RETR_LIST, #CV_RETR_EXTERNAL
            "contoursMethod": CHAIN_APPROX_NONE, #CV_CHAIN_APPROX_SIMPLE
            "minAreaRectMinLen": 1,
            "houghMethod": 20, #CV_HOUGH_STANDARD
            "nlinesInSet": 3,
            "lineSetTresh": 0.15,
            "dro": 20,
            "debug": False
            }
        self.params_removestars = {
            "pixscale": 0.396,
            "defaultxy": 20,
            "maxxy": 60,
            "filter_caps": {'u': 22.0, 'g': 22.2,'r': 22.2, 'i':21.3, 'z': 20.5},
            "magcount": 3,
            "maxmagdiff": 3,
            "debug": False
            }

        if "results" in kwargs:
            self.results = kwargs["results"]
        else:
            self.results = os.path.join(savepth, 'results.txt')

        if "errors" in kwargs:
            self.errors = kwargs["errors"]
        else:
            self.errors  = os.path.join(savepth, 'errors.txt')

        if "params_bright" in kwargs:
            self.params_bright = kwargs["params_bright"]
        if "params_dim" in kwargs:
            self.params_bright = kwargs["params_dim"]
        if "params_removestars" in kwargs:
            self.params_bright = kwargs["params_removestars"]

        if "debug" in kwargs:
            self.debug = kwargs.pop("debug")
            self.params_bright["debug"] = self.debug
            self.params_dim["debug"] = self.debug
            self.params_removestars["debug"] = self.debug
        if any([self.params_removestars["debug"], self.params_bright["debug"],
                self.params_dim["debug"]]):
            setup_debug()

        self._load()

    def _runInfo(self):
        """Reads runlist.par file and extracts startfield and endfield of a
        run. Runs are retrieved from self._run attribute of instance.

        """
        rl = files.runlist()
        w, = _np.where(rl['run'] == self._run)
        if len(w) == 0:
            raise ValueError("Run %s not found in runList.par" % self._run)
        startfield = rl[w]['startfield'][0]
        endfield = rl[w]['endfield'][0]
        return startfield, endfield

    def _getRuns(self):
        """Reads runlist.par file and returns a list of all runs."""
        rl = files.runlist()
        runs = rl["run"]
        if runs is None:
            raise ValueError("Unable to retrieve runs. Retrieved NoneType.")
        return runs

    def _load(self):
        """Parses the send kwargs to determine what selection users  wants to
        process. Currently supported options are:

        * run
        * run-camcol
        * run-filter
        * run-filter-camcol
        * camcol-filter
        * camcol-frame
        * field (full specification run-filter-camcol-frame)

        """
        self._run, self._camcol, self._field = int(0), int(0), int(0)
        self._filter, self._pick = str(0), str(0)

        kwargs = self.kwargs

        if 'run' in kwargs:
            self._run=kwargs['run']
            self._pick = 'run'

        if 'camcol' in kwargs:
            if kwargs['camcol'] not in (1, 2, 3, 4, 5, 6):
                raise ValueError("Nonexisting camcol")
            self._camcol = kwargs['camcol']
            self._pick = 'run-camcol'

        if 'field' in kwargs or 'frame' in kwargs:
            if self._camcol is 0:
                raise ValueError("send camcol= ")
            if 'field' in kwargs:
                self._field = kwargs['field']
            else:
                self._field = kwargs['frame']

        if 'filter' in kwargs:
            if  kwargs['filter'] not in ('u', 'g', 'r', 'i', 'z'):
                raise ValueError("Nonexistting filter")
            self._filter = kwargs['filter']
            if self._camcol is not 0:
                self._pick = 'camcol-filter'
            if self._run is not 0:
                self._pick = 'run-filter'
            if self._camcol is not 0 and self._run is not 0:
                self._pick = 'run-camcol-filter'

        if 'filter' not in kwargs:
            if self._field is not 0 and self._camcol is not 0:
                self._pick = 'camcol-frame'

        if self._field is not 0 and self._camcol is not 0 \
        and self._filter is not "0":
            self._pick = 'field'


    def process(self):
        """Convenience function that runs process_field() for various inputs.
        Not using this function will void majority of error and exception
        handling in processing.

        """
        with open(self.results, "a") as results, \
             open(self.errors, "a") as errors:

            if self._pick == "camcol-filter":
                runs = self._getRuns()
                for _run in runs:
                    self._run=_run
                    startfield, endfield = self._runInfo()
                    for _field in range(startfield, endfield, 1):
                        process_field(results, errors, _run, self._camcol,
                                      self._filter, _field, self.params_bright,
                                      self.params_dim, self.params_removestars)
                self._run=0


            if self._pick == 'run':
                startfield, endfield = self._runInfo()
                filters = ('u', 'g', 'r', 'i', 'z')
                camcols = (1, 2, 3, 4, 5, 6)
                for _camcol in camcols:
                    for _filter in filters:
                        for _field in range (startfield, endfield, 1):
                            process_field(results, errors, self._run, _camcol,
                                          _filter, _field, self.params_bright,
                                          self.params_dim, self.params_removestars)

            if self._pick == 'run-filter':
                startfield, endfield = self._runInfo()
                camcols = (1, 2, 3, 4, 5, 6)
                for _camcol in camcols:
                    for _field in range (startfield, endfield, 1):
                        process_field(results, errors, self._run, _camcol,
                                      self._filter, _field, self.params_bright,
                                      self.params_dim, self.params_removestars)

            if self._pick == 'run-camcol':
                startfield, endfield = self._runInfo()
                filters = ('u', 'g', 'r', 'i', 'z')
                for _filter in filters:
                    for _field in range (startfield, endfield, 50):
                        process_field(results, errors, self._run, self._camcol,
                                      _filter, _field, self.params_bright,
                                      self.params_dim, self.params_removestars)


            if self._pick == 'run-camcol-filter':
                startfield, endfield = self._runInfo()
                for _field in range (startfield, endfield, 1):
                    process_field(results, errors, self._run, self._camcol,
                                  self._filter, _field, self.params_bright,
                                  self.params_dim, self.params_removestars)

            if self._pick == 'camcol-frame':
                filters = ('u', 'g', 'r', 'i', 'z')
                for _filter in filters:
                    process_field(results, errors, self._run, self._camcol,
                                  _filter, self._field, self.params_bright,
                                  self.params_dim, self.params_removestars)


            if self._pick == 'field':
                process_field(results, errors, self._run, self._camcol,
                              self._filter, self._field, self.params_bright,
                              self.params_dim, self.params_removestars)
