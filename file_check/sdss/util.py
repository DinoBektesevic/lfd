"""
Module
------
    sdsspy.util

Functions
---------
    get_photoid(run,rerun,camcol,field,id)
    get_photoid(array with fields):
        Create a 64-bit index from the id info.
    photoid_extract(superid): Extract run,rerun,camcol,field,id from
        a super id created using the get_photoid() function.

    get_objid(run,rerun,camcol,field,id,skyversion=2)
        similar to photoid, but this is the id used in the CAS.
        You can not just read off the run,rerun etc by looking
        at the id because bit shifts are used.
    objid_extract(superid): Extract run,rerun,camcol,field,id from
        a super id created using the get_objid() function.

    nmgy2mag(nmgy, ivar=None):
        Convert nano-maggies to log magnitude.  If ivar is sent, the tuple
        (mag, err) is returned.
    mag2nmgy(mag, magerr=None):
        Convert from magnitudes to nano-maggies.
    nmgy2lups(nmgy, ivar=None, band=None):
        Convert from nano-maggies to luptitudes, which are asinh based
        mags.

    make_cmodelflux(recarr):
        Combine dev and exp fluxes into a composite flux.  The basic
        formula is
            fc = (1-fracdev)*flux_exp + fracdev*flux_dev
    make_cmodelmag(recarr, doerr=True, dered=False, lups=False)
        Combine dev and exp fluxes into a composite flux, and then convert
        to mags.

    dered_fluxes(extinction, flux, ivar=None):
        Deredden fluxes using the 'extinction' given in mags by
        the SDSS pipeline.  It is slightly more precise to correct
        the fluxes before converting to mags.
 
"""
import numpy
from numpy import log10, log, sqrt, where, array

FILTERNUMS = [0,1,2,3,4]
FILTERCHARS = ['u','g','r','i','z']
FILTERNUM = {'u':0, 'g':1, 'r':2, 'i':3, 'z':4,
             0:0, 1:1, 2:2, 3:3, 4:4}

FILTERCHAR = {'u':'u', 'g':'g', 'r':'r', 'i':'i', 'z':'z',
              0:'u', 1:'g', 2:'r', 3:'i', 4:'z'}


def get_photoid(*args, **keys):
    """
    Name:
        get_photoid
    Purpose:
        Convert run,rerun,camcol,field,id to a single 64-bit superid
    Usage:
        pid = photoid(run,rerun,camcol,field,id)
        pid = photoid(recarray)
    Inputs:
        run,rerun,camcol,field,id: SDSS id info.  Note you can enter
            a subset as well as long as they occur in the expected
            order and you start with run, e.g. just run,rerun,camcol
            You must enter at least run,rerun

        OR

        recarray: An array with the fields run,rerun,camcol,field,id

    Keywords:
        old: If true, use the older set of exponents.  These
        old exponents were chosen poorly and should not be used
        for new ids.

    Outputs:
        A super id combining all the id info into a single 64-bit
        number.  This is done in such a way that you can read off
        the individual ids.  E.g. if id info is
            run: 1048
            rerun: 301
            camcol: 4
            field: 125
            id: 994
        Then the result is
            10480301401250994

        You can use the photoid_extract() function to extract
        the original id info.
    """

    def photoid_usage():
        raise ValueError("Send either run,rerun,camcol,field,id or "
                         "a recarray with those fields")

    nargs = len(args)
    if nargs == 0:
        photoid_usage()

    if nargs == 1:
        arg1 = args[0]
        if hasattr(arg1, 'dtype'):
            # see if this has the fields, if so call sphotoid
            names = arg1.dtype.names
            if names is not None:
                return sphotoid(arg1)
            else:
                photoid_usage()
        else:
            photoid_usage()


    # order: run,rerun,camcol,field,id
    #pvals = [15,12,11,6,0]
    # 6 for run
    # 4 for rerun
    # 1 for camcol
    # 4 for field
    # 4 for id
    old = keys.get('old',False)
    if not old:
        pvals = [13,9,8,4,0]
    else:
        pvals = [15,12,11,6,0]
    if nargs > 5:
        nargs=5

    is_scalar = _is_scalar(args[0])

    # make ten an array scalar with exactly 64 bits
    ten = numpy.array(10, dtype='i8')
    superid = None
    for i in range(nargs):
        arg = numpy.array(args[i], dtype='i8', copy=False, ndmin=1)

        if superid is None:
            superid = numpy.zeros(arg.size,dtype='i8')

        p = pvals[i]

        superid += arg*ten**p

    if is_scalar:
        superid = superid[0]
    return superid

def photoid(*args, **keys):
    """
    deprecated: use get_photoid()
    """
    return get_photoid(*args,**keys)


def sphotoid(arr, old=False):
    """
    This just extracts id info from an array with fields.  There is not
    need to call this directly since photoid will call sphotoid if needed.
    """
    names = arr.dtype.names
    if names is None:
        raise ValueError("array must have fields")

    args = []

    # we allow subsets from the left
    for name in ['run','rerun','camcol','field','id']:
        name_upp=name.upper()
        if name in names:
            tname=name
        elif name_upp in names:
            tname=name_upp
        else:
            break

        #tarr = numpy.array(arr[tname], dtype='i8', copy=False, ndmin=1)
        args.append(arr[tname])

    if len(args) == 0:
        raise ValueError("the struct must contain at least 'run'")
    args = tuple(args)
    return photoid( *args, old=old )

def photoid_extract(photoid, as_tuple=False, old=False):
    """

    Extract run,rerun,camcol,field,id from a photoid 
    
    By default Returns a dictionary keyed by run,rerun,...

    See the photoid() function for creating these super ids.

    parameters
    ----------
    superid: 
        A super id created using photoid().  Can be an array.
    as_tuple: bool, optional
        If True, return (run,rerun,camcol,field,id) instead
        of a dictionary
    old: bool, optional
        Assum the old version of exponents were used.
    """
    if not old:
        pvals = [13,9,8,4,0]
    else:
        pvals = [15,12,11,6,0]

    # make ten an array scalar with exactly 64 bits
    ten = numpy.array(10, dtype='i8')

    run = photoid/ten**pvals[0]

    rerun = photoid/ten**pvals[1] - run*ten**(pvals[0]-pvals[1])

    camcol = \
        photoid/ten**pvals[2] - \
        run*ten**(pvals[0]-pvals[2]) - \
        rerun*ten**(pvals[1]-pvals[2])

    field = \
        photoid/ten**pvals[3] - \
        run*ten**(pvals[0]-pvals[3]) - \
        rerun*ten**(pvals[1]-pvals[3]) - \
        camcol*ten**(pvals[2]-pvals[3])

    id =  \
        photoid/ten**pvals[4] - \
        run*ten**(pvals[0]-pvals[4]) - \
        rerun*ten**(pvals[1]-pvals[4]) - \
        camcol*ten**(pvals[2]-pvals[4]) - \
        field*ten**(pvals[3]-pvals[4])

    if as_tuple:
        return run,rerun,camcol,field,id
    else:
        return {'run':run,'rerun':rerun,
                'camcol':camcol,'field':field,
                'id':id}


def get_objid(*args, **keys):
    """
    Name:
        objid
    Purpose:

        Convert run,rerun,camcol,field,id (and possibly a "sky version") to a
        single 64-bit superid used in the CAS. Unlike photoid, one cannot
        simply read of the run,rerun,camcol,field,id values by looking at the
        id.

    Usage:
        oid = objid(run,rerun,camcol,field,id)
        oid = objid(recarray)
    Inputs:
        run,rerun,camcol,field,id: SDSS id info.
            You must enter at least run,rerun

        OR

        recarray: An array with the fields run,rerun,camcol,field,id

    Keywords:
        skyversion: A sky version, default 2.  You should never
            have to set this.

    """

    def objid_usage():
        raise ValueError("Send either run,rerun,camcol,field,id or "
                         "a recarray with those fields")

    nargs = len(args)
    if nargs == 0:
        objid_usage()

    is_scalar = _is_scalar(args[0])
    skyversion=keys.get('skyversion',2)
    if nargs == 1:
        arg1 = args[0]
        #if isinstance(arg1, numpy.ndarray):

        if hasattr(arg1, 'dtype'):
            if arg1.dtype.names is not None:
                if 'run' in arg1.dtype.names:
                    return objid(arg1['run'],arg1['rerun'],arg1['camcol'],
                                 arg1['field'],arg1['id'], skyversion=skyversion)
                elif 'RUN' in arg1.dtype.names:
                    return objid(arg1['RUN'],arg1['RERUN'],arg1['CAMCOL'],
                                 arg1['FIELD'],arg1['ID'], skyversion=skyversion)
                else:
                    raise ValueError("run not found in input recarray")
            else:
                objid_usage()
        else:
            objid_usage()

    elif nargs != 5:
        objid_usage()

    run,rerun,camcol,field,id = args

    dt = 'i8'
    sky    = numpy.array(skyversion, ndmin=1, dtype=dt, copy=False)
    run    = numpy.array(run, ndmin=1, dtype=dt, copy=False)
    rerun  = numpy.array(rerun, ndmin=1, dtype=dt, copy=False)
    camcol = numpy.array(camcol, ndmin=1, dtype=dt, copy=False)
    field  = numpy.array(field, ndmin=1, dtype=dt, copy=False)
    id     = numpy.array(id, ndmin=1, dtype=dt, copy=False)


    wbad, = where(  (sky < 0)     | (sky >= 16) 
                  | (rerun < 0)   | (rerun >= 2**11)
                  | (run < 0)     | (run >= 2**16)
                  | (camcol < 1)  | (camcol > 6) 
                  | (field < 0)   | (field >= 2**12) 
                  | (id < 0)      | (id >= 2**16) )

    if wbad.size > 0:
        raise ValueError("inputs out of bounds")

    superid = numpy.zeros(run.size, dtype=dt)

    first_field = numpy.zeros(run.size, dtype=dt)
    superid = (superid
               | (sky << 59)
               | (rerun << 48)
               | (run << 32)
               | (camcol << 29)
               | (first_field << 28)
               | (field << 16)
               | (id << 0) )

    if is_scalar:
        superid = superid[0]
    return superid

def objid(*args, **keys):
    """
    deprecated: use get_objid
    """
    return get_objid(*args, **keys)

def objid_extract(obj_id, full=False):
    masks={'sky_version':0x7800000000000000,
           'rerun':0x07FF000000000000,
           'run':0x0000FFFF00000000,
           'camcol':0x00000000E0000000,
           'first_field':0x0000000010000000,
           'field':0x000000000FFF0000,
           'id':0x000000000000FFFF}

    run=(obj_id & masks['run']) >> 32
    rerun=(obj_id & masks['rerun']) >> 48
    camcol=(obj_id & masks['camcol']) >> 29
    field=(obj_id & masks['field']) >> 16
    id=(obj_id & masks['id']) >> 0
    sky_version=(obj_id & masks['sky_version']) >> 59
    first_field=(obj_id & masks['first_field']) >> 28

    return {'run':run,
            'rerun':rerun,
            'camcol':camcol,
            'field':field,
            'id':id,
            'first_field':first_field,
            'sky_version':sky_version}

def nmgy2mag(nmgy, ivar=None):
    """
    Name:
        nmgy2mag
    Purpose:
        Convert SDSS nanomaggies to a log10 magnitude.  Also convert
        the inverse variance to mag err if sent.  The basic formulat
        is 
            mag = 22.5-2.5*log_{10}(nanomaggies)
    Calling Sequence:
        mag = nmgy2mag(nmgy)
        mag,err = nmgy2mag(nmgy, ivar=ivar)
    Inputs:
        nmgy: SDSS nanomaggies.  The return value will have the same
            shape as this array.
    Keywords:
        ivar: The inverse variance.  Must have the same shape as nmgy.
            If ivar is sent, then a tuple (mag,err) is returned.

    Outputs:
        The magnitudes.  If ivar= is sent, then a tuple (mag,err)
        is returned.

    Notes:
        The nano-maggie values are clipped to be between 
            [0.001,1.e11]
        which corresponds to a mag range of 30 to -5
    """
    nmgy = numpy.array(nmgy, ndmin=1, copy=False)

    nmgy_clip = numpy.clip(nmgy,0.001,1.e11)

    mag = nmgy_clip.copy()
    mag[:] = 22.5-2.5*log10(nmgy_clip)

    if ivar is not None:

        ivar = numpy.array(ivar, ndmin=1, copy=False)
        if ivar.shape != nmgy.shape:
            raise ValueError("ivar must be same shape as input nmgy array")

        err = mag.copy()
        err[:] = 9999.0

        w=where( ivar > 0 )

        if w[0].size > 0:
            err[w] = sqrt(1.0/ivar[w])

            a = 2.5/log(10)
            err[w] *= a/nmgy_clip[w]

        return mag, err
    else:
        return mag

def mag2nmgy(mag, magerr=None):
    """
    Name:
        mag2nmgy
    Purpose:
        Convert from magnitudes to nano-maggies.  The basic formula
        is 
            mag = 22.5-2.5*log_{10}(nanomaggies)
        The mag error can optionally be sent, in which case the inverse
        variance of the nanomaggies is returned.
    Calling Sequence:
        nmgy = mag2nmgy(mag)
        nmgy,ivar = mag2nmgy(mag, magerr=magerr)
            
    """
    mag = numpy.array(mag, ndmin=1, copy=False)

    nmgy = 10.0**( (22.5-mag)/2.5 )
    if magerr is not None:
        ivar = nmgy.copy()
        ivar[:] = 0.0

        w = numpy.where( (nmgy > 0) & (magerr > 0) )

        if w[0].size > 0:
            a = 2.5/log(10)
            ivar[w] = ( a/nmgy[w]/magerr[w] )**2

        return nmgy, ivar
    else:
        return nmgy

def nmgy2lups(nmgy, ivar=None, band=None):
    """
    Name:
        nmgy2lups
    Purpose:
        Convert from nano-maggies to luptitudes, which are asinh based
        mags.  The default parameters for SDSS are used.
    Calling Sequence:
        lup = nmgy2lups(nmgy)
        lup,err = nmgy2lups(nmgy, ivar=ivar)
    Inputs:
        nmgy: SDSS nanomaggies.  Can either be a [5,Nobj] array or
            an array for a single band, in which case the band must
            be given.
    Keywords:
        ivar: The inverse variance.  Must have the same shape as nmgy.
            If ivar is sent, then a tuple (lup,luperr) is returned.

    Outputs:
        The luptitudes as asinh values.  If ivar= is sent, a tuple
        is returned (lup,luperr)
    """
    s = nmgy.shape
    if ivar is not None:
        sivar = ivar.shape
        if len(sivar) != len(s):
            raise ValueError("ivar and fluxes must be same shape")
        for i in xrange(len(s)):
            if sivar[i] != s[i]:
                raise ValueError("ivar and fluxes must be same shape")

    if len(s) == 2:
        if s[1] != 5:
            raise ValueError("Either enter a 1-d array or a (nobj, 5) array")
        nband = 5
        band=[0,1,2,3,4]
    else:
        if band is None:
            raise ValueError("For 1-d input, specify a band in [0,4]")
        nband = 1
        try:
            if len(band) != 1:
                raise ValueError("for 1-d input, enter a single band")
        except:
            band = [band]

    # make sure band values makes sense
    for b in band:
        if b not in [0,1,2,3,4]:
            raise ValueError("band must be in [0,4]")

    lups = numpy.array( nmgy, copy=True )
    lups[:] = -9999.0
    if ivar is not None:
        lups_err = numpy.array(ivar, copy=True)
        lups_err[:] = -9999.0

    for b in band:
        if nband == 1:
            lups[:] = _nmgy2lups_1band(nmgy, b)
            if ivar is not None:
                lups_err[:] = _ivar2luperr_1band(nmgy, ivar, b)
        else:
            lups[:,b] = _nmgy2lups_1band(nmgy[:,b], b)
            if ivar is not None:
                lups_err[:,b] = _ivar2luperr_1band(nmgy[:,b], ivar[:,b], b)

    if ivar is not None:
        return lups, lups_err
    else:
        return lups

def lups2nmgy(lups, err=None, band=None):
    """
    Name:
        lups2nmgy
    Purpose:
        Convert from luptitudes to nano-maggies. The default parameters 
        for SDSS are used.
    Calling Sequence:
        nmgy= lups2nmgy(lups)
        nmgy,ivar= lups2nmgy(lups,err=err)
    Inputs:
        lups: The luptitudes as asinh values. Can either be a [5,Nobj] array or
         an array for a single band, in which case the band must
         be given.
    Keywords:
       err: uncertainty on the lups.  Must have the same shape as nmgy.
            If err is sent, then a tuple (nmgy,ivar) is returned.
    Outputs:
         SDSS nanomaggies. If err= is set then the inverse variance is returned
         as well as (nmgy,ivar)
    """
    s = lups.shape
    if err is not None:
        serr = err.shape
        if len(serr) != len(s):
            raise ValueError("err and lups must be same shape")
        for i in xrange(len(s)):
            if serr[i] != s[i]:
                raise ValueError("err and lups must be same shape")

    if len(s) == 2:
        if s[1] != 5:
            raise ValueError("Either enter a 1-d array or a (nobj, 5) array")
        nband = 5
        band=[0,1,2,3,4]
    else:
        if band is None:
            raise ValueError("For 1-d input, specify a band in [0,4]")
        nband = 1
        try:
            if len(band) != 1:
                raise ValueError("for 1-d input, enter a single band")
        except:
            band = [band]

    # make sure band values makes sense
    for b in band:
        if b not in [0,1,2,3,4]:
            raise ValueError("band must be in [0,4]")

    nmgy = numpy.array( lups, copy=True )
    nmgy[:] = -9999.0
    if err is not None:
        ivar = numpy.array(err, copy=True)
        ivar[:] = -9999.0

    for b in band:
        if nband == 1:
            nmgy[:] = _lups2nmgy_1band(lups, b)
            if err is not None:
                ivar[:] = _luperr2ivar_1band(lups, err, b)
        else:
            nmgy[:,b] = _lups2nmgy_1band(lups[:,b], b)
            if err is not None:
                ivar[:,b] = _luperr2ivar_1band(lups[:,b], err[:,b], b)

    if err is not None:
        return nmgy, ivar
    else:
        return nmgy

_bvalues=[1.4, 0.9, 1.2, 1.8, 7.4]
_log10 = numpy.log(10.0)

ln10_min10 = -23.02585
def _nmgy2lups_1band(nmgy, band):
    b=_bvalues[band]
    lups = 2.5*(10.0-numpy.log10(b)) - 2.5*numpy.arcsinh(5.0*nmgy/b)/_log10
    return lups

def _ivar2luperr_1band(nmgy, ivar, band):
    b=_bvalues[band]
    lups_err = numpy.array(ivar, copy=True)
    lups_err[:] = -9999.0
    w,=numpy.where(ivar > 0.0)
    if w.size > 0:
        terr = 1.0/numpy.sqrt(ivar[w])
        lups_err[w] = 2.5*terr
        lups_err[w] /= 0.2*b*_log10*numpy.sqrt(1.0 + (5.0*nmgy[w]/b)**2 )
    return lups_err

def _lups2nmgy_1band(lups, band):
    b=_bvalues[band]
    nmgy= b/5.*numpy.sinh(-lups*numpy.log(10.)/2.5-ln10_min10-numpy.log(b))
    return nmgy

def _luperr2ivar_1band(lups, err, band):
    b=_bvalues[band]
    df= b/5.*numpy.cosh(-lups*numpy.log(10.)/2.5-ln10_min10-numpy.log(b))\
        *err*numpy.log(10.)/2.5
    return 1./df**2.

def make_cmodelflux(objs, doivar=True):
    """
    Name:
        make_cmodelfllux
    Purpose:
        Combine dev and exp fluxes into a composite flux.  The basic
        formula is
            fc = (1-fracdev)*flux_exp + fracdev*flux_dev
    Calling Sequence:
        cmodel = make_cmodelflux(str, doiver=True)
    Inputs:
        str: A recarray with fields 'devflux','expflux' and one of 
            'fracdev' or 'fracpsf'.  fracpsf is allowed because
            the PHOTO pipeline now puts the value of fracdev into
            the old fracpsf field.
    Outputs:
        A [5,Nobj] array holding the composite model flux, or in
        the case that doivar=True a tuple (flux,ivar).
    """
    devflux = objs['devflux']
    expflux = objs['expflux']
    if 'fracdev' in objs.dtype.names:
        fracdev = objs['fracdev']
    else:
        fracdev = objs['fracpsf']

    if not doivar:
        flux = devflux*fracdev + expflux*(1.0-fracdev)
        return flux


    devflux_ivar = objs['devflux_ivar']
    expflux_ivar = objs['expflux_ivar']

    # get same shape, type
    flux = objs['devflux'].copy()
    ivar = objs['devflux'].copy()
    flux[:] = -9999.0
    ivar[:] = 0.0

    for band in [0,1,2,3,4]:
        bflux, bivar = _make_cmodelflux_1band(fracdev[:,band],
                                              devflux[:,band],
                                              devflux_ivar[:,band],
                                              expflux[:,band],
                                              expflux_ivar[:,band])
        flux[:,band] = bflux
        ivar[:,band] = bivar

    return flux, ivar

def _make_cmodelflux_1band(fracdev, dev, dev_ivar, exp, exp_ivar):
    fracexp = 1.0-fracdev

    flux = dev*fracdev + exp*fracexp

    ivar = exp.copy()
    ivar[:] = 0.0

    w,=where( (exp_ivar > 0) & (dev_ivar > 0) )
    if w.size > 0:
        # measurements are correlated... doing a weighted average
        err2 = fracdev[w]/dev_ivar[w] + fracexp[w]/exp_ivar[w]

        w2, = where( err2 > 0)
        if w2.size > 0:
            w=w[w2]
            ivar[w] = 1.0/err2[w2]

    return flux,ivar

def make_cmodelmag(objs, doerr=True, dered=False, lups=False):
    """
    Name:
        make_cmodelmag
    Purpose:
        Combine dev and exp fluxes into a composite flux.  The basic
        formula is
            fc = (1-fracdev)*flux_exp + fracdev*flux_dev
        Then convert the flux to mags using 
            mag = 22.5-2.5*log_{10}(fc)
    Calling Sequence:
        cmodelmag = make_cmodelmag(str, doerr=True, dered=False, lups=False)
    Inputs:
        str: A recarray with fields 'devflux','expflux' and one of 
            'fracdev' or 'fracpsf'.  fracpsf is allowed because
            the PHOTO pipeline now puts the value of fracdev into
            the old fracpsf field.

            If dred=True then the 'extinction' field must be present.
    Keywords:
        doerr: Return a tuple (mag,err)
        dered: Apply an extinction correction.
        lups: Return luptitudes instead of log mags.
    """

    if doerr:
        flux, ivar = make_cmodelflux(objs, doivar=True)

        if dered:
            flux, ivar = dered_fluxes(objs['extinction'], flux, ivar)
        if lups:
            mag, err = nmgy2lups(flux, ivar=ivar)
        else:
            mag, err = nmgy2mag(flux, ivar=ivar)
        return mag, err
    else:
        flux = make_cmodelflux(objs, doivar=False)

        if dered:
            flux = dered_fluxes(objs['extinction'], flux)
        if lups:
            mag = nmgy2lups(flux)
        else:
            mag = nmgy2mag(flux)
        return mag



def dered_fluxes(extinction, flux, ivar=None):
    """
    Adam says this is more accurate at the faint end.
    """
    exponent = 0.4*extinction
    flux_correct = (10.0**exponent)*flux

    if ivar is None:
        return flux_correct
    else:
        exponent = -0.8*extinction
        ivar_correct = (10.0**exponent)*ivar

        return flux_correct, ivar_correct










def sdss_wrap(ra):
    """
    Take all points with ra > 300 and put them at negative ra.
    This makes it easier to plot up ra and dec in the SDSS
    """
    ranew = numpy.array(ra, dtype='f8', copy=True, ndmin=1)
    w,=numpy.where(ra > 300)
    if w.size > 0:
        ranew[w] = ra[w]-360.0

    return ranew



def get_id_info(**keys):
    """
    Get id info based on a wide variety of possible inputs
    """
    import copy
    from . import files
    from . import util
    out=copy.deepcopy(keys)

    cat=keys.get('cat',None)
    if cat is not None:
        if len(cat['run'].shape)==0:
            tcat=cat
        else:
            tcat=cat[0]
        for k in ['run','rerun','camcol','field','id']:
            out[k] = tcat[k]
        out['objid'] = objid(tcat)
        out['photoid'] = photoid(tcat)
    elif 'objid' in keys:
        # for the title
        ids=util.objid_extract(keys['objid'])
        for k in ids:
            out[k] = ids[k]
        out['photoid'] = photoid(out['run'],out['rerun'],out['camcol'],
                                 out['field'],out['id'])
    elif 'photoid' in keys:
        # for the title
        ids=util.photoid_extract(keys['photoid'])
        for k in ids:
            out[k] = ids[k]
        out['objid'] = objid(out['run'],out['rerun'],out['camcol'],
                             out['field'],out['id'])

    elif 'run' in keys:
        out['run']=keys['run']
        if 'rerun' in keys:
            out['rerun']=keys['rerun']
        else:
            try:
                out['rerun']=files.find_rerun(out['run'])
            except:
                pass

        if 'camcol' in keys:
            out['camcol']=keys['camcol']
        if 'field' in keys:
            out['field']=keys['field']
        if 'id' in keys:
            out['id']=keys['id']

        if ('run' in out and 'rerun' in out 
                and 'camcol' in out and 'field' in out
                and 'id' in out):
            out['objid'] = objid(out['run'],out['rerun'],out['camcol'],
                                 out['field'],out['id'])
            out['photoid'] = photoid(out['run'],out['rerun'],out['camcol'],
                                     out['field'],out['id'])

    return out

def _is_scalar(obj):
    try:
        l=len(obj)
        return False
    except:
        return True
