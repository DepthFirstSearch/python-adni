from __future__ import division
import numbers
from warnings import warn
import fnmatch
import os
import numpy as np
from numpy.lib.stride_tricks import as_strided
import nibabel as nib
from scipy.io import loadmat


# Change both paths
directory = '/home/mhubrich/ADNI_intnorm_avgpool333'
brainIndex = loadmat('/home/mhubrich/brainIndex')['brainIndex']


def view_as_blocks(arr_in, block_shape):
    if not isinstance(block_shape, tuple):
        raise TypeError('block needs to be a tuple')
    block_shape = np.array(block_shape)
    if (block_shape <= 0).any():
        raise ValueError("'block_shape' elements must be strictly positive")
    if block_shape.size != arr_in.ndim:
        raise ValueError("'block_shape' must have the same length "
                         "as 'arr_in.shape'")
    arr_shape = np.array(arr_in.shape)
    if (arr_shape % block_shape).sum() != 0:
        raise ValueError("'block_shape' is not compatible with 'arr_in'")
    # -- restride the array to build the block view
    if not arr_in.flags.contiguous:
        warn(RuntimeWarning("Cannot provide views on a non-contiguous input "
                            "array without copying."))
    arr_in = np.ascontiguousarray(arr_in)
    new_shape = tuple(arr_shape // block_shape) + tuple(block_shape)
    new_strides = tuple(arr_in.strides * block_shape) + arr_in.strides
    arr_out = as_strided(arr_in, shape=new_shape, strides=new_strides)
    return arr_out



def block_reduce(image, block_size, func=np.sum, cval=0):
    if len(block_size) != image.ndim:
        raise ValueError("`block_size` must have the same length "
                         "as `image.shape`.")
    pad_width = []
    for i in range(len(block_size)):
        if block_size[i] < 1:
            raise ValueError("Down-sampling factors must be >= 1. Use "
                             "`skimage.transform.resize` to up-sample an "
                             "image.")
        if image.shape[i] % block_size[i] != 0:
            after_width = block_size[i] - (image.shape[i] % block_size[i])
        else:
            after_width = 0
        pad_width.append((0, after_width))
    image = np.pad(image, pad_width=pad_width, mode='constant',
                   constant_values=cval)
    out = view_as_blocks(image, block_size)
    for i in range(len(out.shape) // 2):
        out = func(out, axis=-1)
    return out


# brain[x,y,z] == 1 iif (x,y,z) brain voxel
brain = np.zeros((91, 109, 91), dtype=np.float32)
for i in range(brainIndex.shape[0]):
        x = brainIndex[i, 0] - 1
        y = brainIndex[i, 1] - 1
        z = brainIndex[i, 2] - 1
        brain[x,y,z] = 1.0


files = []
for root, dirnames, filenames in os.walk(directory):
    for filename in fnmatch.filter(filenames, '*.nii'):
        files.append(os.path.join(root, filename))


for f in files:
    # Load scan
    scan = nib.load(f).get_data()
    # Remove non-brain voxels
    scan *= brain
    # Delete non-brain slices (new dims: 88x108x88)
    scan = np.delete(scan, [0, 89, 90], 0)
    scan = np.delete(scan, [0], 1)
    scan = np.delete(scan, [88, 89, 90], 2)
    # Bring to size 88x88x88
    scan = np.delete(scan, range(10), 1)
    scan = np.delete(scan, range(88, 98), 1)
    # Remove negative voxels
    scan[np.where(scan < 0)] = 0
    # Pool down by 3x3x3
    scan = block_reduce(scan, (3,3,3), func=np.mean, cval=0)
    # Save new .npy-file and delete old .nii-file
    np.save(os.path.splitext(f)[0] + '.npy', scan)
    os.remove(f)


