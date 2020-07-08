import numpy as np
import matplotlib.pyplot as plt

from lfd.analysis.profiles.convolution import convolve
from lfd.analysis.profiles.objectprofiles import RabinaSource
from lfd.analysis.profiles.defocusing import FluxPerAngle
from lfd.analysis.profiles.seeing import GausKolmogorov
from lfd.analysis.profiles.consts import (SDSS,
                                          SDSSSEEING,
                                          LSST,
                                          LSSTSEEING,
                                          HEIGHTS)
from lfd.analysis.utils import search_cached


__all__ = ["get_rabina_profile", "meshgrid"]


def meshgrid(data, x, y, tgt, fold=None, axes=True):
    """Given a structured numpy array returns two 1D arrays and one 2D array.
    The two 1D arrays contain elements of data and represent the x and y axes,
    respectively, of the returned 2D. Similar to numpy's meshgrid. The 2D array
    containes target column data reshaped such that it matches the chosen x and
    y. Optionally, if there are multiple additional columns with  which the
    target data varies with, it is possible to "fold" over those columns; that
    is subselect only those elements of the target data that correspond to rows
    in the structured numpy array for which element values equal the given fold
    values.

    Parameters
    ----------
    data : `np.array`
        A structured array of data
    x : `str`
        A string representing the column that will be selected as the x axis.
        Must be a valid dtype name of data.
    y : `str`
        A string representing the column that will be selected as the y axis.
        Must be a valid dtype name of data.
    tgt : `str`
        A string representing the column that will be reshaped into 2D array
        matching the entries of x and y.
    fold : `dict`
        An optional dictionary of key:value pairs that represent column names
        and values on which to fold the total data on. Folding subselects
        particular target column elements of data based matched values provided
        in the dictionary.
    axes : `bool`
        If True, default, both axes and grid are returned. If false, only the
        gridded data is returned.

    Returns
    -------
    x : `np.array`
        A 1D array containing data elements that represent the x axis of the
        targeted reshaped data
    y : `np.array`
        A 1D array containing data elements that represent the y axis of the
        targeted reshaped data
    gridded : `np.array`
        A 2D array

    Examples
    --------
     >>> data
        array(
          [(3., 1., 5., 'DiskSource', 'GausKolmogorov', 'FluxPerAngle', 1.43, 8.1, 8.1, 3.5),  # noqa: W505
           (3., 1., 6., 'DiskSource', 'GausKolmogorov', 'FluxPerAngle', 1.43, 9.8, 9.8, 1.5),  # noqa: W505
           (3., 2., 5., 'DiskSource', 'GausKolmogorov', 'FluxPerAngle', 1.43, 4.5, 4.5, 2.6),  # noqa: W505
           (3., 2., 6., 'DiskSource', 'GausKolmogorov', 'FluxPerAngle', 1.43, 4.4, 4.4, 1.5),  # noqa: W505
           (4., 1., 5., 'DiskSource', 'GausKolmogorov', 'FluxPerAngle', 1.43, 8.1, 8.1, 3.5),  # noqa: W505
           (4., 1., 6., 'DiskSource', 'GausKolmogorov', 'FluxPerAngle', 1.43, 9.8, 9.8, 1.5),  # noqa: W505
           (4., 2., 5., 'DiskSource', 'GausKolmogorov', 'FluxPerAngle', 1.43, 4.5, 4.5, 2.6),  # noqa: W505
           (4., 2., 6., 'DiskSource', 'GausKolmogorov', 'FluxPerAngle', 1.43, 4.4, 4.4, 1.5)],  # noqa: W505
      dtype=[('fwhm', '<f8'), ('h', '<f8'), ('radius', '<f8'),
             ('source', '<U12'), ('seeing', '<U14'), ('defocus', '<U12'),
             ('sfwhm', '<f8'), ('dfwhm', '<f8'), ('ofwhm', '<f8'),
             ('depth', '<f8')])
    >>> x, y, z = meshgrid(meas, 'h', 'fwhm', 'ofwhm', fold={'radius':5})
    >>> x
    array([1., 2.])
    >>> y
    array([3., 4.])
    >>> z
    array([[8.1, 4.5],
         [8.1, 4.5]])
    """
    foldedData = data
    if fold is not None:
        for k, v in fold.items():
            foldedData = foldedData[foldedData[k] == v]

    xset = set(data[x])
    yset = set(data[y])
    xarr = np.fromiter(xset, float, len(xset))
    yarr = np.fromiter(yset, float, len(yset))
    xarr.sort()
    yarr.sort()

    xind = data.dtype.names.index(x)
    yind = data.dtype.names.index(y)
    if xind >= yind:
        gridded = foldedData[tgt].reshape((len(yset), len(xset)))
    else:
        gridded = foldedData[tgt].reshape((len(xset), len(yset))).T

    if axes:
        return xarr, yarr, gridded

    return gridded


def get_rabina_profile(angle, useCV2=False):
    """Returns image of projected Rabina profile as a function of angle between
    the observers line of sight and the velocity vector of the meteor.

    Parameters
    ----------
    angle: `float`
        angle, in radians, between LOS and vector of the meteor.
    useCV2: `bool`, optional
        If True will use cv2 to open the Rabina profile, otherwise matplotlib.
        Default is False.

    Notes
    -----
    Pre-rendered Rabina profiles exist for angles in 0.1 increments from 0 to
    1.5 inclusive. This is approximately every 6 degrees from 0 to 90 degrees.
    See `gen_rabina_profile.py` in persistent cache on how to pre-render
    Rabina profiles for other angles.
    Profiles are searched for in both ephemeral and persistent cache locations.
    If multiple matching files are found, those from peristent cache only are
    returned.

    Raises
    ------
    ValueError:
        when the given angle was not in the range 0-1.5 (step 0.1) inclusive.
    FileNotFoundError:
        when the searched for Rabina profile was not found. This can happen
        only when a 3rd party has manually cleared the persistent cache.
    """
    rounded = int(angle*10)
    if rounded not in range(0, 16, 1):
        raise ValueError("No premade Rabina profiles exist outside of the 0 to 1.5 radians!")

    rabinaPaths = search_cached(f"lfd_rabina{rounded}_r.png")
    if len(rabinaPaths) > 1:
        rabinaPaths = search_cached(f"lfd_rabina{rounded}_r.png", ephemeral=False)

    if useCV2:
        import cv2
        return cv2.imread(rabinaPaths[0], cv2.IMREAD_GRAYSCALE)
    return plt.imread(rabinaPaths[0])


def tableRabina(angle=1.5):
    for h in HEIGHTS:
        o = RabinaSource(angle, h)
        d = FluxPerAngle(h, *SDSS)

        ofwhm = o.calc_fwhm()

        c = convolve(o, d)
        dfwhm1 = c.calc_fwhm()

        o = RabinaSource(angle, h)
        s = GausKolmogorov(SDSSSEEING)
        d = FluxPerAngle(h, *SDSS)

        c = convolve(o, s, d)
        obsfwhm1 = c.calc_fwhm()

        o = RabinaSource(angle, h)
        d = FluxPerAngle(h, *LSST)

        c = convolve(o, d)
        dfwhm2 = c.calc_fwhm()

        o = RabinaSource(angle, h)
        s = GausKolmogorov(LSSTSEEING)
        d = FluxPerAngle(h, *LSST)

        c = convolve(o, s, d)
        obsfwhm2 = c.calc_fwhm()

        res = "{0}&\t{1:.2f}&\t{2:.2f}&\t{3:.2f}&\t{4:.2f}&\t{5:.2f}\\\\"
        print(res.format(int(h), ofwhm, dfwhm1, obsfwhm1, dfwhm2, obsfwhm2))
