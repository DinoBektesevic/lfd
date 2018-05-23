"""
    Module:
        sdsspy.files

    Description:
        A set of functions for dealing with SDSS files, including reading files,
        finding file lists, getting run metadata, converting SDSS id numbers
        to strings, etc.

    Some Useful Functions.

        read(ftype, **keys)
            Read an SDSS file given the input file type and id info
            Id info can be
                run=, rerun=, camcol=...
            or
                photoid=
            or
                objid=

        filename(ftype, **keys)
            Generate an SDSS file name from input file type and id info

        filedir(ftype, **keys)
            Generate an SDSS dir path from input file type and id info

        filespec(ftype)
            Return the path specificition for the in input file type.  This information
            read from
                $PREFIX/share/sdssFileTypes.par

        file_list(ftype, **keys)
            Get lists of SDSS files based on id info.

        runlist()
            Return the sdss runlist.  This is read from $PHOTO_REDUX/runList.par
            This data is cached and only read once, so is preferable to using
            sdsspy.files.read('runList')

        expand_sdssvars(string, **keys):
            Convert environment variables and sdss vars, e.g. $RUNNUM, in file
            specifications to values.  Used to generate file locations.

        Routines for converting SDSS id numbers to strings:
            These functions return scalars for scalar input, otherwise lists.

            run2string(runs)
                Convert input run to a string padded to 6 zeros.
            field2string(fields)
                Convert input field to a string padded to 4 zeros.
            id2string(ids)
                Convert input id to string
            camcol2string(camcols, band=None)
                Convert input camcol to a string.
            filter2string(bands)
                Return alphabetic representation of filter
                  fstr = filter2string(2)      # returns 'r'
                  fstr = filter2string('2')    # returns 'r'
                  fstr = filter2string('r')    # returns 'r'
                  fstr = filter2string('R')    # returns 'r'

            rerun2string(reruns)
                Convert input rerun to string
            stripe2string(stripes)
                Convert input stripe to string

    Dependencies:
        numpy
        esutil for reading files and struct processing.


    Modification History:
        Documented: 2007-06-01, Erin Sheldon
"""
import os
import sys
from sys import stdout, stderr

import re
import glob

import numpy
from numpy import where


from .esutil.ostools import path_join
from .esutil.numpy_util import where1
from .esutil import io
from .esutil import ostools
from .esutil import sqlite_util

from .util import FILTERNUM, FILTERCHARS
from . import util
from . import yanny


def get_sdsspy_dir():
    sep=os.sep
    fs=__file__.split(sep)
    dir = '/'.join( fs[0:-1] )
    return dir

def read(ftype, run=None, camcol=None, field=None, id=None, **keys):
    """
    Module:
        sdsspy.files
    Name:
        read
    Purpose:
        Read an SDSS file given the input file type and id info
    Calling Sequence:
        Send the run,rerun,camcol etc.
            data=read(ftype, run=None, camcol=None, field=None, id=None, **keys)
        or send a skyserver objid
            data=read(ftype, objid=, **keys)
        or send a photoid
            data=read(ftype, photoid=, **keys)

    Example:
        data=read('psField', 756, 3, 125)
        data=read('psField', photoid=7560301301250035)
        data=read('psField', objid=1237648721210834979)
        imdict=read('fpAtlas', 756, 3, 125, 125, trim=True)


    Inputs:
        ftype:
            A file type, such as 'psField', 'fpAtlas', 'calibObj.gal'.  See
            $PREFIX/share/sdssFileTypes.par for a list of types.

            The ftype is case-insensitive.

    Keyword Inputs:

        NOTE: For run,camcol,field, *one and only one* of these can be a
        sequence.  You can also send globs such as '*' for these.

        run: 
            SDSS run id, needed for most files.
        camcol:
            SDSS camera column id
        field:
            SDSS field identifier
        id:
            SDSS id within a field.  E.g. the atlas reader requires an id.
        photoid: super id
            see sdsspy.util.photoid
        objid: super id
            see sdsspy.util.objid

        filter:
            SDSS filter id, such as 'u','g','r','i','z'.  You can also send
            an index [0,5] representing those.
        rerun:
            You normally don't have to specify the rerun, it can typically
            be determined from the run list.

        rows:
            A subset of the rows to return for tables.  Ignored if reading
            multiple files.
        columns: 
            A subset of columns to read.

        combine:
            When reading multiple files, the result is usually a list of
            results, one per file.  If combine=True, these are combined
            into a single structure.
        ensure_native:
            Ensure the data is in native byte order.
        lower, upper:
            If lower, make sure all field names are in lower case. Upper
            is the opposite.  Useful for reading outputs from IDL mwrfits
            which is all caps.
        trim:
            Trim atlas images.  See sdsspy.atlas.read_atlas for more info.
        ext:
            Which extension to read.  Some files, like psField files, are
            multi-extension.

        verbose: 
            Print the names of files being read.
    Other Keywords:
        These will probably be specific to a given file type. As an example:
        id=: SDSS id within a field.  Some user-defined file type may depend
            on the id

    """
    flist = file_list(ftype, run, camcol, field, id=id, **keys)

    if len(flist) == 0:
        return None

    lftype = ftype.lower()
    if lftype == 'fpatlas':
        return _read_atlas(flist, id=id, **keys)
    else:
        if is_yanny(flist[0]):
            return _read_yanny(flist, **keys)

        if len(flist) == 1:
            flist=flist[0]

        filter=keys.get('filter', None)
        ext=keys.get('ext', None)
        if ext is None:
            fs = filespec(ftype)
            if fs['ext'] > -1:
                ext=fs['ext']
                keys['ext'] = ext

        if lftype == 'psfield' and (ext != 6 or filter is not None):
            return _read_psfield(flist, **keys)

        return io.read(flist, **keys)

def filename(ftype, run=None, camcol=None, field=None, **keys):
    """
    Module:
        sdsspy.files
    Name:
        filename
    Purpose:
        Generate an SDSS file name from input file type and id info
    Calling Sequence:
        Send the run,rerun,camcol etc.
            fname=filename(ftype, run=None, camcol=None, field=None, **keys)
        or send a photoid
            fname=filename(ftype, photoid=, **keys)
        or send a skyserver objid
            fname=filename(ftype, objid=, **keys)

    Example:
        filename('psField', 756, 3, 125)


    Inputs:
        ftype:
            A file type, such as 'psField', 'fpAtlas', 'calibObj.gal'.  See
            $PREFIX/share/sdssFileTypes.par for a list of types.

            The ftype is case-insensitive.

    Keyword Inputs:

        NOTE: run,camcol,field can also be globs such as '*'

        run:
            SDSS run id, needed for most files.
        camcol:
            SDSS camera column id

        field:
            SDSS field identifier
        filter:
            SDSS filter id, such as 'u','g','r','i','z'.  You can also send
            an index [0,5] representing those.

        rerun:
            You normally don't have to specify the rerun, it can typically
            be determined from the run list.

        photoid: super id
            see sdsspy.util.photoid
        objid: super id
            see sdsspy.util.objid


    Other Keywords:
        These will probably be specific to a given file type. As an example:
        id=: SDSS id within a field.  Some user-defined file type may depend
            on the id

    """
    fs=FileSpec()
    return fs.filename(ftype, run, camcol, field, **keys)

def filedir(ftype, run=None, camcol=None, **keys):
    """
    Module:
        sdsspy.files
    Name:
        filedir
    Purpose:
        Generate an SDSS dir path from input file type and id info
    Calling Sequence:
        Send the run,rerun,camcol etc.
            dir=filedir(ftype, run=None, camcol=None, **keys)
        or send a photoid
            dir=filedir(ftype, photoid=, **keys)
        or send a skyserver objid
            dir=filedir(ftype, objid=, **keys)

    Example:
        filedir('psField', 756, 3)


    Inputs:
        ftype:
            A file type, such as 'psField', 'fpAtlas', 'calibObj.gal'.  See
            $PREFIX/share/sdssFileTypes.par for a list of types.

            The ftype is case-insensitive.

    Keyword Inputs:
        run:
            SDSS run id, needed for most files.
        camcol:
            SDSS camera column id

        rerun:
            You normally don't have to specify the rerun, it can typically
            be determined from the run list.

    Other Keywords:
        These will probably be specific to a given file type

    """

    fs=FileSpec()
    return fs.dir(ftype, run, camcol, **keys)

def filespec(ftype):
    """
    Module:
        sdsspy.files
    Name:
        filespec
    Purpose:
        Return the path specificition for the in input file type.  This information
        read from
            $PREFIX/share/sdssFileTypes.par
    Inputs:
        ftype:  The file type. The ftype is case-insensitive.

    Output:
        A dictionary with the file specification:
            'dir': A directory pattern, e.g. '$PHOTO_REDUX/$RERUN/$RUNNUM/objcs/$COL'
            'name': A name pattern, e.g. 'fpAtlas-$RUNSTR-$COL-$FIELDSTR.fit'
            'ftype': The file type, e.g. fpAtlas
            'ext': The extension.  Supported for fits files.
    """
    fs = FileSpec()
    return fs.filespec(ftype)


def is_yanny(fname):
    return fname[-4:] == '.par'

def _read_yanny(fname, **keys):
    if is_sequence(fname):
        if len(fname) > 1:
            raise ValueError("Only read one .par file at a time")
        fname=fname[0]
    verbose = keys.get('verbose',False)
    if verbose:
        stderr.write("Reading file: '%s'\n" % fname)

    if 'runList' in fname or 'sdssFileTypes' in fname:
        return yanny.readone(fname)
    elif 'sdssMaskbits' in fname:
        return yanny.read(fname)
    else:
        raise ValueError("Unexpected yanny .par file: '%s'" % fname)


def _read_psfield(fname, **keys):
    """

    This reader is designed to read extensions from a single file.  If you want
    to read multiple files extension 6 then just use the main read() function.

    """

    filter = keys.get('filter', None)
    if filter is None:
        ext = keys.get('ext', None)
        if is_sequence(ext):
            raise ValueError("only ask for a single filter/extension when reading "
                             "KL basis functions from a psField file")
        filter = ext+1
    else:
        if is_sequence(filter):
            raise ValueError("only ask for a single filter/extension when reading "
                             "KL basis functions from a psField file")

    if is_sequence(fname):
        raise ValueError("only ask for a single file when reading "
                         "psField KL basis functions")
        fname = fname[0]
    verbose=keys.get('verbose',False)
    pkl = atlas.PSFKL(fname, filter, verbose)
    return pkl


def _read_atlas(flist, **keys):
    import atlas
    trim = keys.get('trim',False)
    id = keys.get('id', None)
    verbose=keys.get('verbose', False)

    if 'photoid' in keys:
        ids=util.photoid_extract(keys['photoid'])
        id=ids['id']
    elif 'objid' in keys:
        ids=util.objid_extract(keys['objid'])
        id=ids['id']
    else:
        id=keys.get('id',None)
        if id is None:
            raise ValueError("You must enter id(s) to read fpAtlas files")

    if len(flist) > 1:
        raise ValueError("You can only read from one atlas image at a "
                         "time, %s requested" % len(flist))
    fname=flist[0]

    if is_sequence(id):
        if len(id) > 1:
            raise ValueError("You can only read one object at a time "
                             "from atlas images, %s requested" % len(id))
        id=id[0]

    if verbose:
        stderr.write("Reading id %s from '%s'\n" % (id,fname))
    imdict=atlas.read_atlas(fname, id, trim=trim)
    return imdict

class FileSpec:
    def __init__(self, reload=False):
        self.load(reload=reload)

    def load(self, reload=False):
        if not hasattr(FileSpec, '_filetypes') or reload:
            d=get_sdsspy_dir()
            d = os.path.join(d, 'share')
            f = os.path.join(d, 'sdssFileTypes.par')

            self._filetypes = yanny.readone(f)

            self._ftypes_lower = self._filetypes['ftype'].copy()
            for i in range(self._ftypes_lower.size):
                self._ftypes_lower[i] = self._ftypes_lower[i].lower()

    def reload(self):
        self.load(reload=True)

    def filespec(self, ftype):

        w,=numpy.where(self._ftypes_lower == ftype.lower().encode())
        if w.size == 0:
            raise ValueError("File type '%s' is unknown" % ftype)

        fs = {'ftype': str( self._filetypes['ftype'][w][0].decode()),
              'dir'  : str( self._filetypes['dir'][w][0].decode()  ),
              'name' : str( self._filetypes['name'][w][0].decode() ),
              'ext'  : int( self._filetypes['ext'][w][0]           )}
        return fs

    def dir_pattern(self, ftype):
        fs = self.filespec(ftype)
        return fs['dir']
    def name_pattern(self, ftype):
        fs = self.filespec(ftype)
        return fs['name']
    def file_pattern(self, ftype):
        fs = self.filespec(ftype)
        d = fs['dir']
        name=fs['name']
        path = os.path.join(d,name)
        return path

    def dir(self, ftype, run=None, camcol=None, **keys):
        p = self.dir_pattern(ftype)
        d = expand_sdssvars(p, run=run, camcol=camcol, **keys)
        return d
    def name(self, ftype, run=None, camcol=None, field=None, **keys):
        n = self.name_pattern(ftype)
        n = expand_sdssvars(n, run=run, camcol=camcol, field=field, **keys)
        return n
    def filename(self, ftype, run=None, camcol=None, field=None, **keys):
        f = self.file_pattern(ftype)
        f = expand_sdssvars(f, run=run, camcol=camcol, field=field, **keys)
        return f

_file_list_cache={}
def file_list(ftype, run=None, camcol=None, field=None, **keys):
    """
    Module:
        sdsspy.files
    Name:
        file_list
    Purpose:
        Get lists of SDSS files based on id info.
    Calling Sequence:
        Send the run,rerun,camcol etc.
            fl=file_list(ftype, run=None, camcol=None, field=None, **keys)
        or send a photoid
            fl=file_list(ftype, photoid=, **keys)
        or send a skyserver objid
            fl=file_list(ftype, objid=, **keys)

    Examples:
        # get atlas file for a given run, camcol, and field
        f=file_list('fpAtlas', 756, 3, 125)
        # get for a range of field
        f=file_list('fpAtlas', 756, 3, range(125,135))
        # get for all fields in the column
        f=file_list('fpAtlas', 756, 3, '*')
        # get for a given field and all columns
        f=file_list('fpAtlas', 756, '*', 125)

    Inputs:
        ftype: 
            A file type, such as 'psField', 'fpAtlas', 'calibObj.gal'.  See
            $PREFIX/share/sdssFileTypes.par for a list of types.

            The ftype is case-insensitive.

    Keyword Inputs:

        NOTE: For run,camcol,field, *one and only one* of these can be a
        sequence.  You can also send globs such as '*' for these.

        run: 
            SDSS run id, needed for most files.
        camcol:
            SDSS camera column id
        field:
            SDSS field identifier
        id:
            SDSS id within a field.  E.g. the atlas reader requires an id.
        filter:
            SDSS filter id, such as 'u','g','r','i','z'.  You can also send
            an index [0,5] representing those.
        rerun:
            You normally don't have to specify the rerun, it can typically
            be determined from the run list.

    Output:
        A list of files.  The output is always a list even if only one file
        is returned.

    """
    glob_pattern = keys.get('glob', None)
    if glob_pattern is None:
        if ftype is None:
            raise ValueError('send filetype and some id info or the full pattern on glob= keyword')


        run_is_sequence, camcol_is_sequence, field_is_sequence =_check_id_sequences(run,camcol,field)

        if run_is_sequence:
            flist=[]
            for trun in run:
                flist += file_list(ftype, trun, camcol, field, **keys)
            return flist

        if camcol_is_sequence:
            flist=[]
            for tcamcol in camcol:
                flist += file_list(ftype, run, tcamcol, field, **keys)
            return flist

        if field_is_sequence:
            flist=[]
            for tfield in field:
                flist += file_list(ftype, run, camcol, tfield, **keys)
            return flist

        fs=FileSpec()
        glob_pattern = fs.filename(ftype, run=run, camcol=camcol, field=field, **keys)

    # add * at the end to catch .gz files
    glob_pattern += '*'

    if glob_pattern not in _file_list_cache:
        #flist = glob.glob(glob_pattern)
        flist = _glob_pattern(glob_pattern)
        _file_list_cache[glob_pattern] = flist
    else:
        flist = _file_list_cache[glob_pattern]

    if len(flist) == 0:
        verbose=keys.get('verbose',False)
        if verbose:
            stderr.write("No matches for file pattern: %s\n" % glob_pattern)
    return flist

def _glob_pattern(pattern):
    if pattern.find('hdfs://') == 0:
        return _glob_hdfs_pattern(pattern)
    else:
        return glob.glob(pattern)

def _glob_hdfs_pattern(pattern):
    # must make an external call
    command = "hadoop fs -ls "+pattern+" | awk 'NF==8 {print $8}'"
    exit_code,stdo,stde=ostools.exec_process(command)
    if exit_code != 0:
        raise ValueError("Error executing command '%s': '%s'" % (command,stde))

    fl = stdo.split('\n')
    fl = ['hdfs://'+f for f in fl if f != '']

    return fl

def runlist():
    """
    Module:
        sdsspy.files
    Name:
        runlist
    Purpose:
        Return the sdss runlist.  This is read from $PHOTO_REDUX/runList.par
        This data is cached and only read once, so is preferable to using
        sdsspy.files.read('runList')

    Calling Sequence:
        rl = sdsspy.files.runlist()

    Outputs:
        A numpy array with fields. This is the typedef from the yanny .par file:
            typedef struct {
                int       run;        # Run number
                char      rerun[];    # Relevant rerun directory
                int       exist;      # Does a directory exist (has it ever been queued) (0/1)?
                int       done;       # Is this field done (0-Not done/1-Done)?
                int       calib;      # Is this field calibrated (0-No/1-Yes)?
                                      # All the fields below are only updated if the run is done
                                      # Otherwise, they are set to zero.
                int       startfield; # Starting field - determined from fpObjc present
                int       endfield;   # Ending field
                char      machine[];  # The machine the data is on
                char      disk[];     # The disk this run is on....
            } RUNDATA;

    """
    rl = RunList()
    return rl.data


class SimpleFileCache:
    """
    This is a base class for file caches.  Inherit from this and implement a
    .load() method.
    """
    def __init__(self, reload=False):
        self.load(reload=reload)

    def load(self, reload=False):
        """
        Over-ride this method, and replace SimpleCache below with your
        class name.
        """
        if not hassattr(SimpleFileCache, 'data') or reload:
            SimpleFileCache.data=None

    def reload(self):
        self.load(reload=True)

class RunList(SimpleFileCache):
    """
    This is a cache for the runList
    """
    def load(self, reload=False):
        if not hasattr(RunList, 'data') or reload:
            rl = read('runList')
            # remove duplicate, bad entry
            w=where1( (rl['run'] != 5194) | (rl['rerun'] == '301'))
            rl = rl[w]
            RunList.data = rl


def _check_id_sequences(run,camcol,field):
    run_is_sequence=False
    camcol_is_sequence=False
    field_is_sequence=False

    nseq=0
    if is_sequence(run):
        nseq += 1
        run_is_sequence=True
    if is_sequence(camcol):
        nseq += 1
        camcol_is_sequence=True
    if is_sequence(field):
        nseq += 1
        field_is_sequence=True

    # only one of run/camcol/field can be a sequence.
    if nseq > 1:
        raise ValueError("only one of run/camcol/field can be a sequence")

    return run_is_sequence, camcol_is_sequence, field_is_sequence

def is_sequence(var):
    if isinstance(var, (str)):
        return False

    try:
        l = len(var)
        return True
    except:
        return False


def find_rerun(run):
    rl = runlist()
    w,=numpy.where(rl['run'] == run)
    if w.size == 0:
        raise ValueError("Run %s not found in runList.par" % run)
    return rl['rerun'][w[0]].decode()

# convert sdss numbers to strings in file names and such
def stripe2string(stripes):
    """
    ss = stripe2String(stripes)
    Return the string version of the stripe.  9->'09'
    Range checking is applied.
    """
    return tostring(stripes, 0, 99)

def run2string(runs):
    """
    rs = run2string(runs)
    Return the string version of the run.  756->'000756'
    Range checking is applied.
    """
    return tostring(runs,0,999999)


def rerun2string(reruns):
    """
    rrs = rerun2string(reruns)
    Return the string version of the rerun.  No zfill is used.
    """
    return tostring(reruns)

def camcol2string(camcols):
    """
    cs = camcol2string(camcols)
    Return the string version of the camcol.  1 -> '1'
    Range checking is applied.
    """
    return tostring(camcols,1,6)

def field2string(fields):
    """
    fs = field2string(field)
    Return the string version of the field.  25->'0025'
    Range checking is applied.
    """
    return tostring(fields,0,9999)

def id2string(ids):
    """
    istr = id2string(ids)
    Return the string version of the id.  25->'00025'
    Range checking is applied.
    """
    return tostring(ids,0,99999)



filter_dict = {0: 'u',
               1: 'g',
               2: 'r',
               3: 'i',
               4: 'z',
               'u':'u',
               'g':'g',
               'r':'r',
               'i':'i',
               'z':'z',
               'irg':'irg'}

def filter2string(filter):
    """
    fstr = filter2string(filter)
    Return alphabetic representation of filter
      fstr = filter2string(2)      # returns 'r'
      fstr = filter2string('2')    # returns 'r'
      fstr = filter2string('r')    # returns 'r'
      fstr = filter2string('R')    # returns 'r'
    """

    if not numpy.isscalar(filter):
        # Scalar pars cannot be modified
        return [filter2string(f) for f in filter]

    if filter == '*':
        return '*'

    if filter not in filter_dict:
        raise ValueError("bad filter indicator: %s" % filter)

    return filter_dict[filter]

def tostring(val, nmin=None, nmax=None):
    if not numpy.isscalar(val):
        return [tostring(v,nmin,nmax) for v in val]

    if isinstance(val, str):
        return val

    if nmin is not None:
        if val < nmin:
            raise ValueError("Number ranges below min value of %s\n" % nmin)
    if nmax is not None:
        if val > nmax:
            raise ValueError("Number ranges higher than max value of %s\n" % nmax)


    if nmax is not None:
        nlen = len(str(nmax))
        vstr = str(val).zfill(nlen)
    else:
        vstr = str(val)

    return vstr






def expand_sdssvars(string_in, **keys):

    string = string_in

    if 'objid' in keys:
        objid=keys['objid']
        ids=util.objid_extract(objid)
        for k in ids:
            keys[k] = ids[k]
    elif 'photoid' in keys:
        photoid=keys['photoid']
        ids=util.photoid_extract(photoid)
        for k in ids:
            keys[k] = ids[k]

    # this will expand all environment variables, e.g. $PHOTO_SWEEP
    # if they don't exist, the result will be incomplete


    if string.find('$SDSSPY_DIR') != -1:
        sdsspy_dir=get_sdsspy_dir()
        string = string.replace('$SDSSPY_DIR', sdsspy_dir)

    if string.find('$RUNNUM') != -1:
        run=keys.get('run', None)
        if run is None:
            raise ValueError("run keyword must be sent: '%s'" % string)
        string = string.replace('$RUNNUM', tostring(run))

    if string.find('$RUNSTR') != -1:
        run=keys.get('run', None)
        if run is None:
            raise ValueError("run keyword must be sent: '%s'" % string)
        string = string.replace('$RUNSTR', run2string(run))

    if string.find('$RERUN') != -1:
        rerun=keys.get('rerun', None)
        if rerun is None:
            # try to determine from run number
            run = keys.get('run',None)
            if run is not None:
                try:
                    rerun = find_rerun(run)
                except ValueError as e:
                    err=str(e) + (", there may be no such run but you "
                                  "might try sending the rerun")
                    raise ValueError(err)

        if rerun is None:
            # try to determine rerun
            raise ValueError("rerun keyword must be sent: '%s'" % string)
        string = string.replace('$RERUN', tostring(rerun))


    if string.find('$COL') != -1:
        camcol=keys.get('camcol', None)
        if camcol is None:
            raise ValueError("camcol keyword must be sent: '%s'" % string)
        string = string.replace('$COL', camcol2string(camcol))

    if string.find('$FIELDSTR') != -1:
        field=keys.get('field', None)
        if field is None:
            raise ValueError("field keyword must be sent: '%s'" % string)
        string = string.replace('$FIELDSTR', field2string(field))


    if string.find('$IDSTR') != -1:
        id=keys.get('id',None)
        if id is None:
            raise ValueError("id keyword must be sent: '%s'" % string)
        string = string.replace('$IDSTR', id2string(id))

    if string.find('$ID') != -1:
        id=keys.get('id',None)
        if id is None:
            raise ValueError("id keyword must be sent: '%s'" % string)
        string = string.replace('$ID', tostring(id))

    if string.find('$FILTER') != -1:
        filter=keys.get('filter',None)
        if filter is None:
            band=keys.get('band',None)
            if band is None:
                raise ValueError("filter keyword must be sent (or band): '%s'" % string)
            filter=band
        string = string.replace('$FILTER', filter2string(filter))

    if string.find('$TYPE') != -1:
        type=keys.get('type',None)
        if type is None:
            raise ValueError("type keyword must be sent: '%s'" % string)
        string = string.replace('$TYPE', tostring(type))

    string = os.path.expandvars(string)

    # see if there are any leftover un-expanded variables.  If so
    # raise an exception
    if string.find('$') != -1:
        raise ValueError("There were unexpanded variables: '%s'" % string)

    return string

def array2sqlite(array, filename, tablename, **keys):
    """

    Convert the input array with fields into an sqlite table.
    
    Arrays with 5 elements are assumed to be associated with SDSS bands, and
    are renamed to col_u, col_g, ..., col_z. Thisis because sqlite does n ot
    support array columns.  Array columns with more or less than 5 elements are
    ignored for now.

    Keywords are passed on to the esutil.SqliteConnection.array2table method,
    e.g the create statement which drops an existing table.

    Parameters
    ----------
    array: numpy.ndarray
        An array with fields, aka recarray.
    filename: string
        The sqlite database file name
    tablename: string
        The name of the table.
    create: boolean
        Clobber existing tables.

    other keywords....

    Requirements
    ------------

    You need the sqlite3 python package installed, esutil installed.
    
    You also need the sqlite3 executable installed.  It is used for
    efficient "copy" of data into the table.

    """

    s = sqlite_util.SqliteConnection(filename)

    stderr.write("Creating sqlite input\n")
    t = _create_sqlite_input(array)

    stderr.write("Writing table '%s'\n" % tablename)
    s.array2table(t, tablename, **keys)

def _create_sqlite_input(st):
    bands = ['u','g','r','i','z']

    dtype=[]
    needs_converting=False
    for d in st.dtype.descr:
        name = str( d[0] )

        if len(d) == 3:
            needs_converting = True
            dims = d[2]
            if dims == 5:
                for filt in FILTERCHARS:
                    fname = name+'_'+filt
                    dtype.append((fname, d[1]))
        else:
            dtype.append(d)

    if not needs_converting:
        return st

    t = numpy.zeros(st.size, dtype=dtype)
    for d in st.dtype.descr:
        name = str( d[0] )

        if len(d) == 3:
            dims = d[2]
            if dims == 5:
                stderr.write("Splitting column '%s' by filter\n" % name)
                for filt in FILTERCHARS:
                    fnum = FILTERNUM[filt]
                    fname = name+'_'+filt
                    t[fname] = st[name][:, fnum]
            else:
                stderr.write("Ignoring column '%s'\n" % name)
        else:
            t[name] = st[name]

    return t
