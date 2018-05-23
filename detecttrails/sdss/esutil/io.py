"""
Some functions to simplify input and output to various file types.

The functions most users will use:

    read():
        Provide a single interface to read from a variety of file types.
        Supports reading from a list of files.
    read_header():
        Read just a header, if the file type suppots headers.  equivalent to
        read(..., header='only')

    write()
        Provide a single interface to write a variety of file types.
        Not yet implemented.

Created late 2009 Erin Sheldon, Brookhaven National Laboratory.  See docs
for individual methods for revision history.

"""

license="""
  Copyright (C) 2010  Erin Sheldon

    This program is free software; you can redistribute it and/or modify it
    under the terms of version 2 of the GNU General Public License as
    published by the Free Software Foundation.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""

import os
import copy
from sys import stdout, stderr


from . import numpy_util
from . import json_util
from . import ostools
from . import hdfs
from .hdfs import is_in_hdfs



try:
    import fitsio
    fits_package='fitsio'
except:
    try:
        import pyfits
        fits_package='pyfits'
    except:
        fits_package=None



try:
    import yaml
    have_yaml=True
except:
    have_yaml=False

def read_header(fileobj, **keys):
    """
    read the header from a file.

    This function is equivalent to io.read(.., header='only').  See the io.read
    function for a description of accepted keywords.

    """
    keys['header'] = 'only'
    return read(fileobj, **keys)

def read(fileobj, **keywords): 
    """
    Name:
        io.read

    Usage:
        import esutil
        data = esutil.io.read(
            filename/fileobject,
            typ=None,
            ext=0,
            rows=None, fields=None, columns=None,
            header=False, 
            combine=False, 
            view=None,
            lower=False, upper=False,
            noroot=True, seproot=False,
            verbose=False, 
            ensure_native=False)

    Purpose:
        Provide a single interface to read from a variety of file types.
        Supports reading from a list of files.


    Inputs:
        filename/fileobject:  
            File name or an open file object.  Can also be a sequence.  If a
            sequence is input, the return value will, by default, be a list of
            results.  If the return types are numpy arrays, one can send the
            combine=True keyword to combine them into a single array as long
            as the data types match.

    Keywords:
        type: 
            A string describing the file type, see below.  If this is not sent,
            then the file type is determined from the file extension.
        ext: 
            The file extension.  If multiple extensions are supported by the
            file type, such as for FITS, then use this keyword to select which
            is to be read. Default is the first extension with data.

        rows:  
            For numpy record-type files such as FITS binary tables or simple
            REC files, setting this keyword will return a subset of the rows.
            For FITS, this requires reading the entire file and selecting a
            subset.  For REC files only the requested rows are read from disk
            by using the recfile package.  Default is all rows.

        fields=, columns=:  
            For numpy record-type files such as FITS binary tables or simple
            REC files, return a subset of the columns or fields.  The keywords
            "fields" and "columns" are synonyms.  For FITS, this requires
            reading the entire file and selecting a subset.  For REC files only
            the requested rows are read from disk by using the recfile package.
            Default is all columns.

        header:  
            If True, and the file type supports header+data, return a tuple
            (data, header).  Can also be 'only' in which case only the header
            is read and returned (rec and fits only for now).  Default is
            False.

        combine:  If a list of filenames/fileobjects is sent, the default
            behavior is to return a list of data.  If combine=True and the
            data are numpy arrays, attempt to combine them into a single
            array.  Only works if the data types match.
        view:  If the result is derived from a numpy array, set this to
            pick the view.  E.g. pyfits returns a special pyfits type for
            binary table.  You can request a simple numpy array with fields
            by setting view=numpy.ndarray, or a numpy recarray type with
            view=numpy.recarray

        lower,upper:  For FITS files, if true convert the case of the
            fields to all lower or all upper.  Certain FITS writers
            tend to write all fields names as capitals which can result
            in annoyance.

        noroot:  For XML files, do not return the root name as the base
            name in the dictionary.  Default is True
        seproot: For XML files, return a tuple (data, rootname) instead of
            just the data under the root.

        ensure_native: For numpy arrays, make sure data is in native
            byte ordering.

    Currently Supported File Types:
        fits
            Flexible Image Transport System
        rec
            Simple ascii header followed by data in binary or text form. These
            files can be written/read using the esutil.sfile module.  REC files
            support appending rows.  Also supports reading sub-selections of
            rows and columns.
        xml
            Extensible Markup Language
        json
            JavaScript Object Notation.  Less flexible than XML but more useful
            in most practical situations such as storing inhomogeneous data in
            a portable way. 
        yaml
            A nice, human readable markup language, especially useful
            for configuration files.  YAML stands for
                YAML Ain't Markup Language
        pyobj
            A straight dump of an object to disk using it's repr().  Files are
            written using pprint, read simply using eval(open(file).read()).

            This is not secure so use with caution.


    Revision History:
        Use **keywords for input and for sending to all called methods. Much
        more flexible when adding new keywords and file types.
        2010
    """


    verbose = keywords.get('verbose', False)

    # If input is a sequence, read them all.
    if isinstance(fileobj, (list,tuple)):
        combine = keywords.get('combine', False)

        # a list was given
        alldata = []
        for f in fileobj:
            # note, only fields/columns is begin passed on but not rows
            # also note seproot is not being passed on
            data = read(f, **keywords) 
            alldata.append(data)

        if combine:
            if len(fileobj) == 1:
                alldata = alldata[0]
            else:
                fn,fobj,type,fs = _get_fname_ftype_from_inputs(fileobj[0], **keywords)
                if type == 'fits' or type == 'rec':
                    # this will only work if the all data has the 
                    # same structure
                    if verbose:
                        stderr.write("Combining arrays\n")
                    alldata = numpy_util.combine_arrlist(alldata)
        return alldata

    # a scalar was input
    fname,fobj,type,fs = _get_fname_ftype_from_inputs(fileobj, **keywords)

    if fs == 'hdfs':
        with hdfs.HDFSFile(fname, verbose=verbose) as hdfs_file:
            data = hdfs_file.read(read, **keywords)
        return data
    else:
        if verbose:
            stderr.write("Reading: %s\n" % fname)

    # pick the right reader based on type
    try:
        if type == 'fits':
            data = read_fits(fobj, **keywords)
        elif type == 'json':
            data = json_util.read(fobj, **keywords)
        elif type == 'yaml':
            data = read_yaml(fobj, **keywords)
        elif type == 'rec':
            data = read_rec(fobj, **keywords)
        elif type == 'xml':
            data = read_xml(fobj, **keywords)
        elif type == 'pyobj':
            data = read_pyobj(fobj, **keywords)
        else:
            raise ValueError("Don't know about file type '%s'" % type)
    finally:
        pass

    return data


def write(fileobj, data, **keywords):
    """
    Name:
        io.write
    Purpose:
        Provide a single interface to write a variety of file types.


    Usage:
        import esutil
        esutil.io.write(fileobj, data, **keywords)

    Inputs:
        filename/object:
            File name or an open file object.  If type= is not sent, file
            type is determined from the name of the file.
        data:
            Data that can be written to indicated file type. E.g. for 
            FITS files this should be a numpy array or a fits object.

    Optional Inputs:
        type:
            Indicator of the file type, e.g. 'fits', see below.  If None, the
            type is determined from the file name.
        header:
            If not None, write the header to the file if supported.

    There are other keywords for the individual writers.

    Currently Supported File Types:
        fits
            Flexible Image Transport System

            extra write keywords (if using fitsio)
                extname: a name for the new extension
                units: units for each column in tables
                compress: compression scheme for images
                header: a header to write
                clobber: remove any existing file
        rec
            Simple ascii header followed by data in binary or text form. These
            files can be written/read using the esutil.sfile module.  REC files
            support appending rows.  Also supports reading sub-selections of
            rows and columns.

            extra write keywords
                header: a header to write
                append: append rows instead of clobbering
                delim: If not None, write ascii data with the specified 
                    delimiter
                padnull:  When writing ascii, replace Null characters with spaces.
                ignorenull: When writing ascii, ignore Null characters. Note
                    you won't be able to read the data back in, but it is
                    useful for things like sqlite database input.

        xml
            Extensible Markup Language
        json
            JavaScript Object Notation.  Less flexible than XML but more useful
            in most practical situations such as storing inhomogeneous data in
            a portable way. 
        yaml
            A nice, human readable markup language, especially useful
            for configuration files.  YAML stands for
                YAML Ain't Markup Language
        pyobj
            A straight dump of an object to disk using it's repr().  Files are
            written using pprint, read simply using eval(open(file).read()).

            This is not secure so use with caution.


    """

    verbose = keywords.get('verbose', False)

    # a scalar was input
    fname,fobj,type,fs =_get_fname_ftype_from_inputs(fileobj, **keywords)

    if fs == 'hdfs':
        with hdfs.HDFSFile(fname, verbose=verbose) as hdfs_file:
            hdfs_file.write(write, data, **keywords)
        return

    try:
        # pick the right reader based on type
        if type == 'fits':
            write_fits(fobj, data, **keywords)
        elif type == 'yaml':
            write_yaml(fobj, data, **keywords)
        elif type == 'json':
            json_util.write(data, fobj, **keywords)
        elif type == 'rec':
            write_rec(fobj, data, **keywords)
        elif type == 'pyobj':
            data = write_pyobj(fobj, data, **keywords)
        else:
            raise ValueError("Need to implement writing file type: %s\n" % type)

        if fs == 'hdfs':
            hdfs_put(fobj, fname_hdfs, verbose=verbose)

    finally:
        pass

def read_fits(fileobj, **keywords):
    """
    Name:
        read_fits
    Purpose:
        Read data from a single fits file.
    Calling Sequence:
        data=read_fits(fileobj, **keywords)
    Inputs:
        fileobj: The file name/file object for a fits file.
    Keywords:
        ext: Which extension, or HDU, to read.  Default first with data.
        view: What view of the data to return. Default is numpy.ndarray
        header:  Return the data,header tuple?  Default False.
        rows:  Subset of the rows to return if reading a binary table extension.
        columns:  Subset of the columns to return if reading a binary table.
        fields: synonymous with columns
        lower: Force the field names to be lower case.
        upper: Force the field names to be upper case.
        ensure_native:  FITS always stores big-endian byte order.  Sending
            ensure_native=True forces the byte ordering to be machine native.
    Example:
        import esutil
        data=esutil.io.read('test.fits', ext=1, )
    """

    import numpy

    if fits_package is None:
        raise ImportError("Could not import fitsio or pyfits")

    if fits_package == 'fitsio':
        result = read_fits_fitsio(fileobj, **keywords)
    elif fits_package == 'pyfits':
        result = read_fits_pyfits(fileobj, **keywords)
    else:
        raise ValueError("expected fitsio or pyfits")

    h=None
    if isinstance(result,tuple):
        d,h = result
    elif keywords.get('header') == 'only':
        return result
    else:
        d = result

    lower= keywords.get('lower',False)
    upper= keywords.get('upper',False)

    if lower:
        d.dtype.names = [n.lower() for n in d.dtype.names]
    elif upper:
        d.dtype.names = [n.upper() for n in d.dtype.names]

    view = keywords.get('view',numpy.ndarray)
    if view is not None:
        d=d.view(view)

    ensure_native = keywords.get('ensure_native',False)
    if ensure_native:
        numpy_util.to_native(d, inplace=True)

    if h is not None:
        return d,h
    else:
        return d

def read_fits_fitsio(filename, **keywords):
    ext=keywords.get('ext',None)
    rows=keywords.get('rows',None)
    columns=keywords.get('columns',None)
    fields = keywords.get('fields', None)
    header=keywords.get('header',False)

    if columns is None and fields is not None:
        columns=fields

    return fitsio.read(filename,
                       ext=ext,
                       rows=rows,
                       columns=columns,
                       header=header)

def read_fits_pyfits(fileobj, **keywords):
    import numpy
    import pyfits
    header = keywords.get('header', False)
    rows=None
    fields=None
    columns=None

    if 'verbose' in keywords:
        del keywords['verbose']

    if 'rows' in keywords:
        rows=keywords['rows']
        del keywords['rows']

    if 'fields' in keywords:
        fields=keywords['fields']
        del keywords['fields']
    if 'columns' in keywords:
        columns=keywords['columns']
        del keywords['columns']

    if fields is None:
        if columns is not None:
            # allow columns to be synonymous with fields
            fields=columns

    if isinstance(fileobj,(str,unicode)):
        fileobj=ostools.expand_filename(fileobj)

    if 'ignore_missing_end' not in keywords:
        # the ignore_missing_end=True is for the multitude
        # of malformed FITS files out there
        keywords['ignore_missing_end'] = True

    if header == 'only':
        return pyfits.getheader(fileobj, **keywords)

    if header:
        d,h = pyfits.getdata(fileobj, **keywords)
    else:
        d = pyfits.getdata(fileobj, **keywords)

    view = keywords.get('view',numpy.ndarray)
    if view is not None:
        d = d.view(view)

    # extract subsets of the data
    if rows is not None:
        d = d[rows]

    if fields is not None:
        d = numpy_util.extract_fields(d.view(numpy.ndarray), fields)

    if header:
        return d,h
    else:
        return d


def write_fits(fileobj, data, **keys):
    verbose = keys.get('verbose', False)
    if verbose:

        if isinstance(fileobj,file):
            name=f.name
        else:
            name=fileobj

        stderr.write("Writing to: %s\n" % name)

    if fits_package == 'fitsio':
        write_fits_fitsio(fileobj, data, **keys)
    elif fits_package == 'pyfits':
        result = write_fits_pyfits(fileobj, data, **keys)
    else:
        raise ValueError("expected fitsio or pyfits")

def write_fits_fitsio(fileobj, data, **keys):
    extname=keys.get('extname',None)
    units=keys.get('units',None)
    compress=keys.get('compress',None)
    header=keys.get('header',None)
    clobber=keys.get('clobber',False)

    fitsio.write(fileobj, data, 
                 extname=extname,
                 units=units,
                 compress=compress,
                 header=header,
                 clobber=clobber)



def write_fits_pyfits(fileobj, data, **keys):
    import pyfits
    pyfits.writeto(fileobj, data, **keys)

def write_rec(fileobj, data, **keys):
    sfile.write(data, fileobj, **keys)



def read_rec(fileobj, **keys):
    import numpy
    header=keys.get('header',False)
    view=keys.get('view',numpy.ndarray)
    rows=keys.get('rows',None)
    columns=keys.get('columns',None)
    fields=keys.get('fields',None)
    ensure_native = keys.get('ensure_native',False)

    
    if header == 'only':
        return sfile.read_header(fileobj)

    # if dtype is sent, we assume there is no header at all
    dtype = keys.get('dtype',None)
    if dtype is not None:
        data = read_rec_plain(fileobj, **keys)
        header=False
    else:
        if header:
            data,hdr = sfile.read(fileobj, header=header, view=view, 
                                  rows=rows, fields=fields, columns=columns)
        else:
            data = sfile.read(fileobj, header=header, view=view, 
                              rows=rows, fields=fields, columns=columns)
    if ensure_native:
        numpy_util.to_native(data, inplace=True)

    if header:
        return data,hdr
    else:
        return data

def read_rec_plain(fileobj, **keys):
    from . import recfile
    with recfile.Recfile(fileobj,**keys) as rf:
        data = rf.read(**keys)
    return data

def read_xml(fileobj, **keywords):
    noroot=keywords.get('noroot',True)
    seproot=keywords.get('seproot',False)
    data = xmltools.xml2dict(fileobj, noroot=noroot, seproot=seproot)
    return data

def read_yaml(fileobj, **keywords):
    if isinstance(fileobj, (str,unicode)):
        return yaml.load(open(fileobj))
    elif isinstance(fileobj,file):
        return yaml.load(fileobj)
    else:
        raise ValueError("file must be a string or open file object")

def write_yaml(fileobj, data, **keywords):
    if isinstance(fileobj, (str,unicode)):
        return yaml.dump(data, open(fileobj,'w'))
    elif isinstance(fileobj,file):
        return yaml.dump(data, fileobj)
    else:
        raise ValueError("file must be a string or open file object")

def read_pyobj(fileobj, **keywords):
    if isinstance(fileobj, (str,unicode)):
        return eval(open(fileobj).read())
    elif isinstance(fileobj,file):
        return eval(fileobj.read())
    else:
        raise ValueError("file must be a string or open file object")

def write_pyobj(fileobj, data, **keywords):
    import pprint
    if isinstance(fileobj, (str,unicode)):
        pprint.pprint(data,stream=open(fileobj,'w'))
    elif isinstance(fileobj,file):
        pprint.pprint(data,stream=fileobj)
    else:
        raise ValueError("file must be a string or open file object")




def ftype2fext(ftype_input):
    ftype=ftype_input.lower()

    if ftype == 'fits' or ftype == 'fit':
        return 'fits'
    elif ftype == 'rec' or ftype == 'pya':
        return 'rec'
    elif ftype == 'json':
        return 'json'
    elif ftype == 'yaml':
        return 'yaml'
    elif ftype == 'xml':
        return 'xml'
    else:
        raise ValueError("Don't know about '%s' files" % ftype)

def fext2ftype(fext_input):

    fext=fext_input.lower()

    if fext == 'fits' or fext == 'fit':
        return 'fits'
    elif fext == 'rec' or fext == 'pya':
        return 'rec'
    elif fext == 'json':
        return 'json'
    elif fext == 'yaml':
        return 'yaml'
    elif fext == 'xml':
        return 'xml'
    elif fext == 'pyobj':
        return 'pyobj'
    else:
        raise ValueError("Don't know about files with '%s' extension" % fext)

def _get_fname_ftype_from_inputs(fileobj, **keywords):
    """
    Get filename, file type, and file system
    """

    fs='local'

    if isinstance(fileobj, file):
        fname = fileobj.name
        fobj = fileobj
    elif isinstance(fileobj, (str,unicode)):
        if is_in_hdfs(fileobj):
            fs='hdfs'

        # make sure we expand all ~username and other variables
        fname=ostools.expand_filename(fileobj)
        fobj = fname
    else:
        raise ValueError("Input must be a string or file object, or a "
                         "list thereof")


    ftype=None
    if 'type' in keywords:
        ftype=keywords['type']
    elif 'typ' in keywords:
        ftype = keywords['typ']

    if ftype is None:
        ftype=get_ftype(fname)
    ftype = ftype.lower()

    return fname, fobj, ftype, fs


def get_ftype(filename):
    fsplit = filename.split('.')
    if len(fsplit) == 1:
        raise ValueError("Could not determine file type file filename: '%s'" % filename)
    fext = fsplit[-1]
    if (fext == 'gz' or fext == 'bz' or fext == 'bz2') and len(fsplit) > 2:
        fext = fsplit[-2]
    typ = fext2ftype(fext)
    return typ


def fexists(fname):
    if is_in_hdfs(fname):
        return hdfs.exists(fname)
    else:
        return os.path.exists(fname)


