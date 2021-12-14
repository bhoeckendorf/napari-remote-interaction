import hashlib as _hashlib
import pickle as _pickle

import blosc as _blosc


def _sign(x, key):
    return _hashlib.blake2b(x, key=key).digest() + x


def _verify(x, key):
    digest, x = x[:64], x[64:]
    if _hashlib.blake2b(x, key=key).digest() != digest:
        raise RuntimeError("Cryptographic verification failed.\n"
                           "Please check hostnames, ports and keys of napari and remote.")
    return x


def _serialize(x, key, maxsize=50 * 1024 ** 2):
    x = _pickle.dumps(x)
    parts = (x[i:i + maxsize] for i in range(0, len(x), maxsize))
    return [_sign(_blosc.compress(i), key) for i in parts]


def _deserialize(x, key):
    return _pickle.loads(b"".join(_blosc.decompress(_verify(i, key)) for i in x))
