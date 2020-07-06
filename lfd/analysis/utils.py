"""A collection of various miscelaneous functionality that helps visualize the
profiles and other utilities.
"""
import os
import os.path as ospath
import glob
import time
import warnings

import numpy as np
import matplotlib.pyplot as plt

from lfd.analysis.profiles.convolution import convolve
from lfd.analysis.profiles.objectprofiles import *
from lfd.analysis.profiles.seeing import *
from lfd.analysis.profiles.consts import *


__all__ = ["PERSISTENT_CACHE", "EPHEMERAL_CACHE",
           "search_cached", "cache_data", "get_data"]


def get_cache_dirs(path=None, name="data"):
    """Returns the profiles module path. If name is given, joins the module
    path and the name.

    Parameters
    ----------
    name : `str`, optional
        If provided, name will be joined to the module path.
    """
    path = ospath.dirname(__file__) if path is None else path
    cacheList = []
    exclude_prefixes = ('__', '.')
    for dirpath, dirnames, filenames in os.walk(path):
        dirnames[:] = [dirname for dirname in dirnames
                       if not dirname.startswith(exclude_prefixes)]
        for dirname in dirnames:
            if dirname == name:
                cacheList.append(ospath.join(dirpath, dirname))

    return cacheList

PERSISTENT_CACHE = get_cache_dirs(name="data")
"""Cache for data that ships with lfd. Contains Rabina profiles as well as data
that recreates plots from published papers. This cache is not meant to be
written to be the user, for that see EPHEMERAL_CACHE."""

EPHEMERAL_CACHE = ospath.expanduser("~/.lfd")
"""Ephemeral cache is used for data created by the user. If it doesn't exist
one will be created at import."""
if not ospath.exists(EPHEMERAL_CACHE):
    os.makedirs(EPHEMERAL_CACHE)


def search_cached(name, ephemeral=True, persistent=True):
    """Returns a list of files matching the given name. By default both caches
    are searched. If no matches are found an error is raised.

    Params
    ------
    names: `str``
        Name of the desired data file.
    ephemeral: `bool`, optional
        Search ephemeral cache. True by default.
    persistent: `bool`, optional
        Search persistent cache. True by default.

    Raises
    ------
    FileNotFoundError:
        No cached files match given name.
    """
    ephemFiles, persistFiles = [], []
    if ephemeral:
        ephemFiles = glob.glob(ospath.join(EPHEMERAL_CACHE, '*'+name+'*'))
    if persistent:
        persistFiles = []
        for pcache in PERSISTENT_CACHE:
            persistFiles.extend(glob.glob(ospath.join(pcache, '*'+name+'*')))
    filePaths = ephemFiles + persistFiles

    if len(filePaths) != 0:
        return filePaths
    else:
        raise FileNotFoundError(f"File {name} does not exist in any cache.")


def get_rabina_profile(angle, useCV2=False):
    """Returns image of projected Rabina profile as a function of angle between
    the observers line of sight and the velocity vector of the meteor.

    Params
    ------
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


def cache_data(data, name):
    """Caches given array-like data under the given name. Utilizes numpy.save
    function to store the array like data.

    Use get_data to retrieve the saved array.

    Not thread safe.

    Parameters
    ----------
    data : `np.array`
        Array like object to save to cache. The EPHEMERAL_CACHE variable stores
        the location of the cache, by default at ~/.lfd/.
    name : `str`, `list` or `tuple`
        Name under which the data will be cached. If the name conflicts the
        current date will pre pre-pended to the name.
    """
    if isinstance(name, str):
        filename = (name, )
        data = (data, )

    for fname, data in zip(filename, data):
        try:
            paths = search_cached(fname)
        except FileNotFoundError:
            # no files with that name exist in either cache, all is well
            filepath = os.path.join(EPHEMERAL_CACHE, fname)
        else:
            # file with that name exists, rename and warn
            newname = time.strftime("%Y%m%d-%H%M%S") + fname
            warnings.warn(f"Filename {fname} exists, saving as {newname}")
            filepath = os.path.join(EPHEMERAL_CACHE, fname)

        np.save(filepath, data, allow_pickle=False)
        print(f"  File cached as {os.path.basename(filepath)}.")


def get_data(fname):
    """If fname is an existing file tries to load the data in it. If fname is a
    file name searches the cache for matches. If the match is unique, loads it.

    Parameters
    ----------
    fname : `str`
        File path or file name of the file to load. Does not support loading.

    Raises
    ------
    FileNotFoundError:
        When fname could not be found.
    """
    if os.path.isfile(fname):
        return np.load(fname, allow_pickle=False)

    filePaths = search_cached(fname)
    if len(filePaths) == 1:
        return np.load(filePaths[0], allow_pickle=False)
    elif len(filePaths) > 1:
        errmsg = "Multiple possible matches found. Which file were you looking for: \n"
        for fp in filePaths:
            errmsg += "    * {os.path.basename(fp)} \n"
        raise FileNotFoundError(errmsg)
