"""This module contains various convolution functionality specifically suited
to work with provided convolutional objects.

"""
import numpy as np
from scipy import misc, signal, interpolate, stats
from lfd.analysis.profiles.convolutionobj import ConvolutionObject

__all__ = ["largest_common_scale", "convolve_seeing", "convolve_defocus",
           "convolve_seeing_defocus", "convolve"]

def largest_common_scale(*args):
    """Finds the new appropriate common scale between given objects such that
    the new boundaries start at the leftmost and end at the rightmost object
    and the step between two points is the smallest step value for all objects.

    It is very important that the scale of the two convolved functions is the
    same! F.e. convolving a functions with scale lengths of 1 arcsecond and 1
    degree is drastically different than convolving functions with the same
    scale length.

    Parameters
    ----------
    *args : list, tuple
      set of objects we wish to reduce to the largest common scale

    Example
    -------
    >>> newscale = largest_common_scale(obj1, obj2, obj3, ...)

    """
    left = min([obj.scaleleft for obj in args])
    right = max([obj.scaleright for obj in args])
    step = min([obj.step for obj in args])

    newscale = np.arange(1.1*left, 1.1*right, step)
    return newscale

def convolve_two(obj1, obj2, name="convolved"):
    """Rescales, normalizes and convolves two ConvolutionObjects.

    Parameters
    ----------
    obj1 : lfd.analysis.profile.ConvolutionObject
      first object to be convolved
    obj2 : lfd.analysis.profile.ConvolutionObject
      second object to be convolved
    name : str
      ConvolutionObjects can be assigned names, or will default to an
      appropriate name based on instantiation, which helps with tracking the
      current object status and with plotting.

    """
    newscale = largest_common_scale(obj1, obj1)

    obj1.rescale(newscale)
    obj2.rescale(newscale)
    obj1.norm()
    obj2.norm()

    conv = signal.fftconvolve(obj1.obj, obj2.obj)
    return ConvolutionObject.fromConvolution(conv, newscale, name)

def convolve_three(obj1, obj2, obj3, name="convolved"):
    """Rescales, normalizes and then convolves three ConvolutionObjects.

    Parameters
    ----------
    obj1 : lfd.analysis.profile.ConvolutionObject
      first object to be convolved, usually starting profile
    obj2 : lfd.analysis.profile.ConvolutionObject
      second object to be convolved, usually seeing
    obj3 : lfd.analysis.profile.ConvolutionObject
      second object to be convolved, usually defocusing effects
    name : str
      ConvolutionObjects can be assigned names, or will default to an
      appropriate name based on instantiation, which helps with tracking the
      current object status and with plotting.
    """
    newscale = largest_common_scale(obj1, obj2, obj3)

    obj1.rescale(newscale)
    obj2.rescale(newscale)
    obj3.rescale(newscale)

    obj1.norm()
    obj2.norm()
    obj3.norm()

    convs = signal.fftconvolve(obj1.obj, obj2.obj)
    convs = ConvolutionObject.fromConvolution(convs, newscale)
    convsd = signal.fftconvolve(convs.obj, obj3.obj)

    return ConvolutionObject.fromConvolution(convsd, newscale, name)


def convolve_seeing(obj, seeing, name="seeing-convolved"):
    """Rescales, normalizes and convolves object and seeing.

    Parameters
    ----------
    obj : lfd.analysis.profile.ConvolutionObject
      brightness profile of object to be convolved
    obj2 : lfd.analysis.profile.ConvolutionObject
      seeing profile that will be convolved with object
    name : str
      ConvolutionObjects can be assigned names, or will default to an
      appropriate name based on instantiation, which helps with tracking the
      current object status and with plotting.
    """
    return convolve_two(obj, seeing, name)

def convolve_defocus(obj, defocus, name="defocus-convolved"):
    """Rescales, normalizes and convolves object and defocus.

    Parameters
    ----------
    obj : lfd.analysis.profile.ConvolutionObject
      brightness profile of object to be convolved
    defocus : lfd.analysis.profile.ConvolutionObject
      defocus profile that will be convolved with object
    name : str
      ConvolutionObjects can be assigned names, or will default to an
      appropriate name based on instantiation, which helps with tracking the
      current object status and with plotting.

    """
    return convolve_two(obj, defocus, name)

def convolve_seeing_defocus(obj, seeing, defocus, name="seeing-defocus-convolved"):
    """Rescales, normalizes and then convolves object, seeing and defocus.

    Parameters
    ----------
    obj : lfd.analysis.profile.ConvolutionObject
      brightness profile of object to be convolved
    defocus : lfd.analysis.profile.ConvolutionObject
      defocus profile that will be convolved with object
    seeing : lfd.analysis.profile.ConvolutionObject
      seeing profile that will be convolved with the previous convolution
      result
    name : str
      ConvolutionObjects can be assigned names, or will default to an
      appropriate name based on instantiation, which helps with tracking the
      current object status and with plotting.

    """
    return convolve_three(obj, seeing, defocus, name)

def convolve(*args, name=None):
    """Rescales, normalizes and convolves the provided ConvolutionObjects.
    Functionality applied in convolve_seeing/defocus or convolve_seeing_defocus
    functions is used when two or three ConvolutionObjects are provided.
    Otherwise the convolution is performed recursively which can be slow.

    Parameters
    ----------
    *args : tuple, list
      set of objects that will be convolved
    name : str
      ConvolutionObjects can be assigned names, or will default to an
      appropriate name based on instantiation, which helps with tracking the
      current object status and with plotting. If left None will default to
      "convolved"

    Example
    -------
    >>> convolve(obj, seeing, defocus)

    """

    # with the changes on Jan 2018 this achieves 500x speedups over previous
    # recursive convolutions and 2x speedups over specified convolutions
    # as the scales increase speedup increases as previously map depended on N
    # elements. 
    if len(args) == 2:
        return convolve_two(*args, name=None)
    if len(args) == 3:
        return convolve_seeing_defocus(*args, name=None)

    newscale = largest_common_scale(*args)

    for obj in args:
        obj.rescale(newscale)
        obj.norm()

    def recursion(index=1, result=args[0]):
        if index == len(args):
            return result
        else:
            result = np.convolve(result.obj, args[index].obj)
            result = ConvolutionObject.fromConvolution(result, newscale, name)
            return recursion(index+1, result)

    return recursion()
