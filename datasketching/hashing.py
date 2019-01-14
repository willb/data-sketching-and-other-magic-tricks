from hashlib import sha1
import pickle

def h_sha1(value):
    bvalue = type(value) == bytes and value or pickle.dumps(value)
    return sha1(bvalue).hexdigest()

def hashes_for(value):
    bvalue = type(value) == bytes and value or pickle.dumps(value)
    digest = sha1(bvalue).hexdigest()
    return [int(digest[s:s+7], 16) for s in [0,8,16,24]]

def h1(value):
    return int(h_sha1(value)[0:8], 16)

def h2(value):
    return int(h_sha1(value)[8:16], 16)

def h3(value):
    return int(h_sha1(value)[16:24], 16)

def hashes_for(count, stride):
    def hashes(value):
        bvalue = type(value) == bytes and value or pickle.dumps(value)
        digest = sha1(bvalue).hexdigest()
        return [int(digest[s:s+stride], 16) for s in [x * stride for x in range(count)]]
    return hashes

