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

def get_file_size_bytes(file_path):
    return os.path.getsize(file_path)

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

def to_dict(lspaths: list[str]) -> dict[str, str]:
    return {str(no): path for no, path in enumerate(lspaths, 1)}

def format_lspaths(lspaths: list[str]) -> str:
    """
    Fungsi ini untuk menampilkan list_dir dalam format:
    1. Dir 1
    2. Dir 2
    3. Dir 3
    4. File 1
    5. File 2
    6. Dst
    """
    message: str = ""
    for no, path in enumerate(lspaths, 1):
        file = os.path.isfile(path)
        simple_path = simplified_path(path)
        size_func = get_file_size_bytes if os.path.isfile(path) else get_folder_size_bytes
        message += f"\n{no}. `{simple_path}` (`{format_size(size_func(path))}`)"
    return message.strip()

def build_response(opening_message: str, lspaths: list[str], ending_message):
    message = opening_message + "\n"
    formatted_lspaths = format_lspaths(lspaths)
    message += formatted_lspaths
    message += "\n" + ending_message
    return message

def get_root_path(fullpath: str) -> str:
    parent_dir = os.path.dirname(fullpath)
    return parent_dir

# path = "/home/kangatang/git/filegator/repository/spark"
# lspaths = list_dir(path)
# formatted_lspaths = format_lspaths(lspaths=lspaths)
# print(formatted_lspaths)
# print(to_dict(lspaths))
# print(lspaths)
# response = build_response(
#     opening_message="Ini daftarnya: ", 
#     ending_message="apakah ada yang bisa saya bantu lagi", 
#     lspaths=lspaths
# )
# print(response)
# print(get_root_path(path))