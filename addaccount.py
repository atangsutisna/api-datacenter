import logging, os, re, requests, json
from telegram.ext import ConversationHandler
from telegram import Update
from telegram.ext import ContextTypes
import re
from telegram.ext import CommandHandler, MessageHandler, filters, ConversationHandler
from dotenv import load_dotenv

load_dotenv()
REPOSITORY_PATH = os.getenv('REPOSITORY_PATH')
USER_REPOSITORY_PATH = os.getenv('USER_REPOSITORY_PATH')
DB_PATH = os.getenv('DB_PATH')

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

ASK_PHONE, ASK_USERNAMES = range(2)

def format_nomor_hp(nomor: str):
    if nomor.startswith("0"):
        return "62" + nomor[1:]
    return nomor

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

def is_phone_exist(phone: str, db_path: str):
    data = read_db(db_path)
    formatted_phone = format_nomor_hp(phone)
    return any(item.get("phone") == formatted_phone for item in data)

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # start reguser-command
    await update.message.reply_text('Silakan masukan nomor HP:')
    return ASK_PHONE

async def receive_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text.strip()
    # Validasi sederhana nomor HP
    logger.info("attempting to validate phone %s", phone)
    if not re.match(r"^\d{10,15}$", phone):
        await update.message.reply_text("Nomor HP tidak valid. Coba lagi:")
        return ASK_PHONE

    # todo: di sini perlu dicek apakah nomor handphone sudah ada
    logger.info("attempting to load db_path %s", DB_PATH)
    if not is_phone_exist(phone, DB_PATH):
        await update.message.reply_text("No. Hp tidak dikenali. Silahkan masukan nomor lain")
        return ASK_PHONE

    logger.info("attempting to find phone with number %s", phone)
    context.user_data["phone"] = phone
    await update.message.reply_text("Masukan username (pisahkan dengan koma):")
    return ASK_USERNAMES

async def receive_usernames(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username_input = update.message.text.strip()
    usernames = [u.strip() for u in username_input.split(",") if u.strip()]
    
    context.user_data["usernames"] = usernames
    
    phone_no = context.user_data['phone']
    new_user = {
        "phoneNumber": format_nomor_hp(phone_no),
        "accounts": usernames
    }
    # db_user = ".json"
    # add_user_to_db(db_user, new_user)

    # Kirim ringkasan data
    # await update.message.reply_text(
    #     f"✅ Data berhasil diterima:\n📱 Nomor HP: {context.user_data['phone']}\n👤 Username: {', '.join(usernames)}"
    # )
    await update.message.reply_text(
        f"✅ Username berhasil ditambahkan"
    )

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Proses dibatalkan.")
    return ConversationHandler.END

def add_account(db_path: str, phone: str, usernames: []):
    logger.info("attempting to load all users from origin")
    with open(USER_REPOSITORY_PATH, 'r', encoding='utf-8') as file:
        origin_users = json.load(file)

    filtered_accounts = {
        key: value for key, value in origin_users.items()
        if value.get("username") in usernames
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

    logger.info("Got users from usernames : %r : %r", usernames, accounts)


conversation_handler = ConversationHandler(
    entry_points=[CommandHandler("addaccount", start_cmd)],
    states={
        ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_phone)],
        ASK_USERNAMES: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_usernames)],
    },
    fallbacks=[CommandHandler("batal", cancel)],
)

# print(is_phone_exist("0909090909090", DB_PATH))
add_account(DB_PATH, '083821230266', ['spark'])
# todo: 
# 1. map username to user and home dir
# 2. add username to account