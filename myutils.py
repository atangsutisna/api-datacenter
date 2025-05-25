import hashlib

def hash_path(path):
    return hashlib.sha1(path.encode()).hexdigest()[:10]