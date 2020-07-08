"""A collection of various miscelaneous functionality that helps visualize the
profiles and results of convolutions and their numerical values.

"""
import itertools
import os.path as ospath
import contextlib
import warnings

import matplotlib.pyplot as plt

from lfd.analysis.profiles.samplers import generic_sampler
import lfd.analysis.utils as utils


__all__ = ["plot_profiles", "paperstyle", "set_ax_props", "get_ls",
           "get_style_path", "get_data_dir", "get_data_file",
           "create_data_file_name", "get_or_create_data"]


"""List of linestyles used in plots."""
LINESTYLES = ["solid", "dashed", "dashdot", "dotted", "-", "--", "-.", ":"]

"""Linestyle style counter."""
CUR_LS = 0


def get_data_dir():
    """Returns the path to data directory of utils module.
    """
    datadir = ospath.dirname(__file__)
    return ospath.join(datadir, "data")


def create_data_file_name(name):
    """Creates a filepath to a file in the data directory of
    utils module.
    The file might already exist. To retrieve a filepath to
    an already existing file use `get_data_file`.

    Parameters
    ----------
    name : str
        Name of the desired data file.

    Returns
    -------
    fpath : `str`
        Path to a file in the data directory.
    """
    return ospath.join(get_data_dir(), name)


def get_data_file(name):
    """Returns a path to an existing file in the data directory of
    utils module. If the file doesn't exist an OSError is raised.

    Parameters
    ----------
    name : str
        Name of the desired data file.

    Returns
    -------
    fname : `str`
        Returns a full data dir path of an existing file.
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
    """Function returns the next linestyle from linestyles
    to help out with graphing in for loops
    """
    global CUR_LS
    CUR_LS += 1
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
        yield c


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


def plot_profiles(ax, profiles, normed=True, **kwargs):
    """Normalizes all given profiles and then plots them on a given axis. Set
    normed to False if normalization is not desired. Lables are determined from
    the name attribute of the profile. `*args` and `**kwargs` are forwarded to
    the matplotlib plot function.
    """
    lss = kwargs.pop("linestyles", (False,)*len(profiles))
    cls = kwargs.pop("colors", (False, ) * len(profiles))
    lbls = kwargs.pop("labels", (False, ) * len(profiles))

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


def set_ax_props(axes, xlims=(), xticks=(), xlabels=(), ylims=((-0.01, 1.1), ),
                 ylabels=(),):
    """Sets the labels, ticks and limits on all pairs of axes,
    ticks and labels provided.

    Parameters
    ----------
    axes : `matplotlib.pyplot.Axes`
        Axes on which ticks, limits and labels will be set
    xlims : `list` or `tuple`
        Nested list or tuple of x-axis limits of the plots per axis.
        Default: (,).
    xticks : `list` or `tuple`
        Nested list or tuple of locations at which ticks and tick marks will be
        placed. Default: (,)
    xlabels : `list`, `tuple`, `string` or generator expression
        List, tuple or an iterable that provide a label for each of the axes
    ylims : `list` or `tuple`
        Nested list or tuple of y-axis limits of the plots per axis.
        Default: (-0.01, 1.1).
    ylabels : `list`, `tuple`, `string` or generator expression
        List, tuple or an iterable that provide a label for each of the axes

    Note
    ----
    Ticks and lims that are shorter than the number of axes will begin
    repeating themselves untill they match the length of axes.
    Given ticks and lims *NEED* to be nested list or tuples (i.e. list of
    lists, list of tuples, tuple of lists...) in order to work properly.
    Otherwise only a singular limit can be extracted from them and the limits
    can not be set properly.

    Ticks and lims can be any iterable that supports Python's
    multiplication trick (i.e. [1, 2]*2 = [1, 2, 1, 2]).
    Given ticks and lims that have length zero will not be set.

    The labels are expected to always be given for each axis. When only a
    string is given an attempt will be made to inspect and ascertain which axes
    are shared and which ones are on the edge of the figure and only those axes
    will be labeled. This procedure, however, is susceptible to errors - often
    in situations where additional axes holding colorbars are given. In that
    situation best course of action is to provide the labels as expected, one
    for each axis, even when they are all the same.
    """
    def pad_prop(prop, lentresh):
        """Given a prop and some numerical treshold returns (False,
        range(lentresh)) when the length of prop is zero and (True, prop) when
        the length of prop is different than zero.
        If a prop is shorter than the numerical treshold it will be padded
        to be at least as long (usually longer)."""
        # catch generators as limit expressions
        try:
            len(prop)
        except TypeError:
            prop = list(prop)

        setprop = False
        if len(prop) != 0:
            setprop = True
            if len(prop) < lentresh:
                prop *= lentresh
        else:
            # a fake prop return prevents the zip from truncating valid props
            prop = (prop,)*lentresh
        return setprop, prop

    # padding ticks and lims could be memory expensive
    # so we try not to expand if not needed.
    if isinstance(axes, plt.Axes):
        axlen = 1
        axes = (axes,)
    else:
        axlen = len(axes)

    setxticks, xticks = pad_prop(xticks, axlen)
    setxlims, xlims = pad_prop(xlims, axlen)
    setylims, ylims = pad_prop(ylims, axlen)
    for (ax, ticks, xlim, ylim) in zip(axes, xticks, xlims, ylims):
        if setxticks:
            ax.set_xticks(ticks)
        if setxlims:
            ax.set_xlim(xlim)
        if setylims:
            ax.set_ylim(ylim)

    # labels are complicated since not only do we need to know if we want to
    # set them, but for which axes we want to set them too.
    xlbls = (xlabels,) if isinstance(xlabels, str) else xlabels
    ylbls = (ylabels,) if isinstance(ylabels, str) else ylabels
    setxlabels, xlbls = pad_prop(xlbls, axlen)
    setylabels, ylbls = pad_prop(ylbls, axlen)

    # only clear-cut case happens when labels are given as lists matching the
    # axes list. Any other case is at least partially ambiguous. Still, attempt
    # is made to resolve the left/right-most axes only and label only those
    # when labels are pure strings. If this happens, setflags are left True
    # only for those axes that are not shared. This will fail if hidden axes,
    # f.e. such as colorbars, are added to the plot. It should, however, always
    # be safe to label border axes of the plot.
    if isinstance(xlabels, str):
        xgrouper = [ax for ax in axes[0].get_shared_x_axes()]
        setxlabels = False if len(xgrouper) != 0 else True
        axes[-1].set_xlabel(xlabels)
    if isinstance(ylabels, str):
        ygrouper = [ax for ax in axes[0].get_shared_y_axes()]
        setylabels = False if len(ygrouper) != 0 else True
        axes[0].set_ylabel(ylabels)

    for (ax, ticks, xlim, ylim, xlbl, ylbl) in zip(axes, xticks, xlims, ylims, xlbls, ylbls):
        if setxlabels:
            ax.set_xlabel(xlbl)
        if setylabels:
            ax.set_ylabel(ylbl)
        if setxticks:
            ax.set_xticks(ticks)
        if setxlims:
            ax.set_xlim(xlim)
        if setylims:
            ax.set_ylim(ylim)

    return axes


def get_or_create_data(filenames, samplerKwargs=None, samplers=None, cache=True, **kwargs):
    """Retrieves data stored in filename(s) or creates the data and stores it
    at given location(s). If the datafiles are just filenames the files are
    read and written to lfd's cache.

    Parameters
    ----------
    filenames : `list`, `tuple` or `str`
        Singular or a list of filepath(s) to existing files, or filename(s) of
        of already cached files.
    samplerKwargs : `list`, `tuple` or `dict`, optional
        Single or multiple dictionaries to pass to the sampler.
    samplers : `list`, `function`, optional
        Sampler(s) to invoke. By default `generic_sampler` is used.`
    cache : `bool`
        If True, data will be cached if it doesn't exist already.
    **kwargs : `dict`
        Optional. Any keywords are forwarded to the sampler.

    Returns
    -------
    data : `list`
       A list of numpy arrays containing the read, or created, data.


    Notes
    -----
    There is no difference between providing a single ``samplerArgs`` or giving
    the arguments as kwargs. When ``samplerArgs`` are a list, however, it is
    iterated over, and each element is passed as a kwarg to the sampler, while
    kwargs are passed to the sampler as-is on every iteration.
    """
    filenames = (filenames, ) if isinstance(filenames, str) else filenames

    if samplers is None:
        samplers = itertools.cycle((generic_sampler, ))
        kwargs["returnType"] = "grid"
        useGeneric = True

    if samplerKwargs is None:
        # neccessary to fool for loop that refuses to iterate over None's
        smplrKw = itertools.cycle(("dummyVal", ))
    elif isinstance(samplerKwargs, dict):
        smplrKw = itertools.cycle((samplerKwargs, ))
    else:
        smplrKw = samplerKwargs

    data = []
    for fname, samplerKwarg, sampler in zip(filenames, smplrKw, samplers):
        try:
            data.append(utils.get_data(fname))
        except FileNotFoundError:
            warnings.warn(f"Creating data file: '{fname}' - this might take a while.")
            if samplerKwargs is None:
                dat = sampler(**kwargs)
            else:
                dat = sampler(**samplerKwarg, **kwargs)

            if useGeneric:
                data.append(dat)
            else:
                data.append(dat)

            if cache:
                utils.cache_data(data[-1], fname)

    return data
