import numpy

class BitVector(object):
    def __init__(self, size):
        self._size = size
        ct = size % 64 == 0 and (size / 64) or (size / 64 + 1)
        self._entries = numpy.zeros(int(ct), numpy.uint64)
    
    def __len__(self):
        return self._size
    
    def __getitem__(self, key):
        k = int(key)
        return (self._entries[int(k / 64)] & numpy.uint64(1 << (k % 64))) > 0
    
    def __setitem__(self, key, value):
        k = int(key)
        if value:
            update = numpy.uint64(1 << key % 64)
            self._entries[int(k / 64)] = self._entries[int(k / 64)] | update
        else:
            update = numpy.uint64(1 << key % 64)
            self._entries[int(k / 64)] = self._entries[int(k / 64)] ^ update
    
    def merge_from(self, other):
        numpy.bitwise_or(self._entries, other._entries, self._entries)
    
    def intersect_from(self, other):
        numpy.bitwise_and(self._entries, other._entries, self._entries)
    
    def dup(self):
        result = BitVector(self._size)
        result.merge_from(self)
        return result
    
    def intersect(self, other):
        result = BitVector(self._size)
        numpy.bitwise_and(self._entries, other._entries, result._entries)
        return result
    
    def union(self, other):
        result = BitVector(self._size)
        numpy.bitwise_or(self._entries, other._entries, result._entries)
        return result
    
    def count_set_bits(self):
        """ Count the number of bits set in this vector. 
            There are absolutely better ways to do this
            but this implementation is suitable for
            occasional use. """
        def set_bits(i):
            result = 0
            i = int(i)
            while i:
                result += (i & 1)
                i >>= 1
            return result
        return sum([set_bits(x) for x in self._entries])

