"""
__author__ = 'linlei'
__project__:utils
__time__:2022/6/22 15:36
__email__:"919711601@qq.com"
"""
import segyio
import numpy as np


def read_segy(filepath):
    """
    This is a function that converts segy files into python arrays.
    Args:
        filepath: segy file path of input

    Returns:
        nd array:[inline,crossline,sample]
    """
    with segyio.open(filepath, strict=False) as f:
        inlines_dim = len(f.ilines)
        crosslines_dim = len(f.xlines)
        timeslice_dim = len(f.samples)
        dim = (inlines_dim, crosslines_dim, timeslice_dim)
        data = f.trace.raw[:].reshape(dim)
    return np.array(data)


def maxmin_normal(data):
    """
    This is a function that performs 0,1 normalization
    Args:
        data: np array

    Returns:
        d_out: np array after normalization
    """
    d_min = np.min(data)
    d_max = np.max(data)
    d_out = (data - d_min) / (d_max - d_min)
    return d_out


def save_h5(data,path):
    """
    Save the np array as a .h5 file
    Args:
        data: np array
        path: .h5 path of save

    Returns:
        None
    """
    f = h5py.File(path,"w")
    f.create_dataset("/data",data = data)
    f.close()


def read_h5(path):
    """
    Read .h5 file as np array
    Args:
        path: .h5 path of read

    Returns:
        np array
    """
    f = h5py.File(path,"r")
    data = f["/data"]
    return np.array(data)
