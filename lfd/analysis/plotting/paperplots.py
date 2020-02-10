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


def set_ax_props(axes, xlims=(), xticks=(), xlabel="arcsec",
                 ylabel="Intensity", ylims =((-0.01, 1.1),)):
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
        setprop = False
        if len(prop) != 0:
            setprop = True
            if len(prop) < lentresh:
                prop *= lentresh
        else:
            # this is a nonsense prop so that zip doesn't truncate
            # remaining props, if we're here - this prop shouldn't be set
            prop = range(len(lentresh))
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

    # only simple plots that share either x or y axes are used here. If axes
    # are grouped together then only leftmost and bottommost get markings.
    xgrouper = [ax for ax in axes[0].get_shared_x_axes()]
    ygrouper = [ax for ax in axes[0].get_shared_y_axes()]
    xlabels = False if len(xgrouper) != 0 else True
    ylabels = False if len(ygrouper) != 0 else True
    # it should be always safe to label extreme borders
    axes[0].set_ylabel(ylabel)
    axes[-1].set_xlabel(xlabel)

    for (ax, ticks, xlim, ylim)  in zip(axes, xticks, xlims, ylims):
        if xlabels:
            ax.set_xlabel(xlabel)
        if ylabels:
            ax.set_ylabel(ylabel)
        if setxticks:
            ax.set_xticks(ticks)
        if setxlims:
            ax.set_xlim(xlim)
        if setylims:
            ax.set_ylim(ylim)

    return axes


def figure4(h=100):
    fig, axes = plt.subplots(1, 2, sharey=True, figsize=(10, 10))
    axes[0].text(-1.2, 1.03,  'SDSS', fontsize=rcParams["axes.titlesize"])
    axes[1].text(-3.35, 1.03, 'LSST', fontsize=rcParams["axes.titlesize"])
    axes = set_ax_props(axes, xlims =((-5.5, 5.5), (-15.5, 15.5)),
                        xticks=(range(-25, 26, 5), range(-20, 21, 5)))

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
    fig, axes = plt.subplots(1, 2, sharey=True, figsize=(10, 10))
    axes[0].text(-1.2, 1.03, 'SDSS', fontsize=rcParams["axes.titlesize"])
    axes[1].text(-3.0, 1.03, 'LSST', fontsize=rcParams["axes.titlesize"])
    axes = set_ax_props(axes, xlims =((-5.5, 5.5), (-15.5, 15.5)),
                        xticks=(range(-25, 26, 5), range(-20, 21, 5)))

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
    fig, axes = plt.subplots(1, 3, sharey=True, figsize=(10, 10))
    axes[0].text(-10., 1.03, r"$D_{meteor} \ll D_{mirror}$",
                 fontsize=rcParams["axes.titlesize"]-8)
    axes[1].text(-13.0, 1.03, r"$D_{meteor} \approx D_{mirror}$",
                 fontsize=rcParams["axes.titlesize"]-8)
    axes[2].text(-17.0, 1.03, r"$D_{meteor} \gg D_{mirror}$",
                 fontsize=rcParams["axes.titlesize"]-8)
    axes = set_ax_props(axes,
                        xlims=((-12, 12), (-15, 16),( -21, 21)),
                        xticks=(range(-20, 21, 5), range(-21, 21, 7), range(-30, 31, 10)))

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
    fig, axes = plt.subplots(1, 2, sharey=True, figsize=(10, 10))
    axes[0].text(xlims[0][0]/2.0, 1.03, r"$D_{meteor} \approx D_{mirror}$",
                 fontsize=rcParams["axes.titlesize"]-8)
    axes[1].text(xlims[1][0]/2.0, 1.03, r"$D_{meteor} \gg D_{mirror}$",
                 fontsize=rcParams["axes.titlesize"]-8)
    axes = set_ax_props(axes, xlims, xticks)

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
    return figures78(rs=(1, 4), instrument=profiles.SDSS, seeingfwhm=profiles.SDSSSEEING,
                     xlims=((-6, 6), (-11, 11)), xticks=(range(-30, 30, 2),))


def figure8():
    return figures78(rs=(4, 8), instrument=profiles.LSST,
                     seeingfwhm=profiles.LSSTSEEING,
                     xlims=((-18, 18), (-25, 25)),
                     xticks=(range(-30, 30, 6), range(-30, 30, 10)))


def figures1011(seeingfwhm, instrument, xlims, xticks):
    fig, axes = plt.subplots(1, 3, sharey=True, figsize=(10, 10))
    # xlims[0][0]/2.0
    axes[0].text(xlims[0][0]/2.0, 1.03, r"$\theta_{rot} = 90^\circ$",
                 fontsize=rcParams["axes.titlesize"]-6)
    axes[1].text(xlims[0][0]/2.0, 1.03, r"$\theta_{rot} = 60^\circ$",
                 fontsize=rcParams["axes.titlesize"]-6)
    axes[2].text(xlims[0][0]/2.0, 1.03, r"$\theta_{rot} = 0^\circ$",
                 fontsize=rcParams["axes.titlesize"]-6)
    axes = set_ax_props(axes, xlims, xticks)

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
    return figures1011(profiles.SDSSSEEING, profiles.SDSS, ((-7.5, 7.5),),
                       (range(-25, 26, 5), ))


def figure11():
    return figures1011(profiles.LSSTSEEING, profiles.LSST, ((-15.5, 15.5), ),
                       (range(-20, 21, 10), ))


def figure1213(tau, h, seeingfwhm, instrument, xlims, xticks, txtpos,
               n=10, duration=2):
    fig, axes = plt.subplots(3, 1, sharex=True, figsize=(12, 14))
    axes = set_ax_props(axes, xlims, xticks)
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

    plt.subplots_adjust(bottom=0.07, left=0.07, right=0.97, top=0.98, hspace=0.08)
    return fig, axes #plt.show()


def figure12():
    return figure1213(1, 100, profiles.SDSSSEEING, profiles.SDSS,
                      xlims=((-8.5,8.5),), xticks=(range(-20, 20, 2),),
                      txtpos=((2,0.8), (2,0.8), (2,0.8)))


def figure13():
    return figure1213(1, 100, profiles.LSSTSEEING, profiles.LSST,
                      xlims=((-15,15),), xticks=(range(-20, 20, 2),),
                      txtpos=((2,0.8), (-5,0.28), (2,0.8)))


def figure1415(tau, h, seeingfwhm, instrument, xlims, xticks, txtpos,
               n=10, duration=2, nsteps=486):
    fig, axes = plt.subplots(3, 1, sharex=True, figsize=(12, 14))
    axes = set_ax_props(axes, xlims, xticks)
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

    plt.subplots_adjust(bottom=0.09, left=0.09, right=0.99, top=0.98, hspace=0.04)
    return fig, axes


def figure14():
    return figure1415(1, 100, profiles.SDSSSEEING, profiles.SDSS,
                      xlims=((-4.5,12.5),), xticks=(range(-20, 20, 2),),
                      txtpos=((6,0.6), (6,0.6), (6,0.6)))


def figure15():
    return figure1415(1, 100, profiles.LSSTSEEING, profiles.LSST,
                      xlims=((-10.5,17.5),), xticks=(range(-20, 20, 5),),
                      txtpos=((9,0.6), (9,0.6), (9,0.6)))


def figure1617(tau, h, seeingfwhm, instrument, xlims, xticks,
               n=10, duration=2, nsteps=486, loc="upper right"):
    fig, ax = plt.subplots(figsize=(12, 10))
    ax = set_ax_props(ax, xlims, xticks)[0]

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
    return  figure1617(1, 100, profiles.SDSSSEEING, profiles.SDSS,
                       xlims=((-5.5,10.5),), xticks=(range(-20, 20, 2),))


def figure17():
    return figure1617(1, 100, profiles.LSSTSEEING, profiles.LSST, loc="upper center",
                      xlims=((-11.5,14.5),), xticks=(range(-20, 20, 5),))


def param_space_sampler(heights, seeings, source, instrument, **kwargs):
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
            diff = (top-mid)*100.0

            data["seeing"][i,j] = s
            data['sfwhm'][i,j] = S.calc_fwhm()
            data['ofwhm'][i,j] = C.calc_fwhm()
            data['depth'][i,j] = diff/top
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


def plot_param_space(fig, ax, data, plot, pcollims=None, contours=None, twax=False, **kwargs):
    heights = data["height"][:,0]
    seeings = data["seeing"][0,:]

    if pcollims is None:
        pcollims = (0, data[plot].max())
    pcol = ax.pcolormesh(seeings, heights, data[plot], vmin=pcollims[0], vmax=pcollims[1])

    def standardize_spacing():
        resetarg = False
        resetval = None
        if  isinstance(contours, dict) and "spacings" in contours:
            spcs = contours["spacings"]
        elif "inline_spacing" in kwargs:
            resetarg = True
            saveval = kwargs["inline_spacing"]
            try:
                spcs = itertools.cycle(saveval)
            except TypeError:
                spcs = itertools.cycle([saveval])
        else:
            spcs = itertools.cycle([5])
        spacing = kwargs.pop("spacings", spcs)

        return spacing, (resetarg, resetval)

    color = kwargs.pop("colors", None)
    fntsize = rcParams["legend.fontsize"]
    spacing, (resetspacing, resetval) = standardize_spacing()

    def draw_contours(contours, spacings, **kwargs):
        for cnts, spc in zip(contours, spacings):
            c = ax.contour(seeings, heights, data[plot], levels=cnts,
                           colors=color, **kwargs)
            c.levels = list(map(str, cnts))
            ax.clabel(c, fontsize=fntsize, inline=True, inline_spacing=spc,
                      colors=color, **kwargs)

    if isinstance(contours, dict):
        draw_contours(contours["levels"], spacing)
        if resetspacing:
            kwargs['inline_spacing'] = resetval
    elif contours:
        draw_contours([contours,], spacing)
    else:
        ax.contour(seeings, heights, data[plot], colors=color, **kwargs)

    if twax:
        ax2 = ax.twinx()
        ax2.plot(data['dfwhm'][:,0], heights, linestyle="--", color="white")
        ax2.set_ylim(min(heights), max(heights))
        # getting ax2.get_xticks and xticklabels gets me nothing sensible! So the
        # matching between defocused FWHM and height has to be done manually. We
        # skip the first tick (40km) via [1:: , grab every 5th defocus fwhm as
        # [1::5 . Data has defocus fwhm per seeing but fwhm changes only with
        # height - we need 1st element of each only. Ergo [1::5,0])
        labels = [f"${d:.2f}$" for d in data['dfwhm'][1::5,0]]
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


def figure232426(fig, axes, data, contours=[None], plot='ofwhm', sharedcb=True, cbtitle=None, twax=False, xlims=None, ylims=None, **kwargs):
    heights = data[0]["height"][:,0]
    seeings = data[0]["seeing"][0,:]
    cbtitle = plot if cbtitle is None else cbtitle

    # if the colorbar is shared to make sure we are looking at the same color
    # ranges create a silly colorbar based on data extrema and then use its
    # normalization to re-color the data graphs.
    cbaxes = []
    if sharedcb:
        pcolmax = max([d[plot].max() for d in data])
        pcolmin = min([d[plot].min() for d in data])
        pcollims = (pcolmin, pcolmax)
        pcol = np.linspace(*pcollims, len(heights)*len(seeings))
        pcol = pcol.reshape(len(heights), len(seeings))
        pcol = axes[0].pcolormesh(seeings, heights, pcol)

        # position the colorbar axes on top when shared plots and
        # plot it with the fake data created above
        cax = fig.add_axes([0.12, 0.93, 0.76, 0.01])
        cax.text(0.5, 3.5, cbtitle, horizontalalignment='center', verticalalignment='center',
                 fontsize=rcParams["axes.titlesize"], transform=cax.transAxes)
        colbar = fig.colorbar(pcol, orientation="horizontal", cax=cax)
        colbar.ax.xaxis.set_ticks_position('top')
        colbar.ax.xaxis.set_label_position('top')
        adjustvals = {"bottom":0.05, "left":0.12, "right":0.88, "top":0.92, "hspace":0.03}

    # now plot the parameter space data
    twinx = []
    for ax, dat, cnt in zip(axes, data, contours):
        pcol1, ax2 = plot_param_space(fig, ax, dat, plot, contours=cnt,
                                      colors="white", twax=twax, **kwargs)
        twinx.append(ax2)
        # but if the colorbar was not shared, plot each axis
        # colorbar individually
        if not sharedcb:
            divider = make_axes_locatable(ax)
            cax = divider.append_axes('top', size='5%', pad=0.1)
            cbaxes.append(cax)
            colbar = fig.colorbar(pcol1, orientation="horizontal", cax=cax)
            colbar.set_label(cbtitle, fontsize=rcParams["axes.titlesize"])
            colbar.ax.xaxis.set_ticks_position('top')
            colbar.ax.xaxis.set_label_position('top')
            adjustvals = {"bottom":0.05, "left":0.1, "right":0.88, "top":0.96, "hspace":0.25}

    # for the radii graphs the x axis changes from plot to plot
    # this isn't desired for the fake CBs for the triple plots
    # so this is a bit of hack to get this function to work for both.
    if xlims is not None:
        for xlim, ax, ax2 in zip(xlims, axes, twinx):
            if twax:
                ax2.set_xlim(*xlim)
            ax.set_xlim(*xlim)

        if len(xlims) < len(axes):
            i = len(xlims)
            for dat, ax, ax2 in zip(data[i:], axes[i:], twinx[i:]):
                seeings = dat["seeing"][0,:]
                mins, maxs = min(seeings), max(seeings)
                if twax:
                    ax2.set_xlim(mins, maxs)
                ax.set_xlim(mins, maxs)

    if ylims is not None:
        for ylim, ax, ax2 in zip(ylims, axes, twinx):
            if twax:
                ax2.set_ylim(*ylim)
            ax.set_ylim(*ylim)

        if len(ylims) < len(axes):
            for dat, ax, ax2 in zip(data[i:], axes[i:], twinx[i:]):
                heights = dat["height"][:,0]
                minh, maxh = min(heights), max(heights)
                if twax:
                    ax2.set_ylim(minh, maxh)
                ax.set_ylim(minh, maxh)

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

    heights = np.arange(40, 450, 10)
    seeings = np.arange(0.01, 5, 0.103)

    # if the premade data products are missing we need to recreate them.
    # The dictionary associated with file-name sets param_space_sampler
    # arguments to values used in the paper.
    datafiles = (("sdss_point_data.npy",
                  {"source" : profiles.PointSource, "instrument" : profiles.SDSS}),
                 ("sdss_diskeq_data.npy",
                  {"source" : profiles.DiskSource, "radius" : 0.9, "instrument" : profiles.SDSS}),
                 ("sdss_diskgg_data.npy",
                  {"source" : profiles.DiskSource, "radius" : 3, "instrument" : profiles.SDSS}))
    data = get_or_create_data(datafiles, heights=heights, seeings=seeings)

    cnt1 = [2, 3, 4, 5, 8]
    cnt2 = {"levels" : [[2,3,4], [5,8, 10,]], "spacings":[5, 1]}
    contours = [cnt1, cnt1, cnt2]

    fig, axes, twinaxes, cbaxes = figure232426(fig, axes, data, contours, plot="ofwhm",
                                               sharedcb=True, cbtitle="Observed FWHM (arcsec)",
                                               twax=True)

    twinaxes[1].set_ylabel("Defocus FWHM (arcsec)")
    axes[1].set_ylabel("Height (km)")
    axes[2].set_xlabel("Seeing FWHM (arcsec)")

    axes[0].get_xaxis().set_visible(False)
    axes[1].get_xaxis().set_visible(False)

    return fig, axes


def figure24():
    fig, axes = plt.subplots(3, 1, figsize=(12, 24), sharex=True)

    heights = np.arange(40, 450, 10)
    seeings = np.arange(0.01, 5, 0.103)

    # if the premade data products are missing we need to recreate them.
    # The dictionary associated with file-name sets param_space_sampler
    # arguments to values used in the paper.
    datafiles = (("lsst_point_data.npy",
                  {"source" : profiles.PointSource, "instrument" : profiles.LSST}),
                 ("lsst_diskeq_data.npy",
                  {"source" : profiles.DiskSource, "radius" : 4, "instrument" : profiles.LSST}),
                 ("lsst_diskgg_data.npy",
                  {"source" : profiles.DiskSource, "radius" : 8, "instrument" : profiles.LSST}))
    data = get_or_create_data(datafiles, heights=heights, seeings=seeings)

    cnt1 = {"levels" : [[4, 5], range(6, 14, 2), [16, 20, 25, 30]],
            "spacings" : [5, 5, 5]}
    cnt2 = {"levels" : [[5], range(6, 9, 2), range(12, 17, 2), range(20, 31, 5)],
            "spacings" : [-10, -10, -20, -20]}
    cnt3 = {"levels" : [[5], range(6, 9, 2), range(12, 17, 2), range(20, 31, 5)],
            "spacings": [--5, -10, -20, -20]}
    contours = [cnt1, cnt2, cnt3]
    fig, axes, twinaxes, cbaxes = figure232426(fig, axes, data, contours, plot="ofwhm",
                                               sharedcb=True, cbtitle="Observed FWHM (arcsec)",
                                               twax=True)

    twinaxes[1].set_ylabel("Defocus FWHM (arcsec)")
    axes[1].set_ylabel("Height (km)")
    axes[2].set_xlabel("Seeing FWHM (arcsec)")

    axes[0].get_xaxis().set_visible(False)
    axes[1].get_xaxis().set_visible(False)

    return fig, axes


def figure26():
    fig, axes = plt.subplots(2, 1, figsize=(12, 24))

    heights = np.arange(40, 450, 10)
    seeings = np.arange(0.01, 5, 0.103)

    # if the premade data products are missing we need to recreate them.
    # The dictionary associated with file-name sets param_space_sampler
    # arguments to values used in the paper.
    datafiles = (("sdss_point_data.npy",
                  {"source" : profiles.PointSource, "instrument" : profiles.SDSS}),
                 ("lsst_point_data.npy",
                  {"source" : profiles.PointSource, "instrument" : profiles.LSST}))
    data = get_or_create_data(datafiles, heights=heights, seeings=seeings)

    cnt1 = {"levels" : [[5,15,25,35]],
            "spacings" : [5]}
    cnt2 = {"levels" : [[5,15,25,35], [40,42,44,49]],
            "spacings" : [5, 1]}

    contours = [cnt1, cnt2]
    fig, axes, twinaxes, cbaxes = figure232426(fig, axes, data, contours, plot="depth",
                                               sharedcb=False, cbtitle="Intensity loss (\% of max value)",
                                               twax=True)

    for ax, twax in zip(axes, twinaxes):
        ax.set_xlabel("Seeing FWHM (arcsec)")
        ax.set_ylabel("Distance (km)")
        twax.set_ylabel("Defocus FWHM (arcsec)")

    return fig, axes








def figure25():
    fig, axes = plt.subplots(2, 1, figsize=(12, 24))

    # this plot is compiled from two different sources of seeing and radii
    # which does have to be stated manually
    heights = np.arange(55, 305, 5)
    radii = np.arange(0.01, 4.1, 0.05)
    datafiles = (("sdss_radii_data.npy",
                  {"source" : profiles.DiskSource, "seeing" : profiles.SDSSSEEING,
                   "instrument" : profiles.SDSS}), )
    dat1 = get_or_create_data(datafiles, heights=heights, radii=radii)
    heights = np.arange(55, 305, 5)
    radii = np.arange(0.01, 8.2, 0.103)
    datafiles = (("lsst_radii_data.npy",
                  {"source" : profiles.DiskSource, "seeing" : profiles.LSSTSEEING,
                   "instrument" : profiles.LSST}), )
    dat2 = get_or_create_data(datafiles, heights=heights, radii=radii)
    data = [dat1[0], dat2[0]]

    cnt1 = {"levels" : [[2, 3, 4, 5, 6, 7, 8, 10]],
            "spacings" : [5]}
    cnt2 = {"levels" : [[6, 7, 8, 10, 12], [ 14, 18, 24]],
            "spacings" : [5, 1]}

    contours = [cnt1, cnt2]
    fig, axes, twinaxes, cbaxes = figure232426(fig, axes, data, contours, plot="ofwhm",
                                               sharedcb=False, cbtitle="Observed FWHM (arcsec)")

    for ax, twax in zip(axes, twinaxes):
        ax.set_xlabel("Radius (m)")
        ax.set_ylabel("Distance (km)")

    return fig, axes



def figure27():
    fig, axes = plt.subplots(2, 1, figsize=(12, 24))

    # this plot is compiled from two different sources of seeing and radii
    # which does have to be stated manually
    heights = np.arange(55, 305, 5)
    radii = np.arange(0.01, 4.1, 0.05)
    datafiles = (("sdss_radii_data.npy",
                  {"source" : profiles.DiskSource, "seeing" : profiles.SDSSSEEING,
                   "instrument" : profiles.SDSS}), )
    dat1 = get_or_create_data(datafiles, heights=heights, radii=radii)
    heights = np.arange(55, 305, 5)
    radii = np.arange(0.01, 8.2, 0.103)
    datafiles = (("lsst_radii_data.npy",
                  {"source" : profiles.DiskSource, "seeing" : profiles.LSSTSEEING,
                   "instrument" : profiles.LSST}), )
    dat2 = get_or_create_data(datafiles, heights=heights, radii=radii)
    data = [dat1[0], dat2[0]]

    cnt1 = {"levels" : [[1, 5, 10, 15, 18, 20, 23]],
            "spacings" : [5]}
    cnt2 = {"levels" : [[1], range(5, 50, 5)],
            "spacings" : [5, 1]}

    contours = [cnt1, cnt2]
    fig, axes, twinaxes, cbaxes = figure232426(fig, axes, data, contours, plot="depth", xlims=[(0.02, 1.8)], ylims=[(60, 181)],
                                               sharedcb=False, cbtitle="Intensity loss (\% of max value)")

    for ax, twax in zip(axes, twinaxes):
        ax.set_xlabel("Radius (m)")
        ax.set_ylabel("Distance (km)")

    return fig, axes
