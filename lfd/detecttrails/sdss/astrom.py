"""
Defines the class Astrom for converting between pixels and equatorial
coordinates.

Also defines eq2gc and gc2eq functions to convert between ra,dec and
"great circle" coordinates

"""

from numpy import where, array, cos, sin, arctan2, \
        arcsin, zeros, deg2rad, rad2deg, abs

err_ra, err_dec = float(), float()

class Astrom(object):
    """
    Conversions between pixel coordinates and equatorial coordinates.

    The intermediate step is the "great circle" coordinates mu,nu.

    init parameters
    ---------------
    All are keywords

    run:
        The run id
    camcol:
        The camera column id
    rerun: optional
        This will be found from the run if the run is in
        the runList.par file

    dependencies
    ------------
    * numpy
    * You need the photoField files for the run of interest.
    * For the inverse transforms from ra,dec to pixels you need
      scipy.  This is only imported if you attempt the inversion,
      so if you don't need the inversion you don't need scipy
      for import.
    """
    def __init__(self, **keys):
        from . import util

        self.keys=keys
        self.load()

    def pix2eq(self, field, filter, row, col, color=0.3):
        """
        convert from pixel coordinates (row,col) to equatorial coordinates
        (ra,dec)

        parameters
        ----------
        field: integer
            The SDSS field.
        row,col: scalar or arrays
            The pixel coords

        outputs
        -------
        ra,dec:
            The equatorial coords in degrees
        """

        mu,nu=self.pix2munu(field,filter,row,col,color=color)
        ra,dec=gc2eq(mu,nu,self._node, self._incl)
        return ra,dec

    def eq2pix(self, field, filter, ra, dec, color=0.3):
        """
        convert from equatorial coordinates (ra,dec) to pixel coordinates
        (row,col)

        parameters
        ----------
        field: integer
            The SDSS field.
        ra,dec:
            The equatorial coords in degrees

        outputs
        -------
        row,col: scalar or arrays
            The pixel coords
        """

        mu,nu = eq2gc(ra, dec, self._node, self._incl)
        row,col = self.munu2pix(field, filter, mu, nu, color=color)

        return row,col


    def munu2pix(self, field, filter, mu, nu, color=0.3):
        """
        Convert between SDSS great circle coordinates and
        pixel coordinates.

        Solve for the row,col that are roots of the equation

            row,col -> mu,nu

        This is because we only have the forward transform

        parameters
        ----------
        field: integer
            SDSS field number
        mu,nu:
            SDSS great circle coordinates in degrees

        outputs
        -------
        row,col:
            pixel values
        """

        import scipy.optimize
        mu,nu,are_scalar=get_array_args(mu,nu,"mu","nu")
        color=self._get_color(color, mu.size)

        trans=self.trans
        w=self._get_field(field)

        fnum=self._get_filter_num(filter)

        if 'f' in trans.dtype.names:
            fname='f'
        else:
            fname='ff'

        # pack away this data for the optimizer
        fd={'a':trans['a'][w,fnum],
            'b':trans['b'][w,fnum],
            'c':trans['c'][w,fnum],
            'd':trans['d'][w,fnum],
            'e':trans['e'][w,fnum],
            'f':trans[fname][w,fnum],
            'drow0':trans['drow0'][w,fnum],
            'drow1':trans['drow1'][w,fnum],
            'drow2':trans['drow2'][w,fnum],
            'drow3':trans['drow3'][w,fnum],

            'dcol0':trans['dcol0'][w,fnum],
            'dcol1':trans['dcol1'][w,fnum],
            'dcol2':trans['dcol2'][w,fnum],
            'dcol3':trans['dcol3'][w,fnum],

            'csrow':trans['csrow'][w,fnum],
            'cscol':trans['cscol'][w,fnum],
            'ccrow':trans['ccrow'][w,fnum],
            'cccol':trans['cccol'][w,fnum],
            'color0':trans['ricut'][w,fnum]}

        self._field_data=fd

        det = fd['b']*fd['f'] - fd['c']*fd['e']
        mudiff = mu - fd['a']
        nudiff = nu - fd['d']
        row_guess = ( mudiff*fd['f'] - fd['c']*nudiff )/det
        col_guess = ( fd['b']*nudiff - mudiff*fd['e'] )/det

        row=zeros(mu.size,dtype='f8')
        col=zeros(mu.size,dtype='f8')
        for i in xrange(mu.size):
            self._tmp_color=color[i]

            self._tmp_munu=array([mu[i],nu[i]])

            rowcol_guess=array([row_guess[i], col_guess[i]])

            rowcol = scipy.optimize.fsolve(self._pix2munu_for_fit, rowcol_guess)

            row[i] = rowcol[0]
            col[i] = rowcol[1]

        if are_scalar:
            row=row[0]
            col=col[0]

        return row,col


    def pix2munu(self, field, filter, row, col, color=0.3):
        """
        convert from row-column to SDSS great circle coordinates (mu,nu)

        parameters
        ----------
        field: integer
            The SDSS field.
        row,col: scalar or arrays
            The row,column in the field.

        outputs
        -------
        mu,nu:
            SDSS great circle coords in degrees
        """

        row,col,are_scalar=get_array_args(row,col,"row","col")
        color=self._get_color(color, row.size)

        trans=self.trans

        w=self._get_field(field)

        fnum=self._get_filter_num(filter)

        if 'f' in trans.dtype.names:
            fname='f'
        else:
            fname='ff'

        a = trans['a'][w,fnum]
        b = trans['b'][w,fnum]
        c = trans['c'][w,fnum]
        d = trans['d'][w,fnum]
        e = trans['e'][w,fnum]
        f = trans[fname][w,fnum]

        drow0 = trans['drow0'][w,fnum]
        drow1 = trans['drow1'][w,fnum]
        drow2 = trans['drow2'][w,fnum]
        drow3 = trans['drow3'][w,fnum]

        dcol0 = trans['dcol0'][w,fnum]
        dcol1 = trans['dcol1'][w,fnum]
        dcol2 = trans['dcol2'][w,fnum]
        dcol3 = trans['dcol3'][w,fnum]

        csrow = trans['csrow'][w,fnum]
        cscol = trans['cscol'][w,fnum]
        ccrow = trans['ccrow'][w,fnum]
        cccol = trans['cccol'][w,fnum]
        # ricut is a misnomer
        color0 = trans['ricut'][w,fnum]

        rowm=zeros(row.size,dtype='f4')
        colm=zeros(row.size,dtype='f4')
        wl,=where(color < color0)
        wh,=where(color >= color0)

        rowm = 0.5 + row+drow0+drow1*col+drow2*(col**2)+drow3*(col**3)
        colm = 0.5 + col+dcol0+dcol1*col+dcol2*(col**2)+dcol3*(col**3)
        if wl.size > 0:
            rowm[wl] += csrow*color[wl]
            colm[wl] += cscol*color[wl]
        if wh.size > 0:
            rowm[wh] += ccrow
            colm[wh] += cccol

        mu = a + b * rowm + c * colm
        nu = d + e * rowm + f * colm

        if are_scalar:
            mu=mu[0]
            nu=nu[0]

        return mu,nu

    def load(self):
        import esutil as eu
        from . import files
        from . import util

        keys=self.keys
        if 'run' not in keys or 'camcol' not in keys:
            raise ValueError("send run= and camcol=")

        self._run=keys['run']
        self._camcol=keys['camcol']
        fname=files.filename('photoField', **keys)

        h = eu.io.read_fits_fitsio(fname, ext=0, header='True')
        self._header=h[1]
        self._node=h[1]['node']
        self._incl=h[1]['incl']
        self._node_rad=deg2rad(self._node)
        self._incl_rad=deg2rad(self._incl)

        trans=eu.io.read(fname,lower=True)

        self.trans=trans


    def _pix2munu_for_fit(self, rowcol):
        """
        This is a version for the fitter only
        """
        row=rowcol[0]
        col=rowcol[1]
        fd=self._field_data

        rowm = (0.5 + row +
                fd['drow0']
                +fd['drow1']*col
                +fd['drow2']*(col**2)
                +fd['drow3']*(col**3) )

        colm = (0.5 + col
                +fd['dcol0']
                +fd['dcol1']*col
                +fd['dcol2']*(col**2)
                +fd['dcol3']*(col**3) )

        if self._tmp_color < fd['color0']:
            rowm += fd['csrow']*self._tmp_color
            colm += fd['cscol']*self._tmp_color
        else:
            rowm += fd['ccrow']
            colm += fd['cccol']

        diff=zeros(2,dtype='f8')
        diff[0] = fd['a'] + fd['b'] * rowm + fd['c'] * colm
        diff[1] = fd['d'] + fd['e'] * rowm + fd['f'] * colm

        diff[0] = abs(diff[0]-self._tmp_munu[0])
        diff[1] = abs(diff[1]-self._tmp_munu[1])

        return diff

    def _get_filter_num(self, filter):
        from . import util
        if filter is None:
            raise ValueError("send the filter")
        fnum=util.FILTERNUM[filter]
        return fnum

    def _get_field(self, field):
        w,=where(self.trans['field']==field)
        if w.size == 0:
            raise ValueError("field not found: %s" % field)
        index=w[0]

        return index

    def _get_color(self, color, size):
        color=array(color, dtype='f4', ndmin=1, copy=False)
        if color.size != size:
            if color.size == 1 and size > 1:
                color0=color.copy()
                color=zeros(size,dtype='f4')
                color[:] = color0[0]
            else:
                raise ValueError("color must be scalar or size "
                                 "%d, got %d" % (size,color.size))
        return color

def eq2gc(ra, dec, node, incl):
    """
    convert from equatorial (ra,dec) to SDSS great circle coordinates
    (mu,nu)

    parameters
    ----------
    ra,dec: scalar or arrays
        The equatorial coordinates in degrees
    node:
        node value in degrees
    incl:
        inclination value in degrees

    outputs
    -------
    mu,nu:
        The SDSS great circle coords in degrees
    """
    ra,dec,are_scalar=get_array_args(ra,dec,"ra","dec")

    rarad=deg2rad(ra)
    decrad=deg2rad(dec)

    noderad=deg2rad(node)
    inclrad=deg2rad(incl)

    cosdec=cos(decrad)
    ra_minus_node = rarad - noderad
    cosincl=cos(inclrad)
    sinincl=sin(inclrad)

    x1 = cos(ra_minus_node)*cosdec
    y1 = sin(ra_minus_node)*cosdec
    z1 = sin(decrad)

    x2 = x1
    y2 = y1*cosincl + z1*sinincl
    z2 =-y1*sinincl + z1*cosincl

    mu = arctan2(y2, x2) + noderad
    nu = arcsin(z2)

    rad2deg(mu,mu)
    rad2deg(nu,nu)

    atbound2(nu, mu)

    if are_scalar:
        mu=mu[0]
        nu=nu[0]

    return mu,nu

def gc2eq(mu, nu, node, incl):
    """
    convert from SDSS great circle coordinates (mu,nu) to equatorial
    (ra,dec)

    parameters
    ----------
    mu,nu: scalar or arrays
        The great circle coordinates in degrees
    node:
        node value in degrees
    incl:
        inclination value in degrees


    outputs
    -------
    ra,dec:
        Equatorial coordinates in degrees
    """

    mu,nu,are_scalar=get_array_args(mu,nu,"mu","nu")

    murad=deg2rad(mu)
    nurad=deg2rad(nu)
    noderad=deg2rad(node)
    inclrad=deg2rad(incl)
    
    cosnu=cos(nurad)
    mu_minus_node=murad-noderad
    x2 = cos(mu_minus_node)*cosnu
    y2 = sin(mu_minus_node)*cosnu
    z2 = sin(nurad)

    cosincl=cos(inclrad)
    sinincl=sin(inclrad)
    y1 = y2*cosincl - z2*sinincl
    z1 = y2*sinincl + z2*cosincl

    ra = arctan2(y1, x2) + noderad
    dec = arcsin(z1)

    rad2deg(ra,ra)
    rad2deg(dec,dec)

    atbound2(dec, ra)

    if are_scalar:
        ra=ra[0]
        dec=dec[0]

    return ra, dec


def atbound(angle, minval, maxval):

    while True:
        w,=where(angle < minval)
        if w.size==0:
            break
        angle[w] += 360.0

    while True:
        w,=where(angle >= maxval)
        if w.size==0:
            break
        angle[w] -= 360.0


def atbound2(theta, phi):

    atbound( theta, -180.0, 180.0 )
    w, = where( abs(theta) > 90.)
    if w.size > 0:
        theta[w] = 180. - theta[w]
        phi[w] = phi[w] + 180.

    atbound( theta, -180.0, 180.0 )
    atbound( phi, 0.0, 360.0 )

    w,=where( abs(theta) == 90. )
    if w.size > 0:
        phi[w] = 0.0



def get_array_args(x1, x2, name1, name2):
    is_scalar1=_is_scalar(x1)
    is_scalar2=_is_scalar(x2)

    if is_scalar1 != is_scalar2:
        mess="%s and %s must both be scalar or array"
        mess = mess % (name1,name2)
        raise ValueError(mess)

    x1=array(x1,copy=False,dtype='f8',ndmin=1)
    x2=array(x2,copy=False,dtype='f8',ndmin=1)

    if x1.size != x2.size:
        mess="%s and %s must both be same length.  got %s and %s"
        mess = mess % (name1,name2,x1.size,x2.size)
        raise ValueError(mess)

    return x1,x2,is_scalar1



def _is_scalar(obj):
    try:
        l=len(obj)
        return False
    except:
        return True
