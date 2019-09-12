from sklearn.utils.murmurhash import murmurhash3_bytes_u32 as mhash


import numpy as np
import random
import pickle


def murmurmaker(seed):
    """
    return a function to calculate a 32-bit murmurhash of v
    (an object or bytes), using the given seed
    """
    def m(v):
        bvalue = None

        if type(v) == str:
            bvalue = v.encode("utf-8")
        elif hasattr(v, "to_bytes"):
            bvalue = v.to_bytes(128, "big")
        elif type(v) == bytes:
            bvalue = v
        else:
            bvalue = pickle.dumps(v)

        return mhash(bvalue, seed=seed)

    return m



def as_bytes(obj):
    import math
    if type(obj) == str:
        return obj.encode("utf-8")
    elif type(obj) == int:
        if obj < (1 << 16):
            return obj.to_bytes(16, "big")
        elif obj < (1 << 32):
            return obj.to_bytes(32, "big")
        elif obj < (1 << 64):
            return obj.to_bytes(64, "big")
        elif obj < (1 << 128):
            return obj.to_bytes(128, "big")
        else:
            bcount = 2 ** (int(math.log(obj) / math.log(2)) + 1)
            return obj.to_bytes(bcount, "big")
    elif type(obj) == bytes:
        return obj

    return pickle.dumps(obj)

murmurize = np.frompyfunc(lambda seed, bytes: mhash(bytes, seed), 2, 1)

class SimpleMinhash(object):
    """ This is a slightly less-basic implementation of minhash """
    def __init__(self, hashes):
        rng = np.random.RandomState(seed=int.from_bytes(b"rad!", "big"))
        self.buckets = np.full(hashes, (1 << 32) - 1)
        self.seeds = rng.randint(0, (1 << 32) - 1, hashes)


    def add(self, obj):
        hashes = murmurize(self.seeds, as_bytes(obj))
        np.minimum(self.buckets, hashes.astype("int"), self.buckets)

    def similarity(self, other):
        """  """
        return np.count_nonzero(self.buckets == other.buckets) / float(len(self.buckets))

    def merge(self, other):
        """ returns a newly-allocated minhash structure containing
            the merge of this hash and another """
        result = SimpleMinhash(0)
        result.buckets = np.minimum(self.buckets, other.buckets)
        result.seeds = self.seeds
        return result


class SlowerMinhash(object):
    """ This is a very basic implementation of minhash """
    def __init__(self, hashes):
        rng = np.random.RandomState(seed=int.from_bytes(b"rad!", "big"))
        self.buckets = np.full(hashes, (1 << 32) - 1)
        self.hashes = [murmurmaker(seed) for seed in rng.randint(0, (1 << 32) - 1, hashes)]

    def add(self, obj):
        self.buckets = np.minimum(self.buckets, [h(obj) for h in self.hashes])

    def similarity(self, other):
        """  """
        return np.count_nonzero(self.buckets == other.buckets) / float(len(self.buckets))

    def merge(self, other):
        """ returns a newly-allocated minhash structure containing
            the merge of this hash and another """
        result = SlowerMinhash(0)
        result.buckets = np.minimum(self.buckets, other.buckets)
        result.hashes = self.hashes
        return result


class LSHMinhash(object):
    """ This is a very basic implementation of minhash with locality-sensitive hashing """
    def __init__(self, rows, bands):
        rng = np.random.RandomState(seed=int.from_bytes(b"rad!", "big"))
        hashes = rows * bands
        self.rows = rows
        self.bands = bands
        self.buckets = np.full(hashes, (1 << 32) - 1)
        self.seeds = rng.randint(0, (1 << 32) - 1, hashes)

    def add(self, obj):
        hashes = murmurize(self.seeds, as_bytes(obj))
        np.minimum(self.buckets, hashes.astype("int"), self.buckets)

    def similarity(self, other):
        """  """
        return np.count_nonzero(self.buckets==other.buckets) / float(len(self.buckets))

    def merge(self, other):
        """ returns a newly-allocated minhash structure containing
            the merge of this hash and another """
        result = LSHMinhash(self.rows, self.bands)
        numpy.minimum(self.buckets, other.buckets, result.buckets)
        result.seeds = self.seeds
        return result

    def lsh_keys(self):
        return [self.hashes[0]([b for b in band]) for band in self.buckets.copy().reshape((self.rows, self.bands))]
