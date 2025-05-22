from userloggedin import get_user_logged_in
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()
REPOSITORY_PATH = os.getenv('REPOSITORY_PATH')

def is_child(parent, child):
    try:
        Path(child).resolve().relative_to(Path(parent).resolve())
        return True
    except ValueError:
        return False

def is_permitted(telegram_id: str, target_path: str, action: str) -> bool:
    current_user = get_user_logged_in(telegram_id)
    accounts = current_user['accounts']
    is_permitted = False
    for account in accounts:
        workspace = account['parentdir']
        if is_child(workspace, target_path):
            permissions = account['permissions']
            if action in permissions:
                is_permitted = True
                break
    
    return is_permitted
# upload_permitted = is_permitted("7272740693", "/home/kangatang/git/filegator/repository/atang/sorangan/", "upload")
# print(upload_permitted)
    