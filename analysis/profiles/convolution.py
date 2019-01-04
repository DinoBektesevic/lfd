import numpy as np
from scipy import misc, signal, interpolate, stats


def largest_common_scale(*args):
    """Finds the new appropriate common scale between given objects such that
    the new boundaries start at the leftmost and end at the rightmost object
    and the step between two points is the smallest step value for all objects.

    It is very important that the scale of the two convolved functions is the
    same! F.e. convolving a functions with scale lengths of 1 arcsecond and 1
    degree is drastically different than convolving functions with the same
    scale length.
    """
    left = min([obj.scaleleft for obj in args])
    right = max([obj.scaleright for obj in args])
    step = min([obj.step for obj in args])

    newscale = np.arange(1.1*left, 1.1*right, step)
    return newscale

def convolve_seeing(obj, seeing):
    """Rescales, normalizes and convolves object and seeing."""
    newscale = largest_common_scale(obj, seeing)

    obj.rescale(newscale)
    seeing.rescale(newscale)
    obj.norm()
    seeing.norm()

    conv = signal.fftconvolve(obj.obj, seeing.obj)
    return ConvolutionObject.fromConvolution(conv, newscale)

def convolve_defocus(obj, defocus):
    """Rescales, normalizes and convolves object and defocus."""
    newscale = largest_common_scale(obj, defocus)

    obj.rescale(newscale)
    defocus.rescale(newscale)
    obj.norm()
    defocus.norm()

    conv = signal.fftconvolve(obj.obj, defocus.obj)
    return ConvolutionObject.fromConvolution(conv, newscale)

def convolve_seeing_defocus(obj, seeing, defocus):
    """Rescales, normalizes and then convolves object, seeing and then defocus."""
    newscale = largest_common_scale(obj, seeing, defocus)

    obj.rescale(newscale)
    seeing.rescale(newscale)
    defocus.rescale(newscale)
    obj.norm()
    seeing.norm()
    defocus.norm()

    convs = signal.fftconvolve(obj.obj, seeing.obj)
    convs = ConvolutionObject.fromConvolution(convs, newscale)
    convsd = signal.fftconvolve(convs.obj, defocus.obj)

    return ConvolutionObject.fromConvolution(convsd, newscale)


def convolve(*args):
    """Rescales and renormalizes given ConvolutionObjects and then recursively
    convolves them in the given order.
    """
    newscale = largest_common_scale(*args)

    for obj in args:
        obj.rescale(newscale)
        obj.norm()

    def recursion(index=1, result=args[0]):
        if index == len(args):
            return result
        else:
            result = np.convolve(result.obj, args[index].obj)
            result = ConvolutionObject.fromConvolution(result, newscale)
            return recursion(index+1, result)

    return recursion()
