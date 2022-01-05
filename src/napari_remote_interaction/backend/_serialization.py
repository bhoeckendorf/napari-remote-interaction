import hashlib as _hashlib
import pickle as _pickle

import blosc as _blosc
import numpy as np


class PackedArray:

    def __init__(self, dtype, shape, buffer):
        self.dtype = dtype
        self.shape = shape
        self.buffer = buffer


def _pack_array(x: np.ndarray):
    return PackedArray(
        x.dtype,
        x.shape,
        _blosc.compress_ptr(
            x.__array_interface__["data"][0],
            x.size,
            x.dtype.itemsize,
            cname="zlib",
            clevel=4
        )
    )


def _unpack_array(x: PackedArray):
    y = np.empty(x.shape, dtype=x.dtype)
    _blosc.decompress_ptr(x.buffer, y.__array_interface__['data'][0])
    return y


def _pack_arrays(x, minsize=1024 ** 2 // 2):
    if not isinstance(x, (list, tuple)):
        return
    for i, v in enumerate(x):
        if isinstance(v, tuple):
            x[i] = list(v)
            _pack_arrays(x[i])
        elif isinstance(v, list):
            _pack_arrays(v)
        elif isinstance(v, np.ndarray) and (v.size * v.itemsize) >= minsize:
            x[i] = _pack_array(v)


def _unpack_arrays(x):
    if not isinstance(x, (list, tuple)):
        return
    for i, v in enumerate(x):
        if isinstance(v, list):
            _unpack_arrays(v)
        elif isinstance(v, PackedArray):
            x[i] = _unpack_array(v)


def _sign(x, key):
    return _hashlib.blake2b(x, key=key).digest() + x


def _verify(x, key):
    digest, x = x[:64], x[64:]
    if _hashlib.blake2b(x, key=key).digest() != digest:
        raise RuntimeError("Cryptographic verification failed.\n"
                           "Please check hostnames, ports and keys of napari and remote.")
    return x


def _serialize(x, key, maxsize=50 * 1024 ** 2):
    _pack_arrays(x)
    x = _pickle.dumps(x)
    parts = (x[i:i + maxsize] for i in range(0, len(x), maxsize))
    return [_sign(i, key) for i in parts]


def _deserialize(x, key):
    x = _pickle.loads(b"".join(_verify(i, key) for i in x))
    _unpack_arrays(x)
    return x
