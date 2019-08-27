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
        bvalue = type(v) == bytes and v or pickle.dumps(v)
        return mhash(bvalue, seed=seed)

    return m


class SimpleMinhash(object):
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
        result = SimpleMinhash(0)
        result.buckets = np.minimum(self.buckets, other.buckets)
        result.hashes = self.hashes
        return result
