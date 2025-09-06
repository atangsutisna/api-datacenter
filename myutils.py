import hashlib, os
from userloggedin import get_user_logged_in
import logging, json,random
from dotenv import load_dotenv

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

load_dotenv()
DB_PATH = os.getenv('DB_PATH')

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
        message += f"\n{no}. `{simple_path}`"
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

def get_workspaces(telegram_id: str):
    curr_user = get_user_logged_in(telegram_id)
    accounts = curr_user['accounts']
    root_path = os.getenv('REPOSITORY_PATH')
    user_workspaces = []
    if len(accounts) > 1:
        for account in accounts:
            homedir = account['homedir'].lstrip("/")
            fullpath = os.path.join(root_path, homedir)
            user_workspaces.append(fullpath)
    else:
        dirname = accounts[0]['homedir'].lstrip("/")
        logger.info("attempting to list all data in %s", dirname)
        home_path = os.path.join(root_path, dirname)
        list_dir = os.listdir(home_path)
        for dir in list_dir:
            child_path = os.path.join(home_path, dir)
            user_workspaces.append(child_path)
    
    return user_workspaces

def format_mphone_number(nomor: str):
    if nomor.startswith("0"):
        return "62" + nomor[1:]
    return nomor

def is_phone_exist(phone: str, db_path: str):
    data = read_db(db_path)
    formatted_phone = format_mphone_number(phone)
    return any(item.get("phone") == formatted_phone for item in data)

def read_db(db_path: str):
    logger.info("attempting to load db_path %s", DB_PATH)
    try:
        with open(DB_PATH, 'r') as f:
            db_data = json.load(f)
            if not isinstance(db_data, list):
                db_data = []
    except (FileNotFoundError, json.JSONDecodeError):
        db_data = []
    return db_data

def simplified_path(original_path: str) -> str:
    folder_name = os.path.basename(original_path)
    repository_path = original_path.split("/repository", 1)[1]
    
    parent_path = os.path.dirname(repository_path)
    return os.path.join(parent_path, folder_name)

def get_ask_to_open_remove_or_download() -> str:
    additional_responses = [
        "Ada hal lain yang perlu saya bantu dengan data ini? Misalnya, Kamu ingin menghapus, mengunduh, atau membuka folder lain?",
        "Perlu bantuan lanjutan? Saya bisa bantu hapus, unduh, atau masuk ke folder lain.",
        "Apa lagi yang bisa saya lakukan untuk Kamu? Ada pilihan hapus, unduh, atau jelajahi folder.",
        "Apakah ada tindakan lain yang ingin Kamu lakukan? Misalnya, menghapus, mengunduh, atau membuka folder?",
        "Sudah selesai dengan ini, atau ada lagi yang bisa saya bantu? Mungkin menghapus, mengunduh, atau membuka folder lain?"
    ]
    return random.choice(additional_responses)
    
def get_range_list(dictionary):
    if not dictionary:
        return "No data"
    min_key = min(int(k) for k in dictionary.keys())
    max_key = max(int(k) for k in dictionary.keys())
    return f"{min_key}..{max_key}"

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