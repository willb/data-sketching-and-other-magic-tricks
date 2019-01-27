import numpy as np

class FT(object):
    """ 
    A Fenwick tree is analogous to a binary heap and provides an 
    efficient prefix sum for counts associated with particular 
    element indices 
    """
    
    @classmethod
    def lsb(self, i):
        return ((i) & (-i))
     
    def __init__(self, size):
        self.elements = None
        self.reset(size)
    
    def sum(self, i):
        result = 0
        i += 1
        while i > 0:
            result += self.elements[i]
            i -= FT.lsb(i)
        return result
    
    def inc_by(self, i, ct):
        i += 1
        while i < len(self.elements) - 1:
            self.elements[i] += ct
            i += FT.lsb(i)
    
    def reset(self, size=None):
        if self.elements is None \
        or (size is not None and size != self.size()):
            self.elements = np.zeros(size + 1)
        else:
            np.ndarray.fill(self.elements, 0.0)
    
    def size(self):
        return len(self.elements) - 1