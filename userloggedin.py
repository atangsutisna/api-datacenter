from dotenv import load_dotenv
import os, logging, json
from pathlib import Path

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
# logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)
load_dotenv()
DB_PATH = os.getenv('DB_PATH')
USER_REPOSITORY_PATH = os.getenv('USER_REPOSITORY_PATH')
# load user logged in
def get_user_logged_in(telegram_id: str):
    logger.info("attempting to find user with telegram id %s on %s", telegram_id, DB_PATH)
    with open(DB_PATH, 'r', encoding='utf-8') as file:
        users_loggedin = json.load(file)
    user = None
    for user_data in users_loggedin:
        # logger.info("Got user data %r", user_data)
        if user_data["telegram_id"] == telegram_id:
            # logger.info("Got user with telegram id %s", telegram_id)
            user = user_data
            break
    
    logger.info("Got account %r", user)
    if user is None:
        logger.info("failed to find user with telegram id %s", telegram_id)
        return user
    # todo: update the permissions
    logger.info("attempting to reload all users")
    with open(USER_REPOSITORY_PATH, 'r', encoding='utf-8') as file:
        origin_users = json.load(file)

    # logger.info("Got origin accounts %r", origin_users)
    # fixme: check setiap account, apakah masih ada di database utama?
    # jika tidak ada, jangan ditampilkan
    for origin_user in origin_users.values():
        # logger.info("Origin user %r", origin_user)
        for account in user["accounts"]:
            # logger.info("attempting to check account %s compare to %s", account["username"], origin_user["username"])
            if account["username"] == origin_user["username"]:
                logger.info("attempting to update permission account %s from %s to be %s", account["username"], account["permissions"], origin_user["permissions"])
                account["permissions"] = origin_user["permissions"]
    
    current_user = filter_user_accounts(user, origin_users)
    logger.info("Got account after filter %r", user)
    return current_user
    # return user


def filter_user_accounts(user_object, accounts_object):
    """
    Menghapus item account dari user_object['accounts'] jika username akun
    tidak ditemukan di dalam properti username pada setiap item accounts_object.

    Args:
        user_object (dict): Objek user yang mengandung array 'accounts'.
        accounts_object (dict): Objek accounts yang berisi daftar akun valid.

    Returns:
        dict: Objek user yang sudah dimodifikasi.
    """
    # 1. Ekstrak semua username yang valid dari accounts_object
    # Kita mengambil nilai 'username' dari setiap item (yang merupakan nilai) dalam accounts_object.
    valid_usernames = set()
    for account_data in accounts_object.values():
        if 'username' in account_data:
            valid_usernames.add(account_data['username'])
            
    # print(f"Username yang valid ditemukan: {valid_usernames}")

    # 2. Filter akun user
    # Kita menggunakan list comprehension untuk membuat list baru
    # yang hanya menyertakan akun user yang username-nya ada di valid_usernames.
    
    original_count = len(user_object.get('accounts', []))
    
    filtered_accounts = [
        account
        for account in user_object.get('accounts', [])
        if account.get('username') in valid_usernames
    ]

    # 3. Ganti array accounts lama dengan yang sudah difilter
    user_object['accounts'] = filtered_accounts
    
    filtered_count = len(user_object.get('accounts', []))
    # print(f"Jumlah akun sebelum filter: {original_count}, setelah filter: {filtered_count}")

    return user_object


def check_username_by_homedir(target_homedir):
    """
    Mencari keberadaan username berdasarkan nilai 'homedir' di dalam objek accounts.

    Args:
        accounts_object (dict): Objek accounts yang berisi daftar akun.
        target_homedir (str): Nilai homedir yang ingin dicari (misalnya, '/atang').

    Returns:
        bool: True jika homedir ditemukan, False jika tidak.
    """
    # accounts_object = 
    target_path = Path(target_homedir)
    # root_absolute = target_path.root
    logger.info("attempting to find username by homedir %s", target_homedir)
    if len(target_path.parts) > 2:
        target_homedir = os.sep + target_path.parts[1] + os.sep + target_path.parts[2]
        logger.info("Extracting the root path %s", target_homedir)

    
    with open(USER_REPOSITORY_PATH, 'r', encoding='utf-8') as file:
        accounts_object = json.load(file)
    # Iterasi melalui semua nilai (objek akun) di dalam accounts_object
    for account_data in accounts_object.values():
        # Pastikan kunci 'homedir' ada, meskipun seharusnya selalu ada berdasarkan data Anda
        if 'homedir' in account_data:
            # Cek apakah homedir akun saat ini cocok dengan homedir yang dicari
            if account_data['homedir'] == target_homedir:
                # Jika ditemukan, langsung kembalikan True dan hentikan fungsi
                logger.info(f"Ditemukan! Username terkait: {account_data.get('username', 'N/A')}")
                return True
                
    # Jika loop selesai tanpa mengembalikan True, berarti tidak ada yang cocok
    return False

# telegram_id = "7272740693"
# current_user = get_user_logged_in(telegram_id)
# print(json.dumps(current_user))
# print(check_username_by_homedir("/atang"))

# target_path = Path("/sdd/tes2/cangkilung")
# if len(target_path.parts) > 2:
#     target_homedir = os.sep + target_path.parts[1] + os.sep + target_path.parts[2]
# print(target_homedir)