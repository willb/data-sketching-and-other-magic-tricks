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
        if obj < (1 << 64):
            return obj.to_bytes(8, "big")
        else:
            bcount = (int(math.log(obj) / math.log(2)) + 1)
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

    def merge_in_place(self, other):
        """ merges other into self, modifying self """
        np.minimum(self.buckets, other.buckets, self.buckets)

    def dup(self):
        result = SimpleMinhash(len(self.seeds))
        np.minumum(result.buckets, self.buckets, result.buckets)
        return result


class SlowerMinhash(object):
    """ This is a very basic implementation of minhash for didactic use only """
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

    def merge_in_place(self, other):
        """ merges other into self, modifying self """
        np.minimum(self.buckets, other.buckets, self.buckets)

    def dup(self):
        result = SlowerMinhash(len(self.seeds))
        np.minimum(result.buckets, self.buckets, result.buckets)
        return result



class LSHMinhash(object):
    """ This is a basic implementation of minhash with locality-sensitive hashing """
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

    def merge_in_place(self, other):
        """ merges other into self, modifying self """
        np.minimum(self.buckets, other.buckets, self.buckets)

    def dup(self):
        result = LSHMinhash(self.rows, self.bands)
        np.minimum(result.buckets, self.buckets, result.buckets)
        return result

    def lsh_keys(self):
        return [mhash(as_bytes(k), seed=self.seeds[0]) for k in self.buckets.reshape((self.rows, self.bands))]


def combine_signatures(*others):
    if len(others) == 0:
        return SimpleMinhash(0)

    result = others[0].dup()

    for other in others[1:]:
        result.merge_in_place(other)

    return result


class MinhashCache(object):
    def __init__(self, proto=None):
        self.d = {}
        if proto is None:
            self.prototype = LSHMinhash(32, 8)
        else:
            self.prototype = proto

    def __getitem__(self, k):
        if k in self.d:
            return self.d[k]
        else:
            sm = self.prototype.dup()
            sm.add(k)
            self.d[k] = sm
            return sm


def generate_minhashes_for(grouped_df, key_col, value_col, prototype=None):
    import itertools
    c = MinhashCache(prototype)
    df = grouped_df.head(grouped_df.size().max())
    return [(k, combine_signatures(*[c[a[1]] for a in g])) for k, g in
    itertools.groupby(zip(df[key_col], df[value_col]), lambda x: x[0])]
