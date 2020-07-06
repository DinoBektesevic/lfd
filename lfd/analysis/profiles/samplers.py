import warnings
import inspect
import itertools
import os.path
import glob

import numpy as np

from lfd.analysis.profiles.convolutionobj import ConvolutionObject
from lfd.analysis.profiles import consts
from lfd.analysis.profiles.objectprofiles import *
from lfd.analysis.profiles.seeing import *
from lfd.analysis.profiles.defocusing import *
from lfd.analysis.profiles.convolution import *
from lfd.analysis.profiles import *


__all__ = ["generic_sampler",]


def generic_sampler(sources, instrument=None, seeingProfile=GausKolmogorov,
                    seeingFWHM=None, defocusProfile=FluxPerAngle,
                    returnType='profiles', testRun=False, ntest=10, **kwargs):
    """Convolves given source profile(s) with defocusing and seeing effects
    and returns a list of observed profiles and, optionally, a structured array
    of profile parameters.

    Parameters
    ----------
    sources : `list` or `cls`
        List of classes or a single class that produces the object profile.
    instrument : `tuple` or `None`
        A tuple of diameters of primary and secondary mirrors of the used
        instrument in milimeters. See also `lfd.analysis.profiles.SDSS` or
        `lfd.analysis.profiles.LSST`.
    seeingProfile: `cls`, optional
        Class representing a seeing profile, by default
        `lfd.analysis.profiles.GausKolmogorov`.
    seeingFWHM: `list`, optional
        A list of full width half max values to use for seeing. If an
        instrument is LSST or SDSS and seeingProfile is provided will default
        to expected seeing FWHM or measured median seeing FWHM value
        respectively. See `lfd.analysis.profiles.LSSTSEEING` and
        `lfd.analysis.profiles.SDSSSEEING`.
    defocusProfile : `cls`
        Class representing a seeing profile, by default
        `lfd.analysis.profiles.FluxPerAngle`.
    returnType : `str`
        Chose values returned: profiles, grid measurements, or both by using
        "profiles", "grid" or "both" respectively. The default, `profiles`,
        returns a simple 1D list of profiles, `grid` also returns a 2D
        structured array containing input and resulting profile parameters.
    testRun : `bool`
        If true will print a table of ingoing arguments to the convolution
        function using the same combinations scheme. Usefull to verify whether
        the given convolution parameters actually match expected.
    ntests : `int`
        Number of sample points printed if testRun is True.
    **kwargs : `dict`
        Any additional provided keyword argument is used to create a Cartesian
        product of sample points which are then fed into the source, seeing and
        defocusing classes and convolved.

    Returns
    -------
    convProfiles : `list`
        List of python objects representing the result of profile convolutions.
    convMeas : `np.array`, optional
        A structured numpy array containing any of the following: any keywords
        that are given are stored under the key in which they were given,
        source profile name `source`, seeing profile name `seeing`, defocus
        profile name `defocus`, seeing FWHM, `sfwhm`, defocused FWHM `dfwhm`,
        observed FWHM `ofwhm`, per-cent value of the depth of central
        dip of the observed profile `depth`.

    Examples
    --------
    >>> convProfiles, convMeas = generic_sampler(sources=profiles.PointSource,
                                                 sfwhm=s, h=h, returnType='grid')
    """
    ########
    #       SANITIZE INPUT
    ########
    sources = [sources] if inspect.isclass(sources) else sources
    instrument = consts.SDSS if instrument is None else instrument

    if seeingProfile is None:
        # order of parameters here matters for the final output
        combinations = itertools.product(*kwargs.values(), sources)
    else:
        # using sfwhm avoids keyword conflicts with fwhm's for profiles
        seeingFWHM = kwargs.pop('sfwhm', seeingFWHM)

        errmsg = ("Requested convolution with seeing but no seeing FWHM given. "
                  "To skip seeing set seeingProfile to None, supply 'sfwhm' "
                  "keyword or set the instrument to LSST or SDSS.")
        if seeingFWHM is None:
            if instrument == consts.SDSS:
                seeingFWHM = [consts.SDSSSEEING,]
            elif instrument == consts.LSST:
                seeingFWHM = [consts.LSSTSEEING,]
            else:
                raise ValueError(errmsg)
        # make sure seeingFWHM is iterable, otherwise combinations will fail
        elif isinstance(seeingFWHM, float):
            seeingFWHM = [seeingFWHM, ]
        else:
            raise ValueError(errmsg)

        combinations = itertools.product(*kwargs.values(), seeingFWHM, sources)

    ########
    #       DRY RUN
    ########
    if testRun:
        stop = 0
        tmplstr = ('%-10s ' * (len(kwargs)+1)).rstrip()
        print(tmplstr % (*kwargs.keys(), "source"))
        for v in combinations:
            print(tmplstr % v )
            stop += 1
            if stop > ntest:
                break
        return

    ########
    #       CONVOLUTIONS
    ########
    convProfiles, sfwhm, dfwhm, ofwhm, depth = [], [], [], [], []
    keys = kwargs.keys()
    for x in combinations:
        convargs, seeingfwhm, source = [], x[-2], x[-1]
        srckwargs = {k:v for k,v in zip(keys, x[:-2])}

        # convolve can't accept a None, so create args list of profiles
        # name the individual profiles so we can calc FWHMs on them if needed
        O = source(**srckwargs, instrument=instrument)
        convargs.append(O)
        if defocusProfile is not None:
            D = defocusProfile(**srckwargs, instrument=instrument)
            convargs.append(D)
        if seeingProfile is not None:
            srckwargs.pop('fwhm', None)
            S = seeingProfile(fwhm=seeingfwhm, **srckwargs)
            convargs.append(S)

        C = convolve(*convargs)
        convProfiles.append(C)

        # don't waste time if we don't need measurements
        if 'grid' in returnType:
            if seeingProfile:
                sfwhm.append(seeingfwhm)
                #sfwhm.append(S.calc_fwhm())

            # if no seeing profile, the above convolutions FWHM is dfwhm, else
            # a new convolution is needed since the above will be ofwhm
            if defocusProfile and not seeingProfile:
                dfwhm.append(C.calc_fwhm())
            elif defocusProfile:
                C1 = convolve(O, D)
                dfwhm.append(C1.calc_fwhm())

            # ofwhm and depth should be a part of any measurement output
            ofwhm.append(C.calc_fwhm())
            mid = C.obj[int(len(C.obj)/2)]
            diff = C.peak-mid
            depth.append(diff/C.peak*100.0)

    ########
    #       SANITIZE OUTPUT
    ########
    if 'grid' in returnType or "both" in returnType:
        # Returned structured array has a column for each kwarg, i.e. each
        # function parameter iterated over, and leaves out parameters not
        # specifically iterated over. Order between keys and data matters and
        # it must match combinations above. First are kwargs (e.g height and
        # seeing), then various given profile names (a self-doc feature) and
        # then any of measurements (defocus and object FWHM and dept). This
        # order must be kept. This makes the following code a bit clumsy.
        # For zip in tuplegen to work correctly list len must match len of data
        # Ofwhm is guaranteed to exist, so that's what to use for padding len

        # First add a column for each kwarg
        addVals = []
        dt = [(k, float) for k in keys]

        onames = [getattr(s, "__name__") for s in sources]
        if seeingProfile:
            dt.append(("sfwhm", float))
            combinations = itertools.product(*kwargs.values(), seeingFWHM, onames)
        else:
            combinations = itertools.product(*kwargs.values(), onames)

        # Second, include a name col for each used profile class, source always
        # exists
        dt.append(("source", "<U12"))

        if seeingProfile:
            dt.append(("seeing", "<U14"))
            addVals.append([seeingProfile.__name__,]*len(ofwhm))

        if defocusProfile:
            dt.append(("defocus", "<U12"))
            addVals.append([defocusProfile.__name__,]*len(ofwhm))


        # Third, add a column for existing measurements
        keys = ('dfwhm', 'ofwhm', 'depth')
        vals = (dfwhm, ofwhm, depth)
        for k, v in zip(keys, vals):
            if len(v) > 0:
                dt.append((k, float))
                addVals.append(v)

        # Fourth, structured arrays require a list of tuples. Combinations is a
        # list of tuples but addVals is a list of lists. Merge them to a list
        # of tuples.
        tuplegen = ((*a, *b) for a, *b in zip(combinations, *addVals))

        # Finally, create a structured array and return
        convMeas = np.fromiter(tuplegen, dtype=dt, count=len(addVals[0]))

        if "both" in returnType:
            return np.array(convProfiles), convMeas
        return convMeas
    return np.array(convProfiles)
