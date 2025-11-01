import hashlib, os
from userloggedin import get_user_logged_in
import logging, json,random
from dotenv import load_dotenv
import requests
import zipfile
import time
import uuid
import math
from spire.xls import *
from spire.xls.common import *
from pathlib import Path
import shutil

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



# def upload_once(file_path):
#     url = "https://file.io"
#     with open(file_path, "rb") as f:
#         response = requests.post(url, files={"file": f})
#     print("Status:", response.status_code)
#     print("Response text:", response.text)
#     return response.json()["link"]

# link = upload_once("/home/kangatang/git/filegator/repository/samplepptx.pptx")
# print("One-time download link:", link)

# contoh penggunaan
# link = upload_to_filebin("/home/kangatang/git/filegator/repository/dummy.pdf")
# print("Link download:", link)
def upload_to_filebin(filepath: str):
    file_name = os.path.basename(filepath)
    bin_name = f"{uuid.uuid4().hex}"
    url = "https://filebin.net/"+ bin_name + "/" + file_name

    with open(filepath, "rb") as f:
        files = {"file": f}
        response = requests.post(url, files=files)
    
    if response.ok:
        logger.info("Upload sukses: %s", response.url)
        return response.url
    else:
        logger.info("Gagal upload: %s : %s", response.status_code, response.text)
        return None

# contoh penggunaan
# long_url = "https://filebin.net/xyz123/samplepptx.pptx"
# short_url = shorten_url(long_url)
# print("Short URL:", short_url)
def shorten_url(url: str) -> str:
    api_url = "https://tinyurl.com/api-create.php"
    response = requests.get(api_url, params={"url": url})
    if response.ok:
        return response.text
    else:
        raise Exception("Gagal memendekkan URL")

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

def to_be_list(slot_value: str):
    text = slot_value.replace("dan", ",").replace("atau", ",")
    return [v.strip() for v in text.split(",") if v.strip().isdigit()]
    # return {"file_no_to_be_removed": values}

# slot_value = ["1,2,3"]
# for val in slot_value:
#     print(to_be_list(val))
def compress_folder(folder_path):
    folder_name = os.path.basename(os.path.normpath(folder_path))
    parent_dir = os.path.dirname(os.path.normpath(folder_path))
    output_path = os.path.join(parent_dir, f"{folder_name}.zip")
    # Membuat file zip
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                # Simpan dengan path relatif agar struktur folder tetap
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)
    print(f"Folder '{folder_path}' berhasil dikompres menjadi '{output_path}'")
    # end_time = time.time()
    return output_path

def compress_file(file_path):
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    parent_dir = os.path.dirname(os.path.normpath(file_path))
    output_path = os.path.join(parent_dir, f"{file_name}.zip")

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(file_path, os.path.basename(file_path))
    print(f"File '{file_path}' berhasil dikompres menjadi '{output_path}'")
    return output_path

def estimate_time(total_size, speed_mb_per_s=50):
    # hitung estimasi (detik)
    return total_size / (speed_mb_per_s * 1024 * 1024)


# Contoh penggunaan:
# Kompres folder
# compress_folder("/home/kangatang/git/filegator/repository/spark/sepeda/")
# Kompres file
# compress_file("/home/kangatang/git/filegator/repository/spark/Paparan_Audiensi_Ombudsman.pptx")

# total_size = get_folder_size_bytes("/home/kangatang/git/filegator/repository/spark")
# est_time = estimate_time(total_size, speed_mb_per_s=50)

# print(f"Total ukuran file: {total_size / (1024*1024):.2f} MB")
# print(f"Estimasi waktu: {est_time:.2f} detik (dengan asumsi 50 MB/s)")

# # proses zip
# actual_time = compress_folder("/home/kangatang/git/filegator/repository/spark")
# print(f"Proses zip selesai: ")
# print(f"Waktu aktual: {actual_time:.2f} detik")
import os

def get_folder_size_mb(folder_path):
    total_size = 0
    for dirpath, _, filenames in os.walk(folder_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.isfile(fp):
                total_size += os.path.getsize(fp)
    # ubah byte ke megabyte
    size_mb = total_size / (1024 * 1024)
    return size_mb

def is_folder_less_than_1gb(folder_path):
    size_in_bytes = get_folder_size_bytes(folder_path)
    one_gb_in_bytes = 1024 * 1024 * 1024
    return size_in_bytes < one_gb_in_bytes

def is_folder_less_than_2mb(folder_path):
    size_in_bytes = get_folder_size_bytes(folder_path)
    two_mb_in_bytes = 2 * 1024 * 1024  # 2 MB = 2 * 1024 * 1024 bytes
    return size_in_bytes < two_mb_in_bytes

def is_folder_larger_than_2mb(folder_path):
    size_in_bytes = get_folder_size_bytes(folder_path)
    two_mb_in_bytes = 2 * 1024 * 1024  # 2 MB dalam byte
    return size_in_bytes > two_mb_in_bytes

def is_file_smaller_than_100mb(file_path: str):
    size_in_bytes = get_file_size_bytes(file_path)
    hundred_mb_in_bytes = 100 * 1024 * 1024  # 100 MB dalam byte
    return size_in_bytes < hundred_mb_in_bytes

def format_time(seconds):
    """Ubah detik menjadi format menit/detik agar mudah dibaca."""
    minutes = math.floor(seconds / 60)
    secs = math.ceil(seconds % 60)
    if minutes > 0:
        return f"{minutes} menit {secs} detik"
    else:
        return f"{secs} detik"
# Contoh penggunaan
# folder_path = "/home/kangatang/git/filegator/repository/atang/master-tabel.xlsx"
# if is_file_smaller_than_100mb(folder_path):
#     print("Ukuran folder kurang dari 100 MB.")
# else:
#     print("Ukuran folder sama dengan atau lebih dari 100 MB.")

def estimate_zip_time(folder_path, compression_speed_mb_per_sec=50):
    """Menghitung estimasi waktu zip berdasarkan ukuran folder."""
    total_size_bytes = get_folder_size_bytes(folder_path)
    total_size_mb = total_size_bytes / (1024 * 1024)
    
    # Hitung estimasi waktu dalam detik
    estimated_seconds = total_size_mb / compression_speed_mb_per_sec
    estimated_double = estimated_seconds * 2
    
    return format_time(estimated_double)

def estimate_upload_time(file_path, upload_speed_mbps=50):
    """
    Menghitung estimasi waktu upload file.
    
    :param file_path: path file yang akan diupload
    :param upload_speed_mbps: kecepatan upload dalam megabit per detik (Mbps)
    """
    if not os.path.isfile(file_path):
        return "File tidak ditemukan."
    
    file_size_bytes = os.path.getsize(file_path)
    
    # 1 byte = 8 bit, 1 Mbps = 1.000.000 bit per detik
    upload_speed_bps = upload_speed_mbps * 1_000_000
    estimated_seconds = (file_size_bytes * 8) / upload_speed_bps
    
    return f"Terima kasih sudah menunggu, saya sedang mempersiapkan file ZIP untuk diunduh. Mungkin perlu waktu sekitar {format_time(estimated_seconds)}"
    # return f"Proses ini mungkin memerlukan sekitar {format_time(estimated_seconds)}"

# folder_path = "/home/kangatang/git/filegator/repository/spark/jamrud.zip"
# print(estimate_upload_time(folder_path))

def get_ext(path: str) -> str:
    fullpath = Path(path)
    return fullpath.suffix.lstrip(".")

def move_item(source_path: str, destination_path: str) -> str:
    """
    Moves a file or a directory (folder) from the source to the destination.

    Args:
        source_path (str): The full path to the file or folder to be moved.
        destination_path (str): The full path to the destination directory or new path.

    Returns:
        str: A status message indicating success or failure.
    """
    # 1. Check if the source exists
    if not os.path.exists(source_path):
        return f"❌ Failure: Source `{source_path}` was not found."

    # 2. Perform the move operation using shutil.move
    try:
        # shutil.move will move the item from source_path to destination_path.
        shutil.move(source_path, destination_path)
        
        # 3. Determine the type of item moved for the confirmation message
        # We check the destination path to see if it's a directory (folder)
        item_type = "Folder" if os.path.isdir(destination_path) and os.path.basename(source_path) == os.path.basename(destination_path) else "File"
        
        return f"✅ Success: `{item_type}` `{os.path.basename(source_path)}` has been moved to `{destination_path}`."
        
    except shutil.Error as e:
        return f"⚠️ Warning: A moving error occurred: {e}"
    except Exception as e:
        return f"❌ Failure: An unexpected error occurred: {e}"