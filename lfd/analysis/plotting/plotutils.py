"""A collection of various miscelaneous functionality that helps visualize the
profiles and results of convolutions and their numerical values.

"""
import os.path as ospath
import contextlib

import matplotlib as mpl
import matplotlib.pyplot as plt


__all__ = ["plot_profiles", "get_ls", "get_style_path", "LINESTYLES", "CUR_LS"]



"""List of linestyles used in plots."""
LINESTYLES = ["solid", "dashed", "dashdot", "dotted", "-", "--", "-.", ":"]

"""Linestyle style counter."""
CUR_LS = 0


def get_data_dir():
    """Returns the path to data directory of plotutils module.
    """
    datadir = ospath.dirname(__file__)
    return ospath.join(datadir, "data")


def create_data_file_name(name):
    """Creates a filepath to a file in the data directory of
    plotutils module.
    The file might already exist. To retrieve a filepath to
    an already existing file use `get_data_file`.

    Params
    ------
    name : str
        Name of the desired data file.
    """
    return ospath.join(get_data_dir(), name)


def get_data_file(name):
    """Returns a path to an existing file in the data directory of
    plotutils module. If the file doesn't exist an OSError is raised.

    Params
    ------
    name : str
        Name of the desired data file.

    Raises
    ------
    error : OSError
        File of given name doesn't exist.
    """
    fullname = create_data_file_name(name)
    if ospath.exists(fullname):
        return fullname
    else:
        raise OSError(f"File {fullname} does not exist.")


def get_style_path():
    """Returns the path to the file defining the Matplotlib figure
    style in the paper.
    """
    return get_data_file("paperstyle.mplstyle")


def get_ls():
    """
    Function returns the next linestyle from linestyles
    to help out with graphing in for loops
    """
    global CUR_LS
    CUR_LS+=1
    if CUR_LS >= len(LINESTYLES):
        CUR_LS = 0
    return LINESTYLES[CUR_LS]


@contextlib.contextmanager
def paperstyle(after_reset=True):
    """Returns matplotlib style context that uses the same style
    as was in the paper.
    """
    stylepath = get_style_path()
    with plt.style.context(stylepath, after_reset) as c:
        yield


def plot_profile(ax, profile, normed=True, **kwargs):
    """Normalizes given profile and then plots them on a given axis. Set
    normed to False if normalization is not desired. Lables are determined from
    the name attribute of the profile. `*args` and `**kwargs` are forwarded to
    the matplotlib plot function.
    """
    if isinstance(normed, bool):
        # I don't want to invoke profile.norm on an object in case height needs
        # to be preserved.
        obj = profile.obj/profile.obj.max()
    else:
        obj = profile.obj/normed
    ls = kwargs.pop("linestyle", '-')
    lbl = kwargs.pop("label", profile.name)
    ax.plot(profile.scale, obj, label=lbl, linestyle=ls, **kwargs)
    return ax


def plot_profiles(ax, profiles,  normed=True,  **kwargs):
    """Normalizes all given profiles and then plots them on a given axis. Set
    normed to False if normalization is not desired. Lables are determined from
    the name attribute of the profile. `*args` and `**kwargs` are forwarded to
    the matplotlib plot function.
    """
    norms = (normed,)*len(profiles)
    lss = kwargs.pop("linestyles", (False,)*len(profiles))
    cls = kwargs.pop("colors", (False,)*len(profiles))
    lbls = kwargs.pop("labels", (False,)*len(profiles))

    plotprops = []
    for profile, label, color, linestyle in zip(profiles, lbls, cls, lss):
        kwarg = {}
        if label:
            kwarg["label"] = label
        if color:
            kwarg["color"] = color
        if linestyle:
            kwarg["linestyle"] = linestyle
        plotprops.append(kwarg)

    for profile, prop in zip(profiles, plotprops):
        plot_profile(ax, profile, normed, **prop, **kwargs)
    return ax
