import os
import warnings
import itertools

from matplotlib import rcParams
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np

from lfd.analysis import profiles
from lfd.analysis.profiles import (convolve, FluxPerAngle, GausKolmogorov,
                                   PointSource, DiskSource, RabinaSource,
                                   GaussianSource)
from lfd.analysis.plotting import plotutils
from lfd.analysis.plotting.plotutils import plot_profile, plot_profiles, get_ls


def set_ax_props(axes, xlims=(), xticks=(), xlabels=(), ylabels=(),
                 ylims =((-0.01, 1.1),)):
    """Sets the labels, ticks and limits on all pairs of axes,
    ticks and labels provided.

    Params
    ------
    axes : `matplotlib.pyplot.Axes`
        Axes on which ticks, limits and labels will be set
    xticks : `list` or `tuple`
        Nested list or tuple of locations at which ticks and tick
        marks will be placed. Default: (,)
    xlims : `list` or `tuple`
        Nested list or tuple of x-axis limits of the plots per axis.
        Default: (,).
    ylims : `list` or `tuple`
        Nested list or tuple of y-axis limits of the plots per axis.
        Default: (-0.01, 1.1).

    Note
    ----
    Ticks and lims that are shorter than the number of axes will
    begin repeating themselves untill they match the longest given
    prop.

    Given ticks and lims *NEED* to be nested list or tuples (i.e.
    list of lists, list of tuples, tuple of lists etc..) in order to
    work properly. Otherwise only a singular limit can be extracted
    from them.

    Ticks and lims can be any iterable that supports Python's
    multiplication trick (i.e. [1, 2]*2 = [1, 2, 1, 2]).

    Given ticks and lims that have length zero will not be set.
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
    for (ax, ticks, xlim, ylim)  in zip(axes, xticks, xlims, ylims):
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

    for (ax, ticks, xlim, ylim, xlbl, ylbl)  in zip(axes, xticks, xlims, ylims, xlbls, ylbls):
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


def figure4(h=100):
    """Effects of seeing on the observed intensity profile of a point source
    located 100km from the imaging instrument. Line types represent results
    based on different seeing values (as shown in the legend). The profile’s
    inner structure (a dip in the middle) is reduced or completely lost as
    the seeing worsens. SDSS is more affected because it has a smaller
    telescope aperture than LSST. The overall effect is similar even for
    much smaller distances to the meteor (see also Fig. 23, 24 and 26).

    Parameters
    ----------
    h : `int` or `float`
        Distance to the meteor head from the observer in kilometers. By default
        a 100km to match the figures in the paper.

    Returns
    -------
    fig : `matplotlib.pyplot.Figure`
        Figure containing the plot.
    ax : `matplotlib.pyplot.Axes`
        Axes containing the plot.
    """
    fig, axes = plt.subplots(1, 2, sharey=True, figsize=(10, 10))
    axes[0].text(-1.2, 1.03,  'SDSS', fontsize=rcParams["axes.titlesize"])
    axes[1].text(-3.35, 1.03, 'LSST', fontsize=rcParams["axes.titlesize"])
    axes = set_ax_props(axes, xlims =((-5.5, 5.5), (-15.5, 15.5)),
                        xticks=(range(-25, 26, 5), range(-20, 21, 5)),
                        xlabels="arcsec", ylabels="Intensity")

    point = PointSource(h)
    sdssdefocus = FluxPerAngle(h, *profiles.SDSS)
    lsstdefocus = FluxPerAngle(h, *profiles.LSST)
    for s in profiles.SEEINGS:
        seeing = GausKolmogorov(s)
        ls = get_ls()
        plot_profile(axes[0], convolve(point, seeing, sdssdefocus),
                     label=f"${s:.2f}''$", color="black", linestyle=ls)
        plot_profile(axes[1], convolve(point, seeing, lsstdefocus),
                     label=f"${s:.2f}''$", color="black", linestyle=ls)

    plt.legend(bbox_to_anchor=(0.1, 1.0, 0.9, 0.), ncol=4, mode="expand",
               bbox_transform=plt.gcf().transFigure, loc="upper left")
    plt.subplots_adjust(bottom=0.1, left=0.12, right=0.98, top=0.92,
                        wspace=0.1)
    return fig, axes


def figure5():
    """Effects of distance on the observed intensity profile of a point source
    for a constant seeing (1.48′′for SDSS and 0.67′′for LSST). Line types
    represent results based on different meteordistances (as shown in the
    legend). The image shows how smaller distances emphasize the central dip
    in the profile, until it reaches its extreme value (such as here for LSST)
    set by the equation (7) dictated by the inner and outer radius of the
    primary mirror (see also Fig. 23, 24 and 26).

    Returns
    -------
    fig : `matplotlib.pyplot.Figure`
        Figure containing the plot.
    ax : `matplotlib.pyplot.Axes`
        Axes containing the plot.
    """
    fig, axes = plt.subplots(1, 2, sharey=True, figsize=(10, 10))
    axes[0].text(-1.2, 1.03, 'SDSS', fontsize=rcParams["axes.titlesize"])
    axes[1].text(-3.0, 1.03, 'LSST', fontsize=rcParams["axes.titlesize"])
    axes = set_ax_props(axes, xlims =((-5.5, 5.5), (-15.5, 15.5)),
                        xticks=(range(-25, 26, 5), range(-20, 21, 5)),
                        xlabels="arcsec", ylabels="Intensity")

    sdssseeing = GausKolmogorov(profiles.SDSSSEEING)
    lsstseeing = GausKolmogorov(profiles.LSSTSEEING)
    for h in profiles.HEIGHTS:
        point = PointSource(h)
        sdssdefocus = FluxPerAngle(h, *profiles.SDSS)
        lsstdefocus = FluxPerAngle(h, *profiles.LSST)
        ls = get_ls()
        plot_profile(axes[0], convolve(point, sdssseeing, sdssdefocus),
                     label=f"${int(h)}km$", color="black", linestyle=ls)
        plot_profile(axes[1], convolve(point, lsstseeing, lsstdefocus),
                     label=f"${int(h)}km$", color="black", linestyle=ls)

    plt.legend(bbox_to_anchor=(0.1, 1.0, 0.9, 0.), ncol=4, mode="expand",
               bbox_transform=plt.gcf().transFigure, loc="upper left")
    plt.subplots_adjust(bottom=0.1, left=0.12, right=0.98, top=0.92,
                        wspace=0.1)

    return fig, axes


def figure6(h=100,  rs=(0.1, 4, 8), instrument=profiles.LSST, seeingfwhm=profiles.LSSTSEEING):
    """Three cases of meteors with \theta_D << \theta_O, \theta_D \approx \theta_O
    and \thetaD >> \theta_O (see equations 6 and 8) illustrated for the LSST
    telescope at 100km distance and the seeing of 0.67′′. Meteors are modeled
    as disks with a uniform surface brightness and the radii of 0.1m, 4m and
    8m, respectively. The solid line shows how the meteor track looks like when
    the telescope is focused on the meteor without any seeing, while the dashed
    line shows what we actually see under defocusing and seeing. For a small
    disk diameter the defocused profile corresponds to that of a point source.
    As the meteor diameter approaches the inner diameter of the LSSTs primary
    mirror, the defocusing profile starts to lose its dip in the middle.

    Parameters
    ----------
    h : `int` or `float`
        Distance to the meteor head in kilometers. By default 100km.
    rs: `list` or `tuple`
        Radii of the meteor heads in meters. By default [0.1, 4, 8]
    instrument : `list` or `tuple`
        Radii of the inner and outter mirror diameters of the instrument in
        meters. By default set to `profiles.LSST`
    seeingfwhm : `int` or `float`
        Seeing FWHM in arcseconds. By default `profiles.LSSTSEEING`.

    Returns
    -------
    fig : `matplotlib.pyplot.Figure`
        Figure containing the plot.
    ax : `matplotlib.pyplot.Axes`
        Axes containing the plot.
    """
    fig, axes = plt.subplots(1, 3, sharey=True, figsize=(10, 10))
    axes[0].text(-10., 1.03, r"$D_{meteor} \ll D_{mirror}$",
                 fontsize=rcParams["axes.titlesize"]-8)
    axes[1].text(-13.0, 1.03, r"$D_{meteor} \approx D_{mirror}$",
                 fontsize=rcParams["axes.titlesize"]-8)
    axes[2].text(-17.0, 1.03, r"$D_{meteor} \gg D_{mirror}$",
                 fontsize=rcParams["axes.titlesize"]-8)
    axes = set_ax_props(axes,
                        xlims=((-12, 12), (-15, 16),( -21, 21)),
                        xticks=(range(-20, 21, 5), range(-21, 21, 7), range(-30, 31, 10)),
                        xlabels="arcsec", ylabels="Intensity")

    seeing  = GausKolmogorov(seeingfwhm)
    defocus = FluxPerAngle(h, *instrument)

    for r, ax in zip(rs, axes):
        d = profiles.DiskSource(h, r)
        c = convolve(d, seeing, defocus)
        plot_profiles(ax, (d, c), color="black", linestyles=('-', '--'),
                      labels=('Object', 'Observed'))

    plt.legend(bbox_to_anchor=(0.1, 1.0, 0.9, 0.), ncol=4, mode="expand",
               bbox_transform=plt.gcf().transFigure, loc="upper left")
    plt.subplots_adjust(bottom=0.1, left=0.12, right=0.98, top=0.92,
                        wspace=0.18)
    return fig, axes


def figures78(rs, instrument, seeingfwhm, xlims, xticks):
    """Genericized version of plots 7 and 8 representing two cases of meteors
    with \theta_D \approx \theta_O and \thetaD >> \theta_O at various distances.
    In effect this is the combination of plots 5 and 6 where we evaluate
    distance to meteor effect on the observed profile and meteor radius effects
    on the observed profile.
    Given the parameters the function creates the whole 2 axes figure with
    titles, x and y labels, ticks, limits and a legend. Figure 7 and 8 exist
    only to specify the parameters that recreate the figures from the paper.

    Parameters
    ----------
    rs : `tuple` or `list`
        Radii of the meteor head in meters.
    instrument : `tuple` or `list`
        Radii of inner and outter mirror diameters of the instrument.
    seeingfwhm : `int` or `float`
        Seeing FWHM in arcseconds.
    xlims : `list` or `tuple` of `lists` or `tuples`
        A list or tuple containing up to two nested lists or tuples. Each
        nested list or tuple contains two values (xmin, xmax) used to set
        individual axis x-axis limits. F.e. [(xmin1, xmax1), (xmin2, xmax2)].
    xticks : `list` or `tuple` 
        A list or tuple containing up to two nested lists or tuples. Each
        nested list or tuple contains positions at which to mark and label the
        ticks at. Tick marks will be displayed for other equally spaced values
        but no labels will be displayed. 

    Returns
    -------
    fig : `matplotlib.pyplot.Figure`
        Figure containing the plot.
    ax : `matplotlib.pyplot.Axes`
        Axes containing the plot.
    """
    fig, axes = plt.subplots(1, 2, sharey=True, figsize=(10, 10))
    axes[0].text(xlims[0][0]/2.0, 1.03, r"$D_{meteor} \approx D_{mirror}$",
                 fontsize=rcParams["axes.titlesize"]-8)
    axes[1].text(xlims[1][0]/2.0, 1.03, r"$D_{meteor} \gg D_{mirror}$",
                 fontsize=rcParams["axes.titlesize"]-8)
    axes = set_ax_props(axes, xlims, xticks, xlabels="arcsec", ylabels="Intensity")

    seeing = GausKolmogorov(seeingfwhm)
    for h in profiles.HEIGHTS:
        defocus = FluxPerAngle(h, *instrument)
        diskeq = DiskSource(h, rs[0])
        diskgg = DiskSource(h, rs[1])

        ls = get_ls()
        plot_profile(axes[0], convolve(diskeq, seeing, defocus),
                     label=f"${int(h)}km$", color="black", linestyle=ls)
        plot_profile(axes[1], convolve(diskgg, seeing, defocus),
                     label=f"${int(h)}km$", color="black", linestyle=ls)

    plt.legend(bbox_to_anchor=(0.1, 1.0, 0.9, 0.), ncol=4, mode="expand",
               bbox_transform=plt.gcf().transFigure, loc="upper left")
    plt.subplots_adjust(bottom=0.1, left=0.12, right=0.98, top=0.92,
                        wspace=0.1)
    return fig, axes


def figure7():
    """Two cases of uniform brightness disk meteors with \theta_D \approx \theta_O
    (R_meteor=1m) and \thetaD >> \theta_O (R_meteor=4m) illustrated for the
    SDSS telescope at various distances (different linetypes) and the seeing of
    1.48′′. This seeing transforms a point source into an object similar to
    \theta_D in size, which results in a defocused image with a negligible
    central drop in the brightness profile. The distinguishing element for a
    disk observed with SDSS is the very wide peak when the disk is similar in
    size to the telescope primary mirror and a growing FWHM as the disk becomes
    much larger than the mirror (compare with fig. 4). Small disk diameter are
    comparable to point source plots in Fig. 5.

    Returns
    -------
    fig : `matplotlib.pyplot.Figure`
        Figure containing the plot.
    ax : `matplotlib.pyplot.Axes`
        Axes containing the plot.

    Notes
    -----
    The function calls on figure78 with the following parameters:
    rs : (1, 4)
    instrument : `profiles.SDSS`
    seeingfwhm : `profiles.SDSSSEEING`
    xlims : [(-6, 6), (-11, 11)]
    xticks : [range(-30, 30, 6), range(-30, 30, 2)]
    """
    return figures78(rs=(1, 4), instrument=profiles.SDSS, seeingfwhm=profiles.SDSSSEEING,
                     xlims=((-6, 6), (-11, 11)), xticks=(range(-30, 30, 2),))


def figure8():
    """Two cases of uniform brightness disk meteors with \theta_D \approx \theta_O
    (R_meteor=4m) and \thetaD >> \theta_O (R_meteor=8m) illustrated for the
    LSST telescope at various distances (different linetypes) and the seeing of
    0.67′′. Since the seeing FWHM is much smaller than the apparent angular
    size \theta_D of the disk in the sky, the brightness profiles are dominated
    by the defocusing effect. Small disk diameter are comparable to point
    source plots in Fig. 5.

    Returns
    -------
    fig : `matplotlib.pyplot.Figure`
        Figure containing the plot.
    ax : `matplotlib.pyplot.Axes`
        Axes containing the plot.

    Notes
    -----
    The function calls on figure78 with the following parameters:
    rs : (4, 8)
    instrument : `profiles.LSST`
    seeingfwhm : `profiles.LSSTSEEING`
    xlims : [(-18, 18), (-25, 25)]
    xticks : [range(-30, 30, 6), range(-30, 30, 10)]
    """
    return figures78(rs=(4, 8), instrument=profiles.LSST,
                     seeingfwhm=profiles.LSSTSEEING,
                     xlims=((-18, 18), (-25, 25)),
                     xticks=(range(-30, 30, 6), range(-30, 30, 10)))


def figures1011(seeingfwhm, instrument, xlims, xticks):
    """Three cases of the fiducial 3D meteor model rotatedby 90, 60 and 0
    degrees observed with SDSS and LSST telescopes at different distances under
    the measured and esimated seeing FWHM conditions respectively.
    A genericized version of plots 10 and 11 that given the parameters creates
    the whole 2 axes figure with titles, x and y labels, ticks limits and a
    legend. Figure 10 and 11 exist only to specify the parameters that recreate
    the figures from the paper.

    Parameters
    ----------
    seeingfwhm : `int` or `float`
        Seeing FWHM in arcseconds.
    instrument : `tuple` or `list`
        Radii of inner and outter mirror diameters of the instrument.
    xlims : `list` or `tuple` of `lists` or `tuples`
        A list or tuple containing up to two nested lists or tuples. Each
        nested list or tuple contains two values (xmin, xmax) used to set
        individual axis x-axis limits. F.e. [(xmin1, xmax1), (xmin2, xmax2)].
    xticks : `list` or `tuple` 
        A list or tuple containing up to two nested lists or tuples. Each
        nested list or tuple contains positions at which to mark and label the
        ticks at. Tick marks will be displayed for other equally spaced values
        but no labels will be displayed. 

    Returns
    -------
    fig : `matplotlib.pyplot.Figure`
        Figure containing the plot.
    ax : `matplotlib.pyplot.Axes`
        Axes containing the plot.
    """
    fig, axes = plt.subplots(1, 3, sharey=True, figsize=(10, 10))
    # xlims[0][0]/2.0
    axes[0].text(xlims[0][0]/2.0, 1.03, r"$\theta_{rot} = 90^\circ$",
                 fontsize=rcParams["axes.titlesize"]-6)
    axes[1].text(xlims[0][0]/2.0, 1.03, r"$\theta_{rot} = 60^\circ$",
                 fontsize=rcParams["axes.titlesize"]-6)
    axes[2].text(xlims[0][0]/2.0, 1.03, r"$\theta_{rot} = 0^\circ$",
                 fontsize=rcParams["axes.titlesize"]-6)
    axes = set_ax_props(axes, xlims, xticks, xlabels="arcsec", ylabels="Intensity")

    seeing = GausKolmogorov(seeingfwhm)
    for h in profiles.HEIGHTS:
        defocus = FluxPerAngle(h, *instrument)
        rab1 = RabinaSource(0.0, h)
        rab2 = RabinaSource(0.5, h)
        rab3 = RabinaSource(1.5, h)

        ls = plotutils.get_ls()
        plot_profile(axes[0], convolve(rab1, seeing, defocus),
                     label=f"${int(h)}km$", color="black", linestyle=ls)
        plot_profile(axes[1], convolve(rab2, seeing, defocus),
                     label=f"${int(h)}km$", color="black", linestyle=ls)
        plot_profile(axes[2], convolve(rab3, seeing, defocus),
                     label=f"${int(h)}km$", color="black", linestyle=ls)

    plt.legend(bbox_to_anchor=(0.1, 1.0, 0.9, 0.), ncol=4, mode="expand",
               bbox_transform=plt.gcf().transFigure, loc="upper left")
    plt.subplots_adjust(bottom=0.1, left=0.12, right=0.98, top=0.92,
                        wspace=0.1)
    return fig, axes


def figure10():
    """Three cases of the fiducial 3D meteor model rotatedby 90, 60 and 0
    degrees, observed with the SDSS telescope from different distances (line
    types as shown in the legend) under the seeing FWHM of 1.48”.

    Returns
    -------
    fig : `matplotlib.pyplot.Figure`
        Figure containing the plot.
    ax : `matplotlib.pyplot.Axes`
        Axes containing the plot.

    Notes
    -----
    The function calls on figures1011 with the following parameters:
    seeingfwhm : `profiles.SDSSSEEING`
    instrument : `profiles.SDSS`
    xlims : [(-7.5, 7.5)]
    xticks : [range (-25, 26, 5)]
    """
    return figures1011(profiles.SDSSSEEING, profiles.SDSS, ((-7.5, 7.5),),
                       (range(-25, 26, 5), ))


def figure11():
    """Three cases of the fiducial 3D meteor model rotatedby 90, 60 and 0
    degrees, observed with the LSST telescope from different distances (line
    types as shown in the legend) under the seeing FWHM of 1.48”.

    Returns
    -------
    fig : `matplotlib.pyplot.Figure`
        Figure containing the plot.
    ax : `matplotlib.pyplot.Axes`
        Axes containing the plot.

    Notes
    -----
    The function calls on figures1011 with the following parameters:
    seeingfwhm : `profiles.LSSTSEEING`
    instrument : `profiles.LSST`
    xlims : [(-7.5, 7.5)]
    xticks : [range (-25, 26, 5)]
    """
    return figures1011(profiles.LSSTSEEING, profiles.LSST, ((-15.5, 15.5), ),
                       (range(-20, 21, 10), ))


def figures1213(tau, h, seeingfwhm, instrument, xlims, xticks, txtpos,
               n=10, duration=2):
    """A fiducial model of ionized meteor trail evolution as seen by SDSS or
    LSST at some distance. The top panel is the trail brightness as seen by an
    telescope without seeing. Different lines show the trail evolution with the
    peak brightness evolving as exp(t/tau), starting from t=0s, while the total
    emitted light remains the same (i.e. the surface under the curves remains
    constant).
    The middle panel shows those profiles convolved with appropriate seeing and
    defocusing.
    The bottom panel is the total time integrated trail brightness profile that
    would actually be observed. This final curve should be added to the meteor
    head brightness profile in order to reconstruct the overall meteor track
    seen in the image.
    All panels have the maximum brightness scaled to one for clarity.

    A genericized version of plots 12 and 13 that given the parameters creates
    the whole 3 axes figure with textboxes, x and y labels, ticks limits and a
    vertical line. Figure 12 and 13 exist only to specify the parameters that
    recreate the figures from the paper.

    Parameters
    ----------
    tau : `int` or `float`
        Characteristic time of meteor trail decay.
    h : `int` or `float`
        Distance from the telescope to the meteor head
    seeingfwhm : `int` or `float`
        Seeing FWHM in arcseconds.
    instrument : `tuple` or `list`
        Radii of inner and outter mirror diameters of the instrument.
    xlims : `list` or `tuple` of `lists` or `tuples`
        A list or tuple containing up to three nested lists or tuples. Each
        nested list or tuple contains two values (xmin, xmax) used to set
        individual axis x-axis limits. F.e. [(xmin1, xmax1), (xmin2, xmax2)].
    xticks : `list` or `tuple` 
        A list or tuple containing up to three nested lists or tuples. Each
        nested list or tuple contains positions at which to mark and label the
        ticks at. Tick marks will be displayed for other equally spaced values
        but no labels will be displayed.
    txtpos : `list` or `tuple`
        A list or tuple containing three nested lists or tuples. Each nested
        list or tuple contains positions at which a textbox, that acts as the
        plot title, will be drawn.
    n : `int`
        The number of trail profile samples that will be evaluated and
        integrated into final profile. Duration and the number of samples
        effectively set the time step dt between two evaluated trails. By
        default set to 10 to give time step between to trail profiles of approx
        0.2 seconds.
    duration : `int` or `float`
        The total duration, in seconds, in which the meteor trail is considered
        to be visible. By default set to 2 seconds giving a time-step between
        two profiles of 0.2 seconds.

    Returns
    -------
    fig : `matplotlib.pyplot.Figure`
        Figure containing the plot.
    ax : `matplotlib.pyplot.Axes`
        Axes containing the plot.
    """
    fig, axes = plt.subplots(3, 1, sharex=True, figsize=(12, 14))
    axes = set_ax_props(axes, xlims, xticks, xlabels="arcsec", ylabels="Intensity")
    axes[0].text(*txtpos[0], 'Gaussian trail evolution', fontsize=rcParams["axes.titlesize"])
    axes[1].text(*txtpos[1], 'Gaussian trail evolution \n defocused', fontsize=rcParams["axes.titlesize"])
    axes[2].text(*txtpos[2], 'All time-steps integrated', fontsize=rcParams["axes.titlesize"])
    axes[0].get_xaxis().set_visible(False)
    axes[1].get_xaxis().set_visible(False)

    gaussians = [GaussianSource(h, i) for i in profiles.exp_fwhms(tau, n, duration)]
    s = GausKolmogorov(seeingfwhm)
    d = FluxPerAngle(h, *instrument)

    conv = []
    for g in gaussians:
        c = convolve(g, s, d)
        # normalization in these plots is to area of unity via Riemmans sum
        g.obj = g.obj/(g.obj.sum()*g.step)
        conv.append(c)

    # each profile carries their own scale, to add them we need to rescale to
    # common scale and renormalize (rescaling will re-evaluate the profiles)
    tmpobj = np.zeros(conv[-1].obj.shape)
    tmpscale = conv[-1].scale
    for c in conv:
        c.rescale(tmpscale)
        c.obj = c.obj/(c.obj.sum()*c.step)
        tmpobj += c.obj

    # profiles are normalized to unity area such that the relative height
    # differences between the curves are physical. Maxima is then some number.
    # For the plots to look nice we want to normalize height to 1 but keep
    # relative heights differences unchanged.So we re-normalize so that largest
    # maxima, of all profiles, is unity and rescale the rest by the same factor
    gscale = gaussians[0].obj.max()
    convscale = conv[0].obj.max()
    addscale = tmpobj.max()

    plot_profiles(axes[0], gaussians, color="black", normed=gscale, linewidth=2)
    plot_profiles(axes[1], conv, color="black", normed=convscale, linewidth=2)
    axes[2].plot(tmpscale, tmpobj/addscale, color="black", linewidth=2)

    plt.subplots_adjust(bottom=0.07, left=0.1, right=0.97, top=0.98, hspace=0.08)
    return fig, axes


def figure12():
    """A fiducial model of ionized meteor trail evolution as seen by SDSS at
    100km distance. The top panel is the trail brightness as seen by the
    telescope without seeing. Different lines show the trail evolution with the
    peak brightness evolving as exp(t/tau), with tau=1s, starting from t=0s,
    while the total emitted light remains the same (i.e. the surface under the
    curves remains constant).
    The middle panel shows those profiles convolved with seeing of 1.48'' and
    defocusing.
    The bottom panel is the total time integrated trail brightness profile that
    would actually be observed. This final curve should be added to the meteor
    head brightness profile in order to reconstruct the overall meteor track
    seen in the image.
    All panels have the maximum brightness scaled to one for clarity.

    Notes
    -----
    The function calls figures1213 with the following values: 
    tau : 1s
    h : 100km
    seeingfwhm : `profiles.SDSSSEEING`
    instrument : `profiles.SDSS`
    xlims : [(-8.5, 8.5)]
    xticks : [range(-20, 20, 2)]
    txtpos : [(2, 0.8), (2, 0.8), (2, 0.8)]
    n : 10
    duration : 2s

    Returns
    -------
    fig : `matplotlib.pyplot.Figure`
        Figure containing the plot.
    ax : `matplotlib.pyplot.Axes`
        Axes containing the plot.
    """ 
    return figures1213(1, 100, profiles.SDSSSEEING, profiles.SDSS,
                      xlims=((-8.5,8.5),), xticks=(range(-20, 20, 2),),
                      txtpos=((2,0.8), (2,0.8), (2,0.8)))


def figure13():
    """A fiducial model of ionized meteor trail evolution as seen by LSST at
    100km distance. The top panel is the trail brightness as seen by the
    telescope without seeing. Different lines show the trail evolution with the
    peak brightness evolving as exp(t/tau), with tau=1s, starting from t=0s,
    while the total emitted light remains the same (i.e. the surface under the
    curves remains constant).
    The middle panel shows those profiles convolved with seeing of 0.67'' and
    defocusing.
    The bottom panel is the total time integrated trail brightness profile that
    would actually be observed. This final curve should be added to the meteor
    head brightness profile in order to reconstruct the overall meteor track
    seen in the image.
    All panels have the maximum brightness scaled to one for clarity.
    Compared to SDSS (figure 12), the defocus effect is much stronger due to a
    larger telescope aperture and now even meteor trails can have a central dip
    in the brightness profile.

    Notes
    -----
    The function calls figures1213 with the following values: 
    tau : 1s
    h : 100km
    seeingfwhm : `profiles.LSSTSEEING`
    instrument : `profiles.LSST`
    xlims : [(-15, 15)]
    xticks : [range(-20, 20, 2)]
    txtpos : [(2, 0.8), (-5, 0.28), (2, 0.8)]
    n : 10
    duration : 2s

    Returns
    -------
    fig : `matplotlib.pyplot.Figure`
        Figure containing the plot.
    ax : `matplotlib.pyplot.Axes`
        Axes containing the plot.
    """ 

    return figures1213(1, 100, profiles.LSSTSEEING, profiles.LSST,
                      xlims=((-15,15),), xticks=(range(-20, 20, 2),),
                      txtpos=((2,0.8), (-5,0.28), (2,0.8)))


def figures1415(tau, h, seeingfwhm, instrument, xlims, xticks, txtpos,
               n=10, duration=2, nsteps=486):
    """A fiducial model of ionized meteor trail evolution as seen by an
    telescope some distance with trail drift, due to atmospheric winds,
    included. The top panel is the trail brightness as seen without seeing.
    Different lines show the trail temporal and spatial evolution with the peak
    brightness evolving as exp(t/tau), with tau=1s, starting from t=0s, while
    the total emitted light remains the same (i.e. the surface under the curves
    remains constant). The trail drift motion is modeled from left to right
    with each step shifting the profile by some number of steps. The vertical
    dashed line shows the initial position of the meteor trail.
    The middle panel shows those profiles convolved with appropriate seeing and
    defocusing.
    The bottom panel is the total integrated trail brightness profile that
    would actually be observed. This final curve should be added to the meteor
    head brightness profile in order to reconstruct the overall meteor track
    seen in the image.

    A genericized version of plots 14 and 15 that given the parameters creates
    the whole 3 axes figure with textboxes, x and y labels, ticks limits and a
    vertical line. Figure 14 and 15 exist only to specify the parameters that
    recreate the figures from the paper.

    Parameters
    ----------
    tau : `int` or `float`
        Characteristic time of meteor trail decay.
    h : `int` or `float`
        Distance from the telescope to the meteor head
    seeingfwhm : `int` or `float`
        Seeing FWHM in arcseconds.
    instrument : `tuple` or `list`
        Radii of inner and outter mirror diameters of the instrument.
    xlims : `list` or `tuple` of `lists` or `tuples`
        A list or tuple containing up to three nested lists or tuples. Each
        nested list or tuple contains two values (xmin, xmax) used to set
        individual axis x-axis limits. F.e. [(xmin1, xmax1), (xmin2, xmax2)].
    xticks : `list` or `tuple` 
        A list or tuple containing up to three nested lists or tuples. Each
        nested list or tuple contains positions at which to mark and label the
        ticks at. Tick marks will be displayed for other equally spaced values
        but no labels will be displayed.
    txtpos : `list` or `tuple`
        A list or tuple containing three nested lists or tuples. Each nested
        list or tuple contains positions at which a textbox, that acts as the
        plot title, will be drawn.
    n : `int`
        The number of trail profile samples that will be evaluated and
        integrated into final profile. Duration and the number of samples
        effectively set the time step dt between two evaluated trails. By
        default set to 10 to give time step between to trail profiles of approx
        0.2 seconds.
    duration : `int` or `float`
        The total duration, in seconds, in which the meteor trail is considered
        to be visible. By default set to 2 seconds giving a time-step between
        two profiles of 0.2 seconds.
    nsteps : `int`
        The total number of rightwards steps each time step will make. The
        drift velocity depends on duration and number of samples. Defaults to
        486 steps such that, with the default values, the drift velocity equals
        2.2''/second.

    Returns
    -------
    fig : `matplotlib.pyplot.Figure`
        Figure containing the plot.
    ax : `matplotlib.pyplot.Axes`
        Axes containing the plot.
    """
    fig, axes = plt.subplots(3, 1, sharex=True, figsize=(12, 14))
    axes = set_ax_props(axes, xlims, xticks, xlabels="arcsec", ylabels="Intensity")
    axes[0].text(*txtpos[0], 'Gaussian trail drift', fontsize=rcParams["axes.titlesize"]-6)
    axes[1].text(*txtpos[1], 'Gaussian trail drift\ndefocused', fontsize=rcParams["axes.titlesize"]-6)
    axes[2].text(*txtpos[2], 'All time-steps integrated', fontsize=rcParams["axes.titlesize"]-6)
    axes[0].get_xaxis().set_visible(False)
    axes[1].get_xaxis().set_visible(False)

    s = GausKolmogorov(seeingfwhm)
    d = FluxPerAngle(h, *instrument)
    gaussians = [GaussianSource(h, i) for i in profiles.exp_fwhms(tau, n, duration)]
    conv = [convolve(g,s,d) for g in gaussians]

    # same procedure as for figures 12 and 13
    newscale = gaussians[-1].scale
    for g, c in zip(gaussians, conv):
        g.rescale(newscale)
        c.rescale(newscale)
        g.obj = g.obj/(g.obj.sum()*g.step)
        c.obj = c.obj/(c.obj.sum()*c.step)

    # to simulate a timestep we need to right-shift the profile on its
    # respective scale by N number of steps. Each step carries some delta x in
    # arcseconds. Each profile is generated from exponential decaying fwhms,
    # each of which is generated for some delta t after the first profile (at
    # t=0) as determined by tau. This gives the drift velocity. At this point
    # one step is about 0.001''. The default tau of 1, and duration of 2s, make
    # each profile 0.22 seconds appart. Stepping for 486 to the right is then
    # equivalent of 0.485''/0.22s or approximately 2.2''/s
    # the +10000 elements is just padding to allow the shifted profiles to fit
    # fully into the new array.
    timestep = 0
    tmpobj = np.zeros((c.obj.shape[0]+10000,))
    for g, c in zip(gaussians, conv):
        newg = np.zeros((g.obj.shape[0]+10000, ))
        newc = np.zeros((c.obj.shape[0]+10000, ))

        shift = timestep*nsteps
        half  = len(g.obj)/2
        start = int(shift - half)
        end   = int(shift + half)

        newg[shift:shift+len(g.obj)] += g.obj
        newc[shift:shift+len(c.obj)] += c.obj

        g.obj   = newg
        g.scale = np.arange(g.scaleleft, g.scaleright+10001*g.step, g.step)
        c.obj   = newc
        c.scale = np.arange(c.scaleleft, c.scaleright+10001*c.step, c.step)
        tmpobj += newc
        timestep += 1

    # same procedures as for figures 12 and 13
    gscale = gaussians[0].obj.max()
    convscale = conv[0].obj.max()
    addscale = tmpobj.max()

    plot_profiles(axes[0], gaussians, color="black", normed=gscale, linewidth=2)
    plot_profiles(axes[1], conv, color="black", normed=convscale, linewidth=2)
    # tmpobj is created by stacking aligned convolution profiles so any scale
    # from any convolution profile should do
    axes[2].plot(c.scale, tmpobj/addscale, color="black", linewidth=2)

    # add vertical line at the position of the maxima of the initial profile
    for ax in axes:
        ax.plot([0, 0], [-10, 10], color="gray", linewidth=1, linestyle="--")

    plt.subplots_adjust(bottom=0.07, left=0.1, right=0.97, top=0.98, hspace=0.08)
    return fig, axes


def figure14():
    """A fiducial model of ionized meteor trail evolution as seen by SDSS at
    100km distance with trail drift, due to atmospheric winds, included. The
    top panel is the trail brightness as seen without seeing. Different lines
    show the trail temporal and spatial evolution with the peak brightness
    evolving as exp(t/tau), with tau=1s, starting from t=0s, while the total
    emitted light remains the same (i.e. the surface under the curves remains
    constant). The trail drift motion is modeled from left to right with each
    step shifting the profile by 486 steps. The vertical dashed line shows the
    initial position of the meteor trail.
    The middle panel shows those profiles convolved with seeing of 1.37'' and
    defocusing.
    The bottom panel is the total integrated trail brightness profile that
    would actually be observed. This final curve should be added to the meteor
    head brightness profile in order to reconstruct the overall meteor track
    seen in the image.

    Notes
    -----
    The function calls figures1415 with the following values: 
    tau : 1s
    h : 100km
    seeingfwhm : `profiles.SDSSSEEING`
    instrument : `profiles.SDSS`
    xlims : [(-4.5, 12.5)]
    xticks : [range(-20, 20, 2)]
    txtpos : [(6, 0.6), (6, 0.06), (6, 0.6)]
    n : 10
    duration : 2s
    nsteps : 486

    Returns
    -------
    fig : `matplotlib.pyplot.Figure`
        Figure containing the plot.
    ax : `matplotlib.pyplot.Axes`
        Axes containing the plot.
    """
    return figures1415(1, 100, profiles.SDSSSEEING, profiles.SDSS,
                      xlims=((-4.5, 12.5),), xticks=(range(-20, 20, 2),),
                      txtpos=((6,0.6), (6,0.6), (6,0.6)))


def figure15():
    """A fiducial model of ionized meteor trail evolution as seen by LSST at
    100km distance with trail drift, due to atmospheric winds, included. The
    top panel is the trail brightness as seen without seeing. Different lines
    show the trail temporal and spatial evolution with the peak brightness
    evolving as exp(t/tau), with tau=1s, starting from t=0s, while the total
    emitted light remains the same (i.e. the surface under the curves remains
    constant). The trail drift motion is modeled from left to right with each
    step shifting the profile by 486 steps. The vertical dashed line shows the
    initial position of the meteor trail.
    The middle panel shows those profiles convolved with seeing of 0.67'' and
    defocusing.
    The bottom panel is the total integrated trail brightness profile that
    would actually be observed. This final curve should be added to the meteor
    head brightness profile in order to reconstruct the overall meteor track
    seen in the image.

    Notes
    -----
    The function calls figures1415 with the following values: 
    tau : 1s
    h : 100km
    seeingfwhm : `profiles.LSSTSEEING`
    instrument : `profiles.LSST`
    xlims : [(-10.5, 17.5)]
    xticks : [range(-20, 20, 5)]
    txtpos : [(9, 0.6), (9, 0.06), (9, 0.6)]
    n : 10
    duration : 2s
    nsteps : 486

    Returns
    -------
    fig : `matplotlib.pyplot.Figure`
        Figure containing the plot.
    ax : `matplotlib.pyplot.Axes`
        Axes containing the plot.
    """
    return figures1415(1, 100, profiles.LSSTSEEING, profiles.LSST,
                      xlims=((-10.5,17.5),), xticks=(range(-20, 20, 5),),
                      txtpos=((9,0.6), (9,0.6), (9,0.6)))


def figure1617(tau, h, seeingfwhm, instrument, xlims, xticks,
               n=10, duration=2, nsteps=486, loc="upper right"):
    """An example of the observed meteor track at some distance (solid line) as
    it would appear in an image from an telescope obtained as a sum of two
    contributions: from a defocused meteor (dashed line) contributing 80% of
    the peak brightness and from a defocused meteor trail (dotted line)
    contributing 20% of the peak brightness. This example illustrate how the
    meteor trail deforms the pure meteor head brightness profile by deforming
    dominantly one side of the defocused two-peak meteor head profile.

    A genericized version of plots 16 and 17 that given the parameters creates
    the whole figure with textboxes, x and y labels, ticks limits and a
    vertical line. Figure 16 and 17 exist only to specify the parameters that
    recreate the figures from the paper.

    Parameters
    ----------
    tau : `int` or `float`
        Characteristic time of meteor trail decay.
    h : `int` or `float`
        Distance from the telescope to the meteor head
    seeingfwhm : `int` or `float`
        Seeing FWHM in arcseconds.
    instrument : `tuple` or `list`
        Radii of inner and outter mirror diameters of the instrument.
    xlims : `list` or `tuple` of `lists` or `tuples`
        A list or tuple containing a nested list or tuple. The nested list or
        tuple contains two values (xmin, xmax) used to set individual axis
        x-axis limits. F.e. [(xmin1, xmax1), (xmin2, xmax2)].
    xticks : `list` or `tuple`
        A list or tuple containing a nested list or tuple. The nested list or
        tuple contains positions at which to mark and label the ticks at. Tick
        marks will be displayed for other equally spaced values but no labels
        will be displayed.
    n : `int`
        The number of trail profile samples that will be evaluated and
        integrated into final profile. Duration and the number of samples
        effectively set the time step dt between two evaluated trails. By
        default set to 10 to give time step between to trail profiles of approx
        0.2 seconds.
    duration : `int` or `float`
        The total duration, in seconds, in which the meteor trail is considered
        to be visible. By default set to 2 seconds giving a time-step between
        two profiles of 0.2 seconds.
    nsteps : `int`
        The total number of rightwards steps each time step will make. The
        drift velocity depends on duration and number of samples. Defaults to
        486 steps such that, with the default values, the drift velocity equals
        2.2''/second.
    loc : `str`
        One of the matplotlib recognized legend location strings. By default
        'upper right'. This reduces the total time it takes to plot the figure
        by avoiding optimal legend position calculation being done by pyplot.

    Returns
    -------
    fig : `matplotlib.pyplot.Figure`
        Figure containing the plot.
    ax : `matplotlib.pyplot.Axes`
        Axes containing the plot.
    """
    fig, ax = plt.subplots(figsize=(12, 10))
    ax = set_ax_props(ax, xlims, xticks, xlabels="arcsec", ylabels="Intensity")[0]

    # same procedure as for figures 12 and 13, first we create the trail sources
    # by defocusing gaussians and getting them to the same scale; except this
    # time its safe to skip rescaling and renormalizing gaussians because we're
    # not plotting them
    s = GausKolmogorov(seeingfwhm)
    d = FluxPerAngle(h, *instrument)
    gaussians = [GaussianSource(h, i) for i in profiles.exp_fwhms(tau, n, duration)]
    obsgaus = [convolve(g,s,d) for g in gaussians]

    timestep = 0
    trail = np.zeros((obsgaus[-1].obj.shape[0]+10000,))
    trailscale = obsgaus[-1].scale
    for c in obsgaus:
        c.rescale(trailscale)
        c.obj = c.obj/(c.obj.sum()*c.step)

        # same as for fig 13 and 14 we then move them nsteps sideways to simulate
        # trail drift, except it's all rolled under 1 for loop
        newc = np.zeros((c.obj.shape[0]+10000, ))

        shift = timestep*nsteps
        half  = len(c.obj)/2
        start = int(shift - half)
        end   = int(shift + half)

        newc[shift:shift+len(c.obj)] += c.obj

        c.obj   = newc
        c.scale = np.arange(c.scaleleft, c.scaleright+10001*c.step, c.step)
        trail += newc
        timestep += 1

    # meteor flies through and leaves its imprint, behind him there is a trail
    # (a "wake") that exists for some time more and adds to the signal. We assume
    # the ratios of the signals are 80% meteor and 20% trail. We add them together
    # by rescaling to same scale and adding.
    p = PointSource(h)
    dp = convolve(p, s, d)
    dp.rescale(c.scale)
    dp.obj = dp.obj/((dp.obj.sum()*dp.step))

    # now we renormalize everything before adding so we can scale appropriately
    # and also for the plots
    trail = trail/trail.max()
    dp.obj = dp.obj/dp.obj.max()

    # add the meteor head and trail drift to gt final observed profile
    observed = 0.8*dp.obj + 0.2*trail

    ax.plot(dp.scale, 0.8*dp.obj, color="black", linestyle="dotted", label="Meteor trail",
            linewidth=2)
    ax.plot(c.scale, 0.2*trail, color="black", linestyle="dashed", label="Meteor head",
            linewidth=2)
    ax.plot(c.scale, observed, color="black", linestyle="solid", label="Head $+$ trail")

    plt.legend(loc=loc)
    plt.subplots_adjust(bottom=0.1, left=0.1, right=0.95, top=0.97, hspace=0.08)

    return fig, ax


def figure16():
    """An example of the observed meteor track (solid line) at 100 km distance
    as it would appear in an image from the SDSS telescope obtained as a sum of
    two contributions: from a defocused meteor (dashed line) contributing 80%
    of the peak brightness and from a defocused meteor trail (dotted line)
    contributing 20%of the peak brightness. This example illustrate how the
    meteor trail deforms the pure meteor head brightness profile by deforming
    dominantly one side of the defocused two-peak meteor head profile.

    Notes
    -----
    The function calls figures1617 with the following values:
    tau : 1s
    h : 100km
    seeingfwhm : `profiles.SDSSSEEING`
    instrument : `profiles.SDSS`
    xlims : [(-5.5, 10.5)]
    xticks : [range(-20, 20, 2)]
    n : 10
    duration : 2s
    nsteps : 486
    loc : 'upper right'

    Returns
    -------
    fig : `matplotlib.pyplot.Figure`
        Figure containing the plot.
    ax : `matplotlib.pyplot.Axes`
        Axes containing the plot.
    """
    return  figure1617(1, 100, profiles.SDSSSEEING, profiles.SDSS,
                       xlims=((-5.5, 10.5),), xticks=(range(-20, 20, 2),))


def figure17():
    """An example of the observed meteor track (solid line) at 100 km distance
    as it would appear in an image from the LSST telescope obtained as a sum of
    two contributions: from a defocused meteor (dashed line) contributing 80%
    of the peak brightness and from a defocused meteor trail (dotted line)
    contributing 20%of the peak brightness. In this case the trail’s main
    disruption to the meteor head brightness is in reducing the depth of the
    central brightness dip, while the profile asymmetryis not very prominent.

    Notes
    -----
    The function calls figures1617 with the following values:
    tau : 1s
    h : 100km
    seeingfwhm : `profiles.LSSTSEEING`
    instrument : `profiles.LSST`
    xlims : [(-11.5, 14.5)]
    xticks : [range(-20, 20, 5)]
    n : 10
    duration : 2s
    nsteps : 486
    loc : 'upper right'

    Returns
    -------
    fig : `matplotlib.pyplot.Figure`
        Figure containing the plot.
    ax : `matplotlib.pyplot.Axes`
        Axes containing the plot.
    """
    return figure1617(1, 100, profiles.LSSTSEEING, profiles.LSST, loc="upper center",
                      xlims=((-11.5,14.5),), xticks=(range(-20, 20, 5),))


def param_space_sampler(heights, seeings, source, instrument, **kwargs):
    """Given of heights and seeings simplistically samples the key meteor
    profile parameters as an numpy structured array with the following columns:
        * height - distance, really, to the meteor head
        * seeing - seeing fwhm
        * sfwhm  - the calculated seeing fwhm post convolution (good for
                   verification)
        * dfwhm  - FWHM of the defocused source profile only (no seeing)
        * ofwhm  - the observed fwhm
        * depth  - the percentage value of the difference between a profiles
                   maximum and the minimum value of the central dip

    The function samples only across different defocusing and seeing effects
    and can not sample across source parameters, i.e. it can not sample across
    different radii of DiskSource, or different initial FWHMs of GaussianSource
    even though it is possible to instantiate sources using different
    parameters.

    Parameters
    ----------
    heights : `list`, `tuple` or `generator`
        Iterable of integers or floats representing height in kilometers.
    seeings : `list`, `tuple` or `generator`
        Iterable of integers or floats representing seeing FWHM in arcseconds.
    source : `cls`
        Class to use for meteor profile.
    instrument : `list` or `tuple`
        An length two iterable containing ints or floats representing the inner
        inner and outter mirror radii of the instrument.
    **kwargs : `dict`
        Any additional kwargs are passed to the source class instantiation.
    """
    dt = np.dtype([("height", float), ("seeing", float),
                   ("sfwhm", float), ("dfwhm", float),
                   ("ofwhm", float), ("depth", float)])
    data = np.zeros((len(heights), len(seeings)), dtype=dt)

    for h, i in zip(heights, range(len(heights))):
        for s, j in zip(seeings, range(len(seeings))):
            P = source(h, **kwargs)
            S = GausKolmogorov(s)
            D = FluxPerAngle(h, *instrument)
            C = convolve(P, S, D)

            top = C.peak
            mid = C.obj[int(len(C.obj)/2)]
            diff = (top-mid)

            data["seeing"][i,j] = s
            data['sfwhm'][i,j] = S.calc_fwhm()
            data['ofwhm'][i,j] = C.calc_fwhm()
            data['depth'][i,j] = (diff/top)*100.0
        # defocusing FWHM will be the same for each seeing FWHM
        C = convolve(P, D)
        data['dfwhm'][i,:] = C.calc_fwhm()
        data['height'][i,:] = h

    return data

def param_space_sampler2(heights, radii, source, seeing, instrument, **kwargs):
    dt = np.dtype([("height", float), ("seeing", float),
                   ("sfwhm", float), ("dfwhm", float),
                   ("ofwhm", float), ("depth", float)])
    data = np.zeros((len(heights), len(radii)), dtype=dt)

    for h, i in zip(heights, range(len(heights))):
        for r, j in zip(radii, range(len(radii))):
            P = source(h, r, **kwargs)
            S = GausKolmogorov(seeing)
            D = FluxPerAngle(h, *instrument)
            C = convolve(P, S, D)

            top = C.peak
            mid = C.obj[int(len(C.obj)/2)]
            diff = (top-mid)

            # this is here to cover for data dependance of plotting function,
            # it should actually say radius
            data["seeing"][i,j] = r
            data['sfwhm'][i,j] = S.calc_fwhm()
            data['ofwhm'][i,j] = C.calc_fwhm()
            data['depth'][i,j] = (diff/top)*100
        # defocusing FWHM will be the same for each seeing FWHM
        C = convolve(P, D)
        data['dfwhm'][i,:] = C.calc_fwhm()
        data['height'][i,:] = h

    return data


def plot_param_space(fig, ax, data, xdat, ydat, secydat=None, pcollims=None,
                     contours=None, **kwargs):
    """Given some data, equivalent to data produced by parameter space
    samplers, plots a psuedocolored plot onto the given ax. Optionally will
    overlay contours at desired values and create a false second y axis which
    labels will match the left hand side's labels but with values taken from
    the specified column in the data.

    Parameters
    ----------
    fig : `matplotlib.pyplot.Figure`
        Figure containing the plot.
    ax : `matplotlib.pyplot.Axes`
        Axes containing the plot.
    data : `numpy.array`
        A 2D array containing the the data for central color plot.
    xdat : `list`, `tuple` or `np.array`
        Data used as the primary x axis.
    ydat : `list`, `tuple` or `np.array`
        Data used as the primary y axis.
    secydat : `list`, `tuple`, `np.array` or `None`
        Data that, if provided, will be used to create a secondary y axis.
    pcollims : `tuple`
        A tuple containing (lower, higher) values of color limits to use when
        normalizing the plot. Useful if figure contains multiple different axes
        all of which need to share the same color normalization limits. If not
        given (0, max(data)) are used as limits.
    contours : `dict`, `tuple`, `list` or `None``
        List, tuple or dictionary of values at which contours will be drawn. If
        None, no contours are drawn. See notes.

    Returns
    -------
    fig : `matplotlib.pyplot.Figure`
        Figure containing the plot.
    ax : `matplotlib.pyplot.Axes`
        Axes containing the plot.


    Notes
    -----
    Matplotlib does not produce nice spacings between inlined contour label and
    the contour it belongs to, especially for contours nested against large
    gradients. Problem is avoided if contours are not plotted all together but
    in batches, each one supplied with it's own, different, spacing. This means
    that even for just one axis of a simple 2 group contour plot of a figure
    one needs to specify something verbose like:

    contours = {
        "batch1" : {"levels" : [1, 2, 3], "spacing" : 7 },
        "batch2" : {"levels" : [4, 5, 6], "spacing" : 8 }
    }

    To reduce verbosity required to call the function the contours are instead
    interpreted as batches per axis, such that each contour in the list is a
    dictionary of batches or an iterable in which spacing is determined
    automatically or to "spacing" kwarg, if supplied. F.e. the
    above example is then shortened to:

    contours = {"levels" : [[1, 2, 3], [4, 5, 6]], "spacings" : [7, 8]}
    """
    if pcollims is None:
        pcollims = (0, data.max())
    pcol = ax.pcolormesh(xdat, ydat, data, vmin=pcollims[0], vmax=pcollims[1])

    # check if contours are special case of batches or simple flat lists
    drawcontours = True
    batched, automaticspcs = False, False
    cnts, spcs = None, None
    if contours is None:
        drawcontours = False
    elif isinstance(contours, dict):
        cnts = contours.get("levels", None)
        spcs = contours.get("spacings", None)
        batched = True
    elif isinstance(contours, list) or isinstance(contours, tuple):
        cnts = contours
        spcs = kwargs.get("spacing", None)
    else:
        raise TypeError("Contour levels must be list or tuples.")
    if spcs is None:
        automaticspcs=True

    color = kwargs.pop("colors", None)
    fntsize = rcParams["legend.fontsize"]

    def draw_contours(contours, spacing, **kwargs):
        """Helper function to avoid code duplication when plotting contours."""
        if not drawcontours:
            return None
        c = ax.contour(xdat, ydat, data, levels=contours, colors=color)
        if automaticspcs:
            ax.clabel(c, fontsize=fntsize, inline=True, colors=color, fmt="%1.0f",
                      rightside_up=True, use_clabeltext=True)
        else:
            ax.clabel(c, fontsize=fntsize, inline=True, inline_spacing=spacing,
                      colors=color, fmt="%1.0f", rightside_up=True,
                      use_clabeltext=True)

    if batched:
        for c, s in zip(cnts, spcs):
            draw_contours(c, s)
    else:
        draw_contours(cnts, spcs)

    if secydat is not None:
        ax2 = ax.twinx()
        ax2.plot(secydat, ydat, linestyle="--", color="white")
        ax2.set_ylim(min(ydat), max(ydat))
        # getting ax2.get_xticks and xticklabels gets me nothing sensible! So the
        # matching between defocused FWHM and height has to be done manually. We
        # skip the first tick (40km) via [1:: , grab every 5th defocus fwhm as
        # [1::5 . Data has defocus fwhm per seeing but fwhm changes only with
        # height - we need 1st element of each only. Ergo [1::5,0])
        labels = [f"${d:.2f}$" for d in secydat[1::5]]
        # and then because of nonsensical tick values, the first one is -2.0,
        # I don't know why, but we have to skip it because it's not actually marked
        tlabels = [""]
        tlabels.extend(labels)
        ax2.yaxis.set_ticklabels(tlabels)
        return pcol, ax2
    return pcol, None


def get_or_create_data(datafiles, heights=None, seeings=None, radii=None):
    # this needs fixing and not just ugly hacks
    if seeings is not None and radii is not None:
        raise ValueError("Sampler undefined when both seeing and radii are given.")
    elif seeings is None and radii is None:
        raise ValueError("Sampler undefined when neither seeing and radii are given.")
    elif seeings is not None:
        sampler = param_space_sampler
        parameter = seeings
    elif radii is not None:
        sampler = param_space_sampler2
        parameter = radii

    data = []
    for datfile in datafiles:
        try:
            path = plotutils.get_data_file(datfile[0])
            data.append(np.load(path, allow_pickle=False))
        except OSError:
            warnings.warn(f"Parameter space data file {plotutils.create_data_file_name(datfile[0])} "
                          "does not exist or has been corrupted. Recreating it can take some time.")
            data.append(sampler(heights, parameter, **datfile[1]))
            np.save(plotutils.create_data_file_name(datfile[0]), data[-1])

    return data


def figure232426(fig, axes, data, xdat, ydat, secydat=None, contours=None,
                 sharedcb=True, cbtitle=None, xlims=None, ylims=None,
                 xlabels="", ylabels="", **kwargs):
    # clean up the arguments. Technically each plot can have completely
    # arbitrary x, y axis and plot data. Realistically, they will share them so
    # for brevity we allow simple lists as x and y data but then sanitize them
    if len(xdat) != len(data):
        xdat = (xdat,)*len(data)
    if len(ydat) != len(data):
        ydat = (ydat,)*len(data)
    cbtitle = plotcol if cbtitle is None else cbtitle

    # shared colorbars need to share color ranges and the same normalization so
    # create a fake data based on data extrema and use its range and
    # normalization to re-color the data graphs.
    cbaxes = []
    if sharedcb:
        pmax = max([np.max(d) for d in data])
        pmin = min([np.min(d) for d in data])
        pcollims = (pmax, pmin) 
        pcol = np.linspace(*pcollims, len(xdat[0])*len(ydat[0]))
        pcol = pcol.reshape(len(ydat[0]), len(xdat[0]))
        pcol = axes[0].pcolormesh(xdat[0], ydat[0], pcol)

        # position the colorbar axes on top when shared
        cax = fig.add_axes([0.12, 0.93, 0.76, 0.01])
        cax.text(0.5, 3.5, cbtitle,
                 horizontalalignment = 'center',
                 verticalalignment = 'center',
                 fontsize = rcParams["axes.titlesize"],
                 transform = cax.transAxes)
        colbar = fig.colorbar(pcol, orientation="horizontal", cax=cax)
        colbar.ax.xaxis.set_ticks_position('top')
        colbar.ax.xaxis.set_label_position('top')
        adjustvals = {"bottom":0.05, "left":0.12, "right":0.88, "top":0.92,
                      "hspace":0.03}

    # now plot the parameter space data
    twinx = []
    contours = [None,]*len(axes) if contours is None else contours
    secydat = [None,]*len(axes) if secydat is None else secydat
    for ax, d, xax, yax, syd, cnt in zip(axes, data, xdat, ydat, secydat, contours):
        pcol1, ax2 = plot_param_space(fig, ax, d, xax, yax, sectdat=syd, contours=cnt,
                                      colors="white", **kwargs)
        twinx.append(ax2)
        # if the colorbar was not shared, plot each axis' colorbar individually
        if not sharedcb:
            divider = make_axes_locatable(ax)
            cax = divider.append_axes('top', size='5%', pad=0.1)
            cbaxes.append(cax)
            colbar = fig.colorbar(pcol1, orientation="horizontal", cax=cax)
            colbar.set_label(cbtitle, fontsize=rcParams["axes.titlesize"])
            colbar.ax.xaxis.set_ticks_position('top')
            colbar.ax.xaxis.set_label_position('top')
            adjustvals = {"bottom":0.05, "left":0.1, "right":0.88, "top":0.96,
                          "hspace":0.25}

    if xlims is None:
        xmax = [np.max(x) for x in xdat]
        xmin = [np.min(x) for x in xdat]
        xlims = zip(xmin, xmax)
    if ylims is None:
        ymax = [np.max(y) for y in ydat]
        ymin = [np.min(y) for y in ydat]
        ylims = zip(ymin, ymax)

    # triple plots are special in that they only label middle plot
    axes = set_ax_props(axes, xlims=xlims, ylims=ylims, xlabels=xlabels,
                        ylabels=ylabels)
    plt.subplots_adjust(**adjustvals)

    return fig, axes, twinx, cbaxes


# The paper plot must be wrong because the bottom defocusing values actually correspond
# to the following:
#     S = [DiskSource(h, 8) for h in range(40, 440, 10)]
#     D = [FluxPerAngle(h, *profiles.LSST) for h in range(40, 440, 10)]
#     C = [convolve(s, d).calc_fwhm() for s, d in zip(S, D)]
#     C[1::5]
#         [35.44, 17.72, 11.81, 8.86, 7.09, 5.91, 5.06, 4.43]
# when the plots claim its for SDSS values, as discovered
# on January 30th 2020 by Dino Bektesevic.
# The top two graphs are correct however.
def figure23():
    fig, axes = plt.subplots(3, 1, figsize=(12, 24), sharex=True)

    # if the premade data products are missing, recreate them. Used parameters
    # match those used in the paper plots, output will be cached if produced. 
    heights = np.arange(40, 450, 10)
    seeings = np.arange(0.01, 5, 0.103)
    datafiles = (("sdss_point_data.npy",
                  {"source" : profiles.PointSource, "instrument" : profiles.SDSS}),
                 ("sdss_diskeq_data.npy",
                  {"source" : profiles.DiskSource, "radius" : 0.9, "instrument" : profiles.SDSS}),
                 ("sdss_diskgg_data.npy",
                  {"source" : profiles.DiskSource, "radius" : 3, "instrument" : profiles.SDSS}))
    data = get_or_create_data(datafiles, heights=heights, seeings=seeings)

    # set the contours
    cnt = {"levels" : [[2,3,4], [5,8]], "spacings" : [5, 3]}
    cnt2 = {"levels" : [[2,3,4,5], [8,10]], "spacings" : [5, -5]}
    contours = [cnt, cnt, cnt2]

    # heights and seeings can be reconstructed from the data, plus knows in
    # advance anyhow, but the observed FWHM and defocus FWHM need to be read.
    plotdata = [d['ofwhm'] for d in data]
    secydat = [d['dfwhm'][:,0] for d in data]
    fig, axes, twinaxes, cbaxes = figure232426(fig, axes, plotdata, seeings,
                                               heights, secydat=secydat,
                                               contours=contours,
                                               sharedcb=True,
                                               cbtitle="Observed FWHM (arcsec)")
    # tidy up axes labels and ticks
    twinaxes[1].set_ylabel("Defocus FWHM (arcsec)")
    axes[1].set_ylabel("Height (km)")
    axes[2].set_xlabel("Seeing FWHM (arcsec)")
    axes[0].get_xaxis().set_visible(False)
    axes[1].get_xaxis().set_visible(False)

    return fig, axes


def figure24():
    fig, axes = plt.subplots(3, 1, figsize=(12, 24), sharex=True)

    # if the premade data products are missing, recreate them. Used parameters
    # match those used in the paper plots, output will be cached if produced. 
    heights = np.arange(40, 450, 10)
    seeings = np.arange(0.01, 5, 0.103)
    datafiles = (("lsst_point_data.npy",
                  {"source" : profiles.PointSource, "instrument" : profiles.LSST}),
                 ("lsst_diskeq_data.npy",
                  {"source" : profiles.DiskSource, "radius" : 4, "instrument" : profiles.LSST}),
                 ("lsst_diskgg_data.npy",
                  {"source" : profiles.DiskSource, "radius" : 8, "instrument" : profiles.LSST}))
    data = get_or_create_data(datafiles, heights=heights, seeings=seeings)

    # set the contours, more complicated on this plot due to large gradient
    cnt1 = {"levels" : [[4,5,6,8], [12, 16, 20, 25, 30]], "spacings" : [5, 5]}
    cnt2 = {"levels" : [[5,6,8], [12, 16, 20, 25, 30]], "spacings" : [-5, -10]}
    contours = [cnt1, cnt2, cnt2]

    # heights and seeings can be reconstructed from the data, plus known in
    # advance, but the observed FWHM and defocus FWHM need to be read.
    plotdata = [d['ofwhm'] for d in data]
    secydat = [d['dfwhm'][:,0] for d in data]
    fig, axes, twinaxes, cbaxes = figure232426(fig, axes, plotdata, seeings,
                                               heights, secydat=secydat,
                                               contours=contours,
                                               sharedcb=True,
                                               cbtitle="Observed FWHM (arcsec)")
    # tidy up axes labels and ticks
    twinaxes[1].set_ylabel("Defocus FWHM (arcsec)")
    axes[1].set_ylabel("Height (km)")
    axes[2].set_xlabel("Seeing FWHM (arcsec)")

    axes[0].get_xaxis().set_visible(False)
    axes[1].get_xaxis().set_visible(False)

    return fig, axes


def figure25():
    fig, axes = plt.subplots(2, 1, figsize=(12, 24))

    # if the premade data products are missing, recreate them using same params
    # as in the paper and cache the calculation results. This plot is compiled
    # from two different sources of seeing and radii which is done manually
    heights1 = np.arange(55, 305, 5)
    radii1 = np.arange(0.01, 4.1, 0.05)
    datafiles = (("sdss_radii_data.npy",
                  {"source" : profiles.DiskSource, "seeing" : profiles.SDSSSEEING,
                   "instrument" : profiles.SDSS}), )
    dat1 = get_or_create_data(datafiles, heights=heights1, radii=radii1)

    heights2 = np.arange(55, 305, 5)
    radii2 = np.arange(0.01, 8.2, 0.103)
    datafiles = (("lsst_radii_data.npy",
                  {"source" : profiles.DiskSource, "seeing" : profiles.LSSTSEEING,
                   "instrument" : profiles.LSST}), )
    dat2 = get_or_create_data(datafiles, heights=heights1, radii=radii1)
    data = [dat1[0], dat2[0]]

    # set the contours
    cnt1 = {"levels" : [[2, 3, 4, 5, 6, 7, 8, 10]],
            "spacings" : [5]}
    cnt2 = {"levels" : [[6, 7, 8, 10, 12], [ 14, 18, 24]],
            "spacings" : [5, 1]}
    contours = [cnt1, cnt2]

    # this plot is different than previous because heights and seeings are not
    # shared across all the plots in the figure. Appropriate height and seeing
    # arrays are required so color mesh can be constricted.
    plotdata = [d['ofwhm'] for d in data]
    xdat = [radii1, radii2]
    ydat = [heights1, heights2]
    fig, axes, twinaxes, cbaxes = figure232426(fig, axes, plotdata, xdat, ydat,
                                               contours=contours, sharedcb=False,
                                               cbtitle="Observed FWHM (arcsec)",
                                               xlabels=("Radius (m)",)*2,
                                               ylabels=("Distance (km)",)*2)
    return fig, axes


def figure26():
    fig, axes = plt.subplots(2, 1, figsize=(12, 24))

    # if the premade data products are missing, recreate them. Used parameters
    # match those used in the paper plots, output will be cached if produced. 
    heights = np.arange(40, 450, 10)
    seeings = np.arange(0.01, 5, 0.103)
    datafiles = (("sdss_point_data.npy",
                  {"source" : profiles.PointSource, "instrument" : profiles.SDSS}),
                 ("lsst_point_data.npy",
                  {"source" : profiles.PointSource, "instrument" : profiles.LSST}))
    data = get_or_create_data(datafiles, heights=heights, seeings=seeings)

    # set the contours
    cnt1 = {"levels" : [[5,15,25,35]],
            "spacings" : [5]}
    cnt2 = {"levels" : [[5,15,25,35], [40,42,44,49]],
            "spacings" : [5, 1]}
    contours = [cnt1, cnt2]

    # heights and seeings can be reconstructed from the data, plus knows in
    # advance anyhow, but the observed FWHM and defocus FWHM need to be read.
    plotdata = [d['depth'] for d in data]
    secydat = [d['dfwhm'][:,0] for d in data]
    fig, axes, twinaxes, cbaxes = figure232426(fig, axes, plotdata, seeings,
                                               heights, secydat=secydat,
                                               contours=contours,
                                               sharedcb=False,
                                               cbtitle="Intensity loss (\% of max value)",
                                               xlabels=("Seeing FWHM (arcsec)",)*2,
                                               ylabels=("Distance (km)",)*2)

    # How I'd love mpl makes it easy to contextualize what is an axis' purpose,
    # untill then, manually setting axes is the only way.
    for ax, twax in zip(axes, twinaxes):
        twax.set_ylabel("Defocus FWHM (arcsec)")

    return fig, axes


def figure27():
    fig, axes = plt.subplots(2, 1, figsize=(12, 24))

    # this plot is compiled from two different sources of seeing and radii
    # which does have to be stated manually
    heights1 = np.arange(55, 305, 5)
    radii1 = np.arange(0.01, 4.1, 0.05)
    datafiles = (("sdss_radii_data.npy",
                  {"source" : profiles.DiskSource, "seeing" : profiles.SDSSSEEING,
                   "instrument" : profiles.SDSS}), )
    dat1 = get_or_create_data(datafiles, heights=heights1, radii=radii1)

    heights2 = np.arange(55, 305, 5)
    radii2 = np.arange(0.01, 8.2, 0.103)
    datafiles = (("lsst_radii_data.npy",
                  {"source" : profiles.DiskSource, "seeing" : profiles.LSSTSEEING,
                   "instrument" : profiles.LSST}), )
    dat2 = get_or_create_data(datafiles, heights=heights2, radii=radii2)
    data = [dat1[0], dat2[0]]

    # set the contours
    cnt1 = {"levels" : [[1, 5, 10, 15, 18, 20, 23]],
            "spacings" : [5]}
    cnt2 = {"levels" : [[1], range(5, 50, 5)],
            "spacings" : [5, 1]}
    contours = [cnt1, cnt2]

    # this plot is different than previous because heights and seeings are not
    # shared across all the plots in the figure. Appropriate height and seeing
    # arrays are required so color mesh can be constricted.
    plotdata = [d['depth'] for d in data]
    ydat = [heights1, heights2]
    xdat = [radii1, radii2]
    fig, axes, twinaxes, cbaxes = figure232426(fig, axes, plotdata, xdat, ydat,
                                               contours=contours,
                                               xlims=[(0.02, 1.8), (0.01, 8)],
                                               ylims=[(60, 181), (55, 300)],
                                               xlabels=("Radius (m)",)*2,
                                               ylabels=("Distance (km)",)*2,
                                               sharedcb=False,
                                               cbtitle="Intensity loss (\% of max value)")

    for ax, twax in zip(axes, twinaxes):
        ax.set_xlabel("Radius (m)")
        ax.set_ylabel("Distance (km)")

    return fig, axes