import datasketching.cms as cms
import heapq

MAX_OVERHEAD = 10

class TopK(object):

    def __init__(self, k, width, hashes):
        self.width = width
        self.hashes = hashes
        self.cms = cms.CMS(width, hashes)
        self.k = k
        self.queue = []
        self.seen = set()

    def insert(self, obj):
        """ Inserts _obj_ in this summary and updates the top k elements if this
            element is likely to be in the top k elements as given by the underlying top-k sketch """

        # Identify how many times you've seen `obj` already
        self.cms.insert(obj)
        count = self.cms.lookup(obj)

        # Insert _obj_ into the priority queue (`self.queue`).

        # Hint #1:  How would you sort the priority queue to ensure that it contains the top k elements?
        # Hint #2:  Python's `heapq.heappush` function puts the smallest things first
        # Hint #3:  What happens when you need to update the count of something that's already in the queue?

        # By storing a tuple with the negated count as the first element, we can keep the smallest things first
        to_insert = (-count, obj)

        if obj in self.seen:
            item, = [x for x in self.queue if x[1] == obj]
            self.queue.remove(item)
        else:
            self.seen.add(obj)

        heapq.heappush(self.queue, to_insert)

        # Hint #4:  How will you ensure that the priority queue doesn't grow unbounded?
        if len(self.queue) > (self.k * MAX_OVERHEAD):
            newsize = max(int(self.k * MAX_OVERHEAD / 2), 1)
            self.queue = heapq.nsmallest(newsize, self.queue)
            self.seen = set([v for _, v in self.queue])


    def topk(self):
        """ Returns a list of 2-tuples (value, count) for the top k elements in this structure """
        return [(value, -count) for count, value in heapq.nsmallest(self.k, self.queue)]


    def merge(self, other):
        result = TopK(self.width, self.hashes)
        result.cms.merge_from(self.cms)
        result.cms.merge_from(other.cms)
        newsize = max(int(self.k * MAX_OVERHEAD / 2), 1)
        result.queue = heapq.nsmallest(newsize, heaqp.merge(self.queue, other.queue))
        result.seen = set([v for _, v in result.queue])
        result.k = self.k
        return result