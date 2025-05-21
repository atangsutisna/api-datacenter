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
REPOSITORY_PATH = os.getenv('REPOSITORY_PATH')
USER_REPOSITORY_PATH = os.getenv('USER_REPOSITORY_PATH')



def verify_phone_number(telegram_id: str, phone: str) -> bool:
    logger.info("attempting to load all users from origin")
    with open(USER_REPOSITORY_PATH, 'r', encoding='utf-8') as file:
        origin_users = json.load(file)

    logger.info("attempting to load mapping-users")
    with open('mappinguser.json', 'r', encoding='utf-8') as file:
        phone_to_users = json.load(file)

    # if phone.startswith("0"):
    #     phone = "62" + phone[:1]
    
    logger.info("attempting to find user with phone %s", phone)
    filtered_phone_to_users = [
        item for item in phone_to_users if item.get('phoneNumber') == phone
    ]

    if filtered_phone_to_users:
        logger.info("found user with phone %s", phone)
        target_accounts = filtered_phone_to_users[0]['accounts']
        filtered_accounts = {
            key: value for key, value in origin_users.items()
            if value.get("username") in target_accounts
        }

        accounts = []
        for user_id, user_data in filtered_accounts.items():
            account = {
                "username": user_data["username"],
                "fullname": user_data["name"],
                "homedir": user_data["homedir"],
                "parentdir": REPOSITORY_PATH + user_data["homedir"],
                "permissions": user_data["permissions"],
            }
            logger.info("attempting to add user id %s to accounts", user_id)
            accounts.append(account)
        # print(json.dumps(accounts, indent=2))
        new_user = {
            "telegram_id": telegram_id,
            "fullname": accounts[0]['fullname'],
            "accounts": accounts,
            "phone": phone
        }
        # print(json.dumps(new_user, indent=2))
        try:
            with open('db.json', 'r') as f:
                db_data = json.load(f)
                if not isinstance(db_data, list):
                    db_data = []
        except (FileNotFoundError, json.JSONDecodeError):
            db_data = []
        
        db_data.append(new_user)
        # save to db
        logger.info("attempting to save a new user %r", new_user)
        with open("db.json", "w") as f:
            json.dump(db_data, f)
        
        return True
    else:
        logger.info("user with phone %s not found", phone)
        return False

# verify_phone_number("12345678", "6283821230266")