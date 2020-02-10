"""A collection of various miscelaneous functionality that helps visualize the
profiles and other utilities.
"""
import matplotlib.pyplot as plt

from lfd.analysis.profiles.convolution import convolve
from lfd.analysis.profiles.objectprofiles import *
from lfd.analysis.profiles.seeing import *
from lfd.analysis.profiles.consts import *
import os.path as ospath

__all__ = ["get_rabina_dir", "get_rabina_path", "get_premade_rabina_profile"]

def get_rabina_dir():
    """Returns the directory containing the pre-rendered Rabina
    profile images.
    """
    curdir = ospath.dirname(__file__)
    return ospath.join(curdir, "rabina")


def get_rabina_path(angle):
    """Returns the full path to the PNG image containing the
    projection of the Rabina profile. An angle between the
    observers line of sight and the velocity vector of the
    meteor is required to fully specify the desired profile.

    Params
    ------
    angle - angle in radians between observer LOS and vel.
        vector of the meteor.

    Notes
    -----
    Pre-rendered Rabina profiles exist for angles in 0.1
    increments from 0 to 1.5 inclusive. This is approximately
    every 6 degrees from 0 to 90 degrees. See `gen_rabina_profile.py`
    in the same directory on how to pre-render Rabina profiles
    for other angles.

    Raises
    ------
    ValueError - if the given angle was not one of the allowed
        values in the 0 to 1.5 range inclusive.
    """
    rabinadir = get_rabina_dir()
    if 10*angle not in range(0, 16, 1):
        raise ValueError("No premade Rabina profiles exist outside of the 0 to 1.5 radians!")
    imgname = "lfd_img{0}_r.png".format(int(angle*10))
    return ospath.join(rabinadir, imgname)


def get_premade_rabina_profile(angle):
    """Returns the image of projected Rabina profile as an
    numpy array. An angle between the observers line of sight
    and the velocity vector of the meteor is required.

    Params
    ------
    angle - angle in radians between observer LOS and vel.
        vector of the meteor.

    Notes
    -----
    Pre-rendered Rabina profiles exist for angles in 0.1
    increments from 0 to 1.5 inclusive. This is approximately
    every 6 degrees from 0 to 90 degrees. See `gen_rabina_profile.py`
    in the same directory on how to render Rabina profiles
    for other angles.

    Raises
    ------
    ValueError - if the given angle was not one of the allowed
        values in the 0 to 1.5 range inclusive.
    """
    return plt.imread(get_rabina_path(angle))


def tableRabina(angle=1.5):
    profile = get_prerendered_rabina_profile_path(angle)
    for h in HEIGHTS:
        o = RabinaSource(profile, h)
        d = FluxPerAngle(h, *SDSS)

        ofwhm = o.calc_fwhm()

        c = convolve(o, d)
        dfwhm1 = c.calc_fwhm()

        o = RabinaSource(profile, h)
        s = GausKolmogorov(SDSSSEEING)
        d = FluxPerAngle(h, *SDSS)

        c = convolve(o, s, d)
        obsfwhm1 = c.calc_fwhm()

        o = RabinaSource(profile, h)
        d = FluxPerAngle(h, *LSST)

        c = convolve(o, d)
        dfwhm2 = c.calc_fwhm()

        o = RabinaSource(profile, h)
        s = GausKolmogorov(LSSTSEEING)
        d = FluxPerAngle(h, *LSST)

        c = convolve(o, s, d)
        obsfwhm2 = c.calc_fwhm()

        res = "{0}&\t{1:.2f}&\t{2:.2f}&\t{3:.2f}&\t{4:.2f}&\t{5:.2f}\\\\"
        print(res.format(int(h), ofwhm, dfwhm1, obsfwhm1, dfwhm2, obsfwhm2))

