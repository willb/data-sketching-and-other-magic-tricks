import numpy as np


class CMS(object):
    def __init__(self, width, hashes):
        """ Initializes a Count-min sketch with the
            given width and a collection of hashes,
            which are functions taking arbitrary
            values and returning integers.  The depth
            of the sketch structure is taken from the
            number of supplied hash functions.

            hashes can be either a function taking
            a value and returning a list of results
            or a list of functions.  In the latter
            case, this constructor will synthesize
            the former """
        self.__width = width

        if hasattr(hashes, '__call__'):
            self.__hashes = hashes
            # inspect the tuple returned by the hash function to get a depth
            self.__depth = len(hashes(bytes()))
        else:
            funs = hashes[:]
            self.__depth = len(hashes)

            def h(value):
                return [int(f(value)) for f in funs]

            self.__hashes = h

        self.__buckets = np.zeros((int(width), int(self.__depth)), np.uint64)

    def width(self):
        return self.__width

    def depth(self):
        return self.__depth

    def insert(self, value):
        """ Inserts a value into this sketch """
        for (row, col) in enumerate(self.__hashes(value)):
            self.__buckets[col % self.__width][row] += 1

    def lookup(self, value):
        """ Returns a biased estimate of number of times value has been inserted in this sketch"""
        return min([self.__buckets[col % self.__width][row] for (row, col) in enumerate(self.__hashes(value))])

    def merge_from(self, other):
        """ Merges other in to this sketch by
            adding the counts from each bucket in other
            to the corresponding buckets in this

            Updates this. """
        self.__buckets += other.__buckets

    def merge(self, other):
        """ Creates a new sketch by merging this sketch's
            counts with those of another sketch. """

        cms = CMS(self.width(), self.__hashes)
        cms.__buckets += self.__buckets
        cms.__buckets += other.__buckets
        return cms

    def inner(self, other):
        """ returns the inner product of self and other, estimating
            the equijoin size between the streams modeled by
            self and other """
        r, = np.tensordot(self.__buckets, other.__buckets).flat
        return r

    def minimum(self, other):
        """ Creates a new sketch by taking the elementwise minimum
            of this sketch and another. """
        cms = CMS(self.width(), self.__hashes)
        np.minimum(self.__buckets, other.__buckets, cms.__buckets)
        return cms

    def dup(self):
        cms = CMS(self.width(), self.__hashes)
        cms.merge_from(self)
        return cms
