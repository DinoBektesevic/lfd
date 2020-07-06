import os
import re
import warnings

from matplotlib import rcParams
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np

from lfd.analysis.utils import *
from lfd.analysis.profiles import *
from lfd.analysis.plotting.utils import *


__all__ = ["plotall", "figure4", "figure5", "figure6", "figure7", "figure8", "figure10",
           "figure11", "figure12", "figure13", "figur1e14", "figure15", "figure16",
           "figure17", "figure23", "figure24", "figure25", "figure26", "figure27"]


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
    sdssdefocus = FluxPerAngle(h, profiles.SDSS)
    lsstdefocus = FluxPerAngle(h, profiles.LSST)
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

    sdssc = generic_sampler(PointSource, h=profiles.HEIGHTS)
    lsstc = generic_sampler(PointSource, instrument=profiles.LSST, h=profiles.HEIGHTS)
    for sp, lp, h in zip(sdssc, lsstc, profiles.HEIGHTS):
        ls = get_ls()
        plot_profile(axes[0], sp, label=f"${int(h)}km$", color="black", linestyle=ls)
        plot_profile(axes[1], lp, label=f"${int(h)}km$", color="black", linestyle=ls)

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
    # guard against sting-like values of rcParams when calling directly, if
    # rcParams titlesze is given assume it's paperplots context manager
    if isinstance(rcParams["axes.titlesize"], str):
        titlesize = rcParams["axes.titlesize"]
    else:
        titlesize = rcParams["axes.titlesize"] - 8

    fig, axes = plt.subplots(1, 3, sharey=True, figsize=(10, 10))
    axes[0].text(-10., 1.03, r"$D_{meteor} \ll D_{mirror}$",
                 fontsize=titlesize)
    axes[1].text(-13.0, 1.03, r"$D_{meteor} \approx D_{mirror}$",
                 fontsize=titlesize)
    axes[2].text(-17.0, 1.03, r"$D_{meteor} \gg D_{mirror}$",
                 fontsize=titlesize)
    axes = set_ax_props(axes,
                        xlims=((-12, 12), (-15, 16),( -21, 21)),
                        xticks=(range(-20, 21, 5), range(-21, 21, 7), range(-30, 31, 10)),
                        xlabels="arcsec", ylabels="Intensity")

    convs = generic_sampler(DiskSource, instrument=instrument,
                            seeingFWHM=seeingfwhm, h=(h,), radius=rs)
    for r, c, ax in zip(rs, convs, axes):
        d = DiskSource(h, r)
        plot_profiles(ax, (d, c), color="black", linestyles=('-', '--'),
                      labels=('Object', 'Observed'))

    plt.legend(bbox_to_anchor=(0.1, 1.0, 0.9, 0.), ncol=4, mode="expand",
               bbox_transform=plt.gcf().transFigure, loc="upper left")
    plt.subplots_adjust(bottom=0.1, left=0.12, right=0.98, top=0.92,
                        wspace=0.18)
    return fig, axes


def figures78(rs, instrument,  xlims, xticks, seeingfwhm=None):
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
    xlims : `list` or `tuple` of `lists` or `tuples`
        A list or tuple containing up to two nested lists or tuples. Each
        nested list or tuple contains two values (xmin, xmax) used to set
        individual axis x-axis limits. F.e. [(xmin1, xmax1), (xmin2, xmax2)].
    xticks : `list` or `tuple`
        A list or tuple containing up to two nested lists or tuples. Each
        nested list or tuple contains positions at which to mark and label the
        ticks at. Tick marks will be displayed for other equally spaced values
        but no labels will be displayed.
    seeingfwhm : `int` or `float`, optional
        Seeing FWHM in arcseconds, if known instrument is given can be None.

    Returns
    -------
    fig : `matplotlib.pyplot.Figure`
        Figure containing the plot.
    ax : `matplotlib.pyplot.Axes`
        Axes containing the plot.
    """
    if isinstance(rcParams["axes.titlesize"], str):
        titlesize = rcParams["axes.titlesize"]
    else:
        titlesize = rcParams["axes.titlesize"] - 8

    fig, axes = plt.subplots(1, 2, sharey=True, figsize=(10, 10))
    axes[0].text(xlims[0][0]/2.0, 1.03, r"$D_{meteor} \approx D_{mirror}$",
                 fontsize=titlesize)
    axes[1].text(xlims[1][0]/2.0, 1.03, r"$D_{meteor} \gg D_{mirror}$",
                 fontsize=titlesize)
    axes = set_ax_props(axes, xlims, xticks, xlabels="arcsec", ylabels="Intensity")

    profs = generic_sampler(DiskSource, instrument=instrument, radius=rs,
                            h=profiles.HEIGHTS, seeingFWHM=seeingfwhm)
    diskeq, diskgg = profs[:len(profiles.HEIGHTS)], profs[len(profiles.HEIGHTS):]

    # sampler iterates the last given param first, so they will be ordered by r
    for h, deq, dgg in zip( profiles.HEIGHTS, diskeq, diskgg):
        ls = get_ls()
        plot_profile(axes[0], deq, label=f"${int(h)}km$", color="black", linestyle=ls)
        plot_profile(axes[1], dgg, label=f"${int(h)}km$", color="black", linestyle=ls)

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
    return figures78(rs=(1, 4), instrument=profiles.SDSS,
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
    if isinstance(rcParams["axes.titlesize"], str):
        titlesize = rcParams["axes.titlesize"]
    else:
        titlesize = rcParams["axes.titlesize"] - 8

    fig, axes = plt.subplots(1, 3, sharey=True, figsize=(10, 10))
    # xlims[0][0]/2.0
    axes[0].text(xlims[0][0]/2.0, 1.03, r"$\theta_{rot} = 90^\circ$",
                 fontsize=titlesize)
    axes[1].text(xlims[0][0]/2.0, 1.03, r"$\theta_{rot} = 60^\circ$",
                 fontsize=titlesize)
    axes[2].text(xlims[0][0]/2.0, 1.03, r"$\theta_{rot} = 0^\circ$",
                 fontsize=titlesize)
    axes = set_ax_props(axes, xlims, xticks, xlabels="arcsec", ylabels="Intensity")

    seeing = GausKolmogorov(seeingfwhm)
    for h in profiles.HEIGHTS:
        defocus = FluxPerAngle(h, instrument)
        rab1 = RabinaSource(h, 0.0)
        rab2 = RabinaSource(h, 0.5)
        rab3 = RabinaSource(h, 1.5)

        ls = get_ls()
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
    axes = set_ax_props(axes, xlims, xticks, xlabels="arcsec", ylabels=("Intensity",)*3)
    axes[0].text(*txtpos[0], 'Gaussian trail evolution', fontsize=rcParams["axes.titlesize"])
    axes[1].text(*txtpos[1], 'Gaussian trail evolution \n defocused', fontsize=rcParams["axes.titlesize"])
    axes[2].text(*txtpos[2], 'All time-steps integrated', fontsize=rcParams["axes.titlesize"])
    axes[0].get_xaxis().set_visible(False)
    axes[1].get_xaxis().set_visible(False)

    gaussians = [GaussianSource(h, i) for i in profiles.exp_fwhms(tau, n, duration)]
    s = GausKolmogorov(seeingfwhm)
    d = FluxPerAngle(h, instrument)

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
    d = FluxPerAngle(h, instrument)
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


def figures1617(tau, h, seeingfwhm, instrument, xlims, xticks,
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
    d = FluxPerAngle(h, instrument)
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
    return  figures1617(1, 100, profiles.SDSSSEEING, profiles.SDSS,
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
    return figures1617(1, 100, profiles.LSSTSEEING, profiles.LSST, loc="upper center",
                      xlims=((-11.5,14.5),), xticks=(range(-20, 20, 5),))


def plot_param_space(fig, ax, xdat, ydat, data, secydat=None, pcollims=None,
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
        pcollims = (0, np.max(data))
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


def figures23242526(fig, axes, xdat, ydat, data, secydat=None, contours=None,
                   sharedcb=True, cbtitle=None, xlims=None, ylims=None,
                   xlabels="", ylabels="", **kwargs):
    """A genericized version of plots 23 to 26. Generally useful to create
    pseudo-colored parameter space plots for figures with multiple axes with a
    shared or individual colorbar and with or without the 3rd axis. Effectively
    calls `plot_param_space` for each of the given axis and then additionaly
    performs full-figure operations such as creating a single or multiple
    colorbar axes, or appending 3rd axis to each of the plots, maintains axis
    limits etc.

    Parameters
    ----------
    fig : `matplotlib.pyplot.Figure`
        Figure containing the plot.
    ax : `tuple` or `list`
        List of ``matplotlib.pyplot.Axes` on which to plot.
    data : `tuple` or `list`
        List containing the data, as a 2D `numpy.array`, that will make the
        central color plot on each axis.
    xdat : `list`, `tuple` or `numpy.array`
        Data that will be used to stretch the x axis of the plot, f.e. seeing.
    ydat : `list`, `tuple` or `numpy.array`
        Data that will be used to stretch the y axis of the plot, f.e. heights.
    secydat : `list`, `tuple`, `numpy.array` or `None`
        Optional. If not None a 3rd axis will be added to the plot, i.e. a 2nd
        y axis. The data contained in secydat will be used to create labels for
        that axis, therefore data provided should be invariant to xdat data.
    contours : `list`, `tuple`, `numpy.array` or `None`
        Optional. List of values at which contours will be drawn. If None, no
        countours are drawn.
    sharedcb : `bool`
        If True the entire figure will contain a single colorbar at the top of
        the plot. Else, each axis will have a colorbar attached to it. True by
        default.
    cbtitle : `str` or `None`
        Optional. Title displayed on top of the colorbar.
    xlims : `list`, `tuple` or `None`
        Optional. A nested list or tuple each element of which is a (min, max)
        value used to set limits of the x axes of the plot. If None the limits
        are determined as minimal and maximal values of the data plotted. See
        `lfd.analysis.plotting.paperplots.set_ax_props` for more.
    ylims : `list`, `tuple` or `None`
        Optional. A nested list or tuple each element of which is a (min, max)
        value used to set limits of the y axes of the plot. If None the limits
        are determined as minimal and maximal values of the data plotted. See
        `lfd.analysis.plotting.paperplots.set_ax_props` for more.
    xlabels : `list`, `tuple`, `str` or generator expression
        Optional. No x axis labels are created if not provided. If a string
        only the edge axis are labeled, if an iterable all axes will be
        labeled. See `lfd.analysis.plotting.paperplots.set_ax_props` for more.
    ylabels : `list`, `tuple`, `str` or generator expression
        Optional. No y axis labels are created when not provided. If a string
        only the edge axis are labeled, if an iterable all axes will be
        labeled. See `lfd.analysis.plotting.paperplots.set_ax_props` for more.
    **kwargs : `dict`
        Dictionary of any additional keywords is forwarded to
        `plot_param_space` function.

    Returns
    -------
    fig  : `matplotlib.pyplot.Figure`
        Figure containing the plot.
    axes : `list` or `tuple`
        List of all the main `matplotlib.pyplot.Axes` in the figure.
    twinaxes : `list`
        List of `matplotlib.pyplot.Axes`. If secydat data is given any created
        secondary axes are returned in this list. Otherwise it's empty.
    cbaxes : `list`
        List of `matplotlib.pyplot.Axes` containing all the axes that contain
        colorbars.
    """
    # clean up the arguments. Technically each plot can have completely
    # arbitrary x, y axis and plot data. Realistically, they will share them so
    # for brevity we allow simple lists as x and y data but then sanitize them
    if len(xdat) != len(data):
        xdat = (xdat,)*len(data)
    if len(ydat) != len(data):
        ydat = (ydat,)*len(data)
    cbtitle = "" if cbtitle is None else cbtitle

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
    for ax, xax, yax, d, syd, cnt in zip(axes, xdat, ydat, data, secydat, contours):
        pcol1, ax2 = plot_param_space(fig, ax, xax, yax, d, secydat=syd,
                                      contours=cnt, colors="white", **kwargs)
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


# The paper plot must be wrong because the bottom defocusing values actually
# correspond to the following:
#     S = [DiskSource(h, 8) for h in range(40, 440, 10)]
#     D = [FluxPerAngle(h, *profiles.LSST) for h in range(40, 440, 10)]
#     C = [convolve(s, d).calc_fwhm() for s, d in zip(S, D)]
#     C[1::5]
#         [35.44, 17.72, 11.81, 8.86, 7.09, 5.91, 5.06, 4.43]
# when the plots claim its for SDSS values, as discovered
# on January 30th 2020 by Dino Bektesevic.
# The top two graphs are correct however.
def figure23():
    """Plot of the observed FWHM (color scale and contours) as a function of
    distance and seeing for SDSS in three cases (from the top to bottom): point
    source, a uniform disk of R_meteor=0.9m (~R_mirror) and a uniform disk of
    R_meteor=3m (>> R_mirror). The right axis shows the defocussing FWHM for
    distances indicated on the left axis. This is the convolution of source
    profile with defocusing only. The dashed line represents FWHM for which
    the seeing is identical to the defocussing at agiven height. Points above
    the dashed line are dominated by the seeing FWHM, while defocusing
    dominates points below the line.

    Returns
    -------
    fig  : `matplotlib.pyplot.Figure`
        Figure containing the plot.
    axes : `list` or `tuple`
        List of all the main `matplotlib.pyplot.Axes` in the figure.
    twinaxes : `list`
        List of `matplotlib.pyplot.Axes`. If secydat data is given any created
        secondary axes are returned in this list. Otherwise it's empty.
    cbaxes : `list`
        List of `matplotlib.pyplot.Axes` containing all the axes that contain
        colorbars.
    """
    fig, axes = plt.subplots(3, 1, figsize=(12, 24), sharex=True)

    # if the premade data products are missing, recreate them. Used parameters
    # match those used in the paper plots, output will be cached if produced.x
    heights = np.arange(40, 450, 10)
    seeings = np.arange(0.01, 5, 0.103)
    skwargs = ({"sources" : PointSource},
               {"sources" : DiskSource, "radius" : (0.9, 3)})
    data = get_or_create_data(("sdss_point_data.npy", "sdss_disk_data.npy"),
                              samplerKwargs=skwargs, h=heights, seeingFWHM=seeings,
                              instrument=SDSS)

    plotdata = [meshgrid(data[0], 'sfwhm', 'h', 'ofwhm', axes=False),
                meshgrid(data[1], 'sfwhm', 'h', 'ofwhm', fold={'radius':0.9}, axes=False),
                meshgrid(data[1], 'sfwhm', 'h', 'ofwhm', fold={'radius':3}, axes=False)]
    # gridding on defocus gets us rows of same values, we only need a column
    secydat = [meshgrid(data[0], 'sfwhm', 'h', 'dfwhm', axes=False)[:,0],
               meshgrid(data[1], 'sfwhm', 'h', 'dfwhm', fold={'radius':0.9}, axes=False)[:,0],
               meshgrid(data[1], 'sfwhm', 'h', 'dfwhm', fold={'radius':3}, axes=False)[:,0]]


    # set the contours
    cnt = {"levels" : [[2,3,4], [5,8]], "spacings" : [5, 3]}
    cnt2 = {"levels" : [[2,3,4,5], [8,10]], "spacings" : [5, -5]}
    contours = [cnt, cnt, cnt2]

    fig, axes, twinaxes, cbaxes = figures23242526(fig, axes, seeings, heights,
                                                  plotdata, secydat=secydat,
                                                  contours=contours,
                                                  sharedcb=True,
                                                  cbtitle="Observed FWHM (arcsec)")
    # tidy up axes labels and ticks
    twinaxes[1].set_ylabel("Defocus FWHM (arcsec)")
    axes[1].set_ylabel("Height (km)")
    axes[2].set_xlabel("Seeing FWHM (arcsec)")
    axes[0].get_xaxis().set_visible(False)
    axes[1].get_xaxis().set_visible(False)

    return fig, axes, twinaxes, cbaxes


def figure24():
    """Plot of the observed FWHM (color scale and contours) as a function of
    distance and seeing for LSST in three cases (from the top to bottom): point
    source, a uniform disk of R_meteor=4m (~R_mirror) and a uniform disk of
    R_meteor=8m (>> R_mirror). The right axis shows the defocussing FWHM for
    distances indicated on the left axis. This is the convolution of source
    profile with defocusing only. The dashed line represents FWHM for which
    the seeing is identical to the defocussing at agiven height. The observed
    FWHM is almost completely dominated by the defocusing effect for the range
    of distances and seeing shown in these panels.

    Returns
    -------
    fig  : `matplotlib.pyplot.Figure`
        Figure containing the plot.
    axes : `list` or `tuple`
        List of all the main `matplotlib.pyplot.Axes` in the figure.
    twinaxes : `list`
        List of `matplotlib.pyplot.Axes`. If secydat data is given any created
        secondary axes are returned in this list. Otherwise it's empty.
    cbaxes : `list`
        List of `matplotlib.pyplot.Axes` containing all the axes that contain
        colorbars.
    """
    fig, axes = plt.subplots(3, 1, figsize=(12, 24), sharex=True)

    # if the premade data products are missing, recreate them. Used parameters
    # match those used in the paper plots, output will be cached if produced.
    heights = np.arange(40, 450, 10)
    seeings = np.arange(0.01, 5, 0.103)
    skwargs = ({"sources" : PointSource},
               {"sources" : DiskSource, "radius" : (4, 8)})
    data = get_or_create_data(("lsst_point_data.npy", "lsst_disk_data.npy"),
                              samplerKwargs=skwargs, h=heights, seeingFWHM=seeings,
                              instrument=LSST)

    plotdata = [meshgrid(data[0], 'sfwhm', 'h', 'ofwhm', axes=False),
                meshgrid(data[1], 'sfwhm', 'h', 'ofwhm', fold={'radius':4}, axes=False),
                meshgrid(data[1], 'sfwhm', 'h', 'ofwhm', fold={'radius':8}, axes=False)]
    # gridding on defocus gets us rows of same values, we only need a column
    secydat = [meshgrid(data[0], 'sfwhm', 'h', 'dfwhm', axes=False)[:,0],
               meshgrid(data[1], 'sfwhm', 'h', 'dfwhm', fold={'radius':4}, axes=False)[:,0],
               meshgrid(data[1], 'sfwhm', 'h', 'dfwhm', fold={'radius':8}, axes=False)[:,0]]

    # set the contours, more complicated on this plot due to large gradient
    cnt1 = {"levels" : [[4,5,6,8], [12, 16, 20, 25, 30]], "spacings" : [5, 5]}
    cnt2 = {"levels" : [[5,6,8], [12, 16, 20, 25, 30]], "spacings" : [-5, -10]}
    contours = [cnt1, cnt2, cnt2]

    fig, axes, twinaxes, cbaxes = figures23242526(fig, axes, seeings, heights,
                                                  plotdata, secydat=secydat,
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
    """The observed FWHM (color scale and contours) as afunction of a uniform
    brightness disk radius and meteor distance to the telescope. The top panel
    is for the case of SDSS (the seeing FWHM fixed to 1.48′′) and the bottom is
    for LSST (seeing is 0.67′′).

    Returns
    -------
    fig  : `matplotlib.pyplot.Figure`
        Figure containing the plot.
    axes : `list` or `tuple`
        List of all the main `matplotlib.pyplot.Axes` in the figure.
    twinaxes : `list`
        List of `matplotlib.pyplot.Axes`. If secydat data is given any created
        secondary axes are returned in this list. Otherwise it's empty.
    cbaxes : `list`
        List of `matplotlib.pyplot.Axes` containing all the axes that contain
        colorbars.
    """
    fig, axes = plt.subplots(2, 1, figsize=(12, 24))

    # if the premade data products are missing, recreate them using same params
    # as in the paper and cache the calculation results. This plot is compiled
    # from two different sources of seeing and radii which is done manually
    heights = np.arange(55, 305, 5)
    radii1 = np.arange(0.01, 4.1, 0.05)
    radii2 = np.arange(0.01, 8.2, 0.103)
    skwargs = ({"sources" : DiskSource, "radius": radii1, "instrument": SDSS},
               {"sources" : DiskSource, "radius": radii2, "instrument": LSST})
    datafile = ("sdss_radii_data.npy", "lsst_radii_data.npy")
    data = get_or_create_data(datafile, heights=heights, radii=radii1, sources=skwargs)

    # set the contours
    cnt1 = {"levels" : [[2, 3, 4, 5, 6, 7, 8, 10]],
            "spacings" : [5]}
    cnt2 = {"levels" : [[6, 7, 8, 10, 12], [ 14, 18, 24]],
            "spacings" : [5, 1]}
    contours = [cnt1, cnt2]

    # this plot is different than previous because heights and seeings are not
    # shared across all the plots in the figure. Appropriate height and seeing
    # arrays are required so color mesh can be constricted.
    xdat = [radii1, radii2]
    ydat = [heights, heights]
    plotdata = [meshgrid(data[0], 'radius', 'h', 'ofwhm', axes=False),
                meshgrid(data[1], 'radius', 'h', 'ofwhm', axes=False)]

    fig, axes, twinaxes, cbaxes = figures23242526(fig, axes, xdat, ydat, plotdata,
                                                  contours=contours, sharedcb=False,
                                                  cbtitle="Observed FWHM (arcsec)",
                                                  xlabels=("Radius (m)",)*2,
                                                  ylabels=("Distance (km)",)*2)
    return fig, axes, twinaxes, cbaxes


def figure26():
    """The strength of the central dip for a point source in the observed
    image profile measured as the intensity loss (colorscale and contours)
    relative to the maximum brightness value im the profile (see e.g. Figs.4
    and 5). The panels show how the intensity loss depends on seeing and
    distance from the meteor in SDSS (top panel) and LSST (bottom panel). The
    right axis shows the defocusing FWHM for distances indicated on the left
    axis. These are FWHM of the convolution profile of source profile and
    defocusing effects only.

    Returns
    -------
    fig  : `matplotlib.pyplot.Figure`
        Figure containing the plot.
    axes : `list` or `tuple`
        List of all the main `matplotlib.pyplot.Axes` in the figure.
    twinaxes : `list`
        List of `matplotlib.pyplot.Axes`. If secydat data is given any created
        secondary axes are returned in this list. Otherwise it's empty.
    cbaxes : `list`
        List of `matplotlib.pyplot.Axes` containing all the axes that contain
        colorbars.
    """
    fig, axes = plt.subplots(2, 1, figsize=(12, 24))

    # if the premade data products are missing, recreate them. Used parameters
    # match those used in the paper plots, output will be cached if produced.
    heights = np.arange(40, 450, 10)
    seeings = np.arange(0.01, 5, 0.103)
    sources = ({"source" : PointSource, "instrument" : SDSS},
               {"source" : PointSource, "instrument" : LSST})
    datafiles = ("sdss_point_data.npy", "lsst_point_data.npy")
    data = get_or_create_data(datafiles, heights=heights, seeings=seeings,
                              sources=sources)

    # set the contours
    cnt1 = {"levels" : [[5,15,25,35]],
            "spacings" : [5]}
    cnt2 = {"levels" : [[5,15,25,35], [40,42,44,49]],
            "spacings" : [5, 1]}
    contours = [cnt1, cnt2]

    # heights and seeings can be reconstructed from the data, plus knows in
    # advance anyhow, but the observed FWHM and defocus FWHM need to be read.
    plotdata = [meshgrid(data[0], 'sfwhm', 'h', 'depth', axes=False),
                meshgrid(data[1], 'sfwhm', 'h', 'depth', axes=False)]
    secydat = [meshgrid(data[0], 'sfwhm', 'h', 'dfwhm', axes=False)[:,0],
               meshgrid(data[1], 'sfwhm', 'h', 'dfwhm', axes=False)[:,0]]

    fig, axes, twinaxes, cbaxes = figures23242526(fig, axes, seeings, heights,
                                                  plotdata, secydat=secydat,
                                                  contours=contours,
                                                  sharedcb=False,
                                                  cbtitle="Intensity loss (\% of max value)",
                                                  xlabels=("Seeing FWHM (arcsec)",)*2,
                                                  ylabels=("Distance (km)",)*2)

    # How I'd love mpl makes it easy to contextualize what is an axis' purpose,
    # untill then, manually setting axes is the only way.
    for ax, twax in zip(axes, twinaxes):
        twax.set_ylabel("Defocus FWHM (arcsec)")

    return fig, axes, twinaxes, cbaxes


def figure27():
    """The strength of the central dip for a disk source in the observed
    image profile measured as the intensity loss (colorscale and contours)
    relative to the maximum brightness value im the profile (see e.g. Figs.4
    and 5). The horizontal axis shows the meteor head radius. The seeing is
    set to 1.48′′for SDSS (top panel) and 0.67′′for LSST (bottom panel).

    Returns
    -------
    fig  : `matplotlib.pyplot.Figure`
        Figure containing the plot.
    axes : `list` or `tuple`
        List of all the main `matplotlib.pyplot.Axes` in the figure.
    twinaxes : `list`
        List of `matplotlib.pyplot.Axes`. If secydat data is given any created
        secondary axes are returned in this list. Otherwise it's empty.
    cbaxes : `list`
        List of `matplotlib.pyplot.Axes` containing all the axes that contain
        colorbars.
    """
    fig, axes = plt.subplots(2, 1, figsize=(12, 24))

    # this plot is compiled from two different sources of seeing and radii
    # which does have to be stated manually
    heights = np.arange(55, 305, 5)
    radii1 = np.arange(0.01, 4.1, 0.05)
    radii2 = np.arange(0.01, 8.2, 0.103)
    skwargs = ({"sources" : DiskSource, "radius": radii1, "instrument": SDSS},
               {"sources" : DiskSource, "radius": radii2, "instrument": LSST})
    datafile = ("sdss_radii_data.npy", "lsst_radii_data.npy")
    data = get_or_create_data(datafile, heights=heights, radii=radii1, sources=skwargs)

    # set the contours
    cnt1 = {"levels" : [[1, 5, 10, 15, 18, 20, 23]],
            "spacings" : [5]}
    cnt2 = {"levels" : [[1], range(5, 50, 5)],
            "spacings" : [5, 1]}
    contours = [cnt1, cnt2]

    # this plot is different than previous because heights and seeings are not
    # shared across all the plots in the figure. Appropriate height and seeing
    # arrays are required so color mesh can be constricted.
    xdat = [radii1, radii2]
    ydat = [heights, heights]
    plotdata = [meshgrid(data[0], 'radius', 'h', 'depth', axes=False),
                meshgrid(data[1], 'radius', 'h', 'depth', axes=False)]

    fig, axes, twinaxes, cbaxes = figures23242526(fig, axes, xdat, ydat, plotdata,
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

    return fig, axes, twinaxes, cbaxes


def plotall(path="."):
    """Create PNG image files containing figures 4 to 27 as they appeared in
    the::

      Bektesevic & Vinkovic et. al. 2017 (arxiv: 1707.07223)

    paper at a given location.

    Parameters
    ---------
    path : `str`
        Optional. Path to location in which images will be stored. Defaults to
        current directory.
    """
    globs = globals()
    abspath = os.path.abspath(path)
    plotfuns = [f for f in globs if re.search(r"figure\d+", f)]
    for plotfun in plotfuns:
        with paperstyle():
            fig, axes, *rest = globs[plotfun]()
            plt.savefig(os.path.join(abspath, plotfun+".png"))
            plt.close(fig)
