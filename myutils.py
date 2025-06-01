import hashlib, os

def hash_path(path):
    return hashlib.sha1(path.encode()).hexdigest()[:10]

def simplified_path(original_path: str) -> str:
    folder_name = os.path.basename(original_path)
    repository_path = original_path.split("/repository", 1)[1]
    
    parent_path = os.path.dirname(repository_path)
    return os.path.join(parent_path, folder_name)

def get_folder_size_bytes(folder_path):
    total_size = 0
    for dirpath, _, filenames in os.walk(folder_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.isfile(fp):
                total_size += os.path.getsize(fp)
    return total_size    

def format_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024**2:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024**3:
        return f"{size_bytes / 1024**2:.2f} MB"
    else:
        return f"{size_bytes / 1024**3:.2f} GB"

def list_dir(target_path: str) -> list[str]:
    """
    Fungsi ini untuk menampilkan daftar folder dan file.
    Nilai yang dikembalikan adalah daftar directory dan file. Disertai dengan 
    """
    ls_dir = os.listdir(target_path)
    ls_dir_fullpath = []
    if not ls_dir:
        return ls_dir_fullpath
    
    for dir in ls_dir:
        child_path = os.path.join(target_path, dir)
        ls_dir_fullpath.append(child_path)

    return ls_dir_fullpath

def format_lspaths(opening_message: str, lspaths: list[str]) -> str:
    """
    Fungsi ini untuk menampilkan list_dir dalam format:
    1. Dir 1
    2. Dir 2
    3. Dir 3
    4. File 1
    5. File 2
    6. Dst
    """
    no = 1
    message: str = ""
    message += opening_message + "\n"
    for path in lspaths:
        file = os.path.isfile(path)
        simple_path = simplified_path(path)
        if not file:
            message += f"\n{no}. `{simple_path}` (`{format_size(get_folder_size_bytes(path))}`)"
        else:
            message += f"\n{no}. `{simple_path}` (`{format_size(get_file_size_bytes(path))}`)"
        no += 1
    return message

path = "/home/kangatang/git/filegator/repository/spark"
lspaths = list_dir(path)
formatted_lspaths = format_lspaths(opening_message="Ini daftarnya:", lspaths=lspaths)
print(formatted_lspaths)