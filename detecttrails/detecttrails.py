from removestars import remove_stars
from processfield import process_field_bright, process_field_dim
import fitsio
from sdss import files

import os
import traceback
import numpy as _np
import cv2
from cv2 import RETR_LIST, RETR_EXTERNAL, RETR_CCOMP, RETR_TREE
from cv2 import (CHAIN_APPROX_NONE , CHAIN_APPROX_SIMPLE,
                 CHAIN_APPROX_TC89_L1, CHAIN_APPROX_TC89_KCOS)


def process_field(results, errors, run, camcol, filter, field,
                  params_bright, params_dim, params_removestars):
    """
    Function that calls the correct order of actions needed to detect
    trails per frame. Writes  "results.txt" and "errors.txt".
    Please use the class!

    Order of operations:
      1) Unpack .tar.bz2 fits files to FITS_DUMP path
         (env. var. in start.sh)
      2) Remove Stars
      3) process field bright
      4) if bright detection is not made:
            4.1) process field dim is called
         4.2) else: write results.
      5) clean-up (remove unpacked fits, close files, dump silenced
         errors)
    """
    try:
        origPathName = files.filename('frame', run=run, camcol=camcol,
                                      field=field, filter=filter)

        unpackPath = os.environ["FITSDMP"]

        fname = origPathName.split("/")[-1]
        unpackedfits = os.path.join(unpackPath, fname)

        os.popen("bunzip2 -qkc "+origPathName+".bz2 >"+unpackedfits)

        img = fitsio.read(unpackedfits)

        h = fitsio.read_header(unpackedfits)
        printit = (str(run)+" "+str(camcol)+" "+filter+" "+str(field)+" "
                   +str(h['TAI'])+" "+str(h['CRPIX1'])+" "+str(h['CRPIX2'])+" "
                   +str(h['CRVAL1'])+" "+str(h['CRVAL2'])+" "+str(h['CD1_1'])+" "
                   +str(h['CD1_2'])+" "+str(h['CD2_1'])+" "+str(h['CD2_2'])+" ")

        img = remove_stars(img, run, camcol, filter, field,
                             **params_removestars)

        #WARNING mirror the image vertically
        #it seems CV2 and FITSIO set different pix coords
        img = cv2.flip(img, 0)

        detection,res = process_field_bright(img,**params_bright)

        if detection:
                results.write(printit+str(res["x1"])+" "+str(res["y1"])+" "+
                              str(res["x2"])+" "+str(res["y2"])+"\n")
        else:
            detection, res= process_field_dim(img, **params_dim)
            if detection:
                    results.write(printit+str(res["x1"])+" "+str(res["y1"])+" "+
                                  str(res["x2"])+" "+str(res["y2"])+"\n")

    except Exception, e:
        if params_bright["debug"] or params_dim["debug"]:
            traceback.print_exc(limit=3)
        errors.write(str(run)+","+str(camcol)+","+str(field)+","+str(filter)+"\n")
        traceback.print_exc(limit=3, file=errors)
        errors.write(str(e)+"\n\n")
        pass

    finally:
        try: os.remove(unpackedfits)
        except: pass



class DetectTrails:
    """
    (run={all} , camcol={1-6}, field={all], filter={all})

    Defines a convenience class that processes frames.
    Use with caution when processing large number of frames due to
    possible long execution times.
    Use cases:
        foo = DetectTrails(run=2888)
        foo = DetectTrails(camcol=1)
        foo = DetecTrails(filter="i")
        foo = DetectTrails(run=2888, camcol=1)
        foo = DetectTrails(run=2888, camcol=1, filter='i')
        foo = DetectTrails(run=2888, camcol=1, filter='i', field=139)
    At least 1 keyword has to be sent!
    Detection and execution parameters are optional, i.e.:
        foo.params_bright["debug"] = True
        foo.params_removestars["filter_caps"]["i"] = 20
    See module help for full list of optional parameters and explanations.
    To start detection routine call:
        foo.process()
    All errors are silenced and dumped to error file.  Results are dumped to
    results file. Default file location is the package home folder.

    init parameters
    ----------------
    Keywords:

        run:
            run ID

    Optional:

        camcol:
            camera column ID {1,2,3,4,5,6}
        field:
            frame ID
        filter:
            filter ID {u,g,r,i,z}
        params_dim:
            optional detection parameters for detecting dim trails. See
            detecttrails module help for full list and explanations.
        params_bright:
            optional detection parameters for detecting bright trails. See
            detecttrails module help for full list.
        params_removestars:
            optional detection parameters for tuning star removal. See
            detecttrails module help for full list.
    """

    def __init__(self, **kwargs):
        self.results = open('results.txt', 'a')
        self.errors = open('errors.txt', 'a')
        self.kwargs=kwargs
        self.params_bright = {
            "lwTresh": 5,
            "thetaTresh": 0.15,
            "dilateKernel":_np.ones((4,4), _np.uint8),
            "contoursMode": RETR_LIST, #CV_RETR_EXTERNAL
            "contoursMethod": CHAIN_APPROX_NONE, #CV_CHAIN_APPROX_SIMPLE
            "minAreaRectMinLen": 1, ##HAS A BIG IMPACT ON FOUND COUNTOURS!
            "houghMethod": 1, #CV_HOUGH_STANDARD
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
            "houghMethod": 1, #CV_HOUGH_STANDARD
            "nlinesInSet": 3,
            "lineSetTresh": 0.15,
            "dro": 20,
            "debug": False
            }
        self.params_removestars = {
            "pixscale": 0.396,
            "defaultxy": 20,
            "maxxy": 60,
            "filter_caps": {'u': 22.0, 'g': 22.2,'r': 22.2, 'i':21.3,
                            'z': 20.5},
            "magcount": 3,
            "maxmagdiff": 3
            }
        self._load()

    def _runInfo(self):
        """
        Reads runlist.par file and extracts startfield and endfield
        of a run. Runs are gotten from self._run attribute of instance
        """
        rl = files.runlist()
        w, = _np.where(rl['run'] == self._run)
        if len(w) == 0:
            raise ValueError("Run %s not found in runList.par" % self._run)
        startfield = rl[w]['startfield'][0]
        endfield = rl[w]['endfield'][0]
        return startfield, endfield

    def _getRuns(self):
        """
        Reads runlist.par file and returns a list of all runs.
        """
        rl = files.runlist()
        runs = rl["run"]
        if runs is None:
            raise ValueError("Unable to retrieve runs. Retrieved NoneType.")
        return runs

    def _load(self):
        """
        Parses the send kwargs to determine what selection users
        wants to process. Currently supported options are:
        run
        run-camcol
        run-filter
        run-filter-camcol
        camcol-filter
        camcol-frame
        field (full specification run-filter-camcol-frame)
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
        """
        Convenience function that runs process_field() for
        various inputs. Not using this function will void majority of
        error and exception handling.
        """

        if self._pick == "camcol-filter":
            runs = self._getRuns()
            for _run in runs:
                self._run=_run
                startfield, endfield = self._runInfo()
                for _field in range(startfield, endfield, 1):
                    process_field(self.results, self.errors,
                                  _run, self._camcol, self._filter, _field,
                                  self.params_bright, self.params_dim,
                                  self.params_removestars)
                    #print files.filename('frame', run=_run, camcol=self._camcol, filter=self._filter, field=_field)
            self._run=0


        if self._pick == 'run':
            startfield, endfield = self._runInfo()
            filters = ('u', 'g', 'r', 'i', 'z')
            camcols = (1, 2, 3, 4, 5, 6)
            for _camcol in camcols:
                for _filter in filters:
                    for _field in range (startfield, endfield, 1):
                        process_field(self.results, self.errors, self._run,
                                      _camcol, _filter, _field,
                                      self.params_bright, self.params_dim,
                                      self.params_removestars)
                        #print files.filename('frame', run=self._run, camcol=_camcol, filter=_filter, field=_field)

        if self._pick == 'run-filter':
            startfield, endfield = self._runInfo()
            camcols = (1, 2, 3, 4, 5, 6)
            for _camcol in camcols:
                for _field in range (startfield, endfield, 1):
                    process_field(self.results, self.errors, self._run,
                                  _camcol, self._filter, _field,
                                  self.params_bright, self.params_dim,
                                  self.params_removestars)
                    #print files.filename('frame', run=self._run, camcol=_camcol, filter=self._filter, field=_field)


        if self._pick == 'run-camcol':
            startfield, endfield = self._runInfo()
            filters = ('u', 'g', 'r', 'i', 'z')
            for _filter in filters:
                for _field in range (startfield, endfield, 50):
                    process_field(self.results, self.errors, self._run,
                                  self._camcol, _filter, _field,
                                  self.params_bright, self.params_dim,
                                  self.params_removestars)
                    #print files.filename('frame', self._run, self._camcol, filter=_filter, field=_field)


        if self._pick == 'run-camcol-filter':
            startfield, endfield = self._runInfo()
            for _field in range (startfield, endfield, 1):
                process_field(self.results, self.errors, self._run,
                              self._camcol, self._filter, _field,
                              self.params_bright, self.params_dim,
                              self.params_removestars)
                #print files.filename('frame', self._run, self._camcol, filter=self._filter, field=_field)

        if self._pick == 'camcol-frame':
            filters = ('u', 'g', 'r', 'i', 'z')
            for _filter in filters:
                process_field(self.results, self.errors, self._run,
                              self._camcol, _filter, self._field,
                              self.params_bright, self.params_dim,
                              self.params_removestars)
                #print files.filename('frame', self._run, self._camcol, filter=filter, field=self._field)


        if self._pick == 'field':
            process_field(self.results, self.errors, self._run,
                          self._camcol, self._filter, self._field,
                          self.params_bright, self.params_dim, 
                          self.params_removestars)
            #print files.filename('frame', self._run, self._camcol, filter=self._filter, field=self._field)

#        self.results.close()


