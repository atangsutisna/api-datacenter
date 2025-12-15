from dotenv import load_dotenv
import os, logging, json

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
            
    return user
# telegram_id = "926678467"
# get_user_logged_in(telegram_id)