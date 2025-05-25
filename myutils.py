import hashlib, os

def hash_path(path):
    return hashlib.sha1(path.encode()).hexdigest()[:10]

def simplified_path(original_path: str) -> str:
    folder_name = os.path.basename(original_path)
    repository_path = original_path.split("/repository", 1)[1]
    
    parent_path = os.path.dirname(repository_path)
    return os.path.join(parent_path, folder_name)