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
# load user logged in
def get_user_logged_in(telegram_id: str):
    logger.info("attempting to find user with telegram id %s on %s", telegram_id, DB_PATH)
    with open(DB_PATH, 'r', encoding='utf-8') as file:
        users_loggedin = json.load(file)
    user = None
    for user_data in users_loggedin:
        if user_data["telegram_id"] == telegram_id:
            logger.info("Got user with telegram id %s", telegram_id)
            user = user_data
            break
    return user