from reguser import add_user_to_db
import logging, os, re, requests,json
from telegram.ext import ConversationHandler
from telegram import Update
from telegram.ext import ContextTypes
import re
from telegram.ext import CommandHandler, MessageHandler, filters, ConversationHandler
from reguser import add_user_to_db
from myutils import read_db
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

ASK_PHONE, ASK_FULLNAME, ASK_USERNAMES = range(3)

def format_nomor_hp(nomor: str):
    if nomor.startswith("0"):
        return "62" + nomor[1:]
    return nomor

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # start reguser-command
    await update.message.reply_text('Silakan masukan nomor HP:')
    return ASK_PHONE

async def receive_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text.strip()
    # Validasi sederhana nomor HP
    if not re.match(r"^\d{10,15}$", phone):
        await update.message.reply_text("Nomor HP tidak valid. Coba lagi:")
        return ASK_PHONE

    context.user_data["phone"] = phone
    await update.message.reply_text("Masukan nama lengkap")
    return ASK_FULLNAME

async def receive_usernames(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username_input = update.message.text.strip()
    usernames = [u.strip() for u in username_input.split(",") if u.strip()]
    valid_unames = find_usernames()
    for uname in usernames:
        if uname not in valid_unames:
            await update.message.reply_text(
                f"username {uname} tidak dikenali, Mohon diperiksa kembali."
            )
            await update.message.reply_text(
                "Untuk membatalkan proses registrasi, klik atau ketik /batal"
            )
            return ASK_USERNAMES


    context.user_data["usernames"] = usernames
    # validate usernames
    # for username in usernames:
        # che
    phone_no = context.user_data['phone']
    fullname = context.user_data['fullname']
    new_user = {
        "phoneNumber": format_nomor_hp(phone_no),
        "accounts": usernames,
        "fullname": fullname
    }
    db_user = "mappinguser.json"
    add_user_to_db(db_user, new_user)

    # Kirim ringkasan data
    await update.message.reply_text(
        f"✅ Data berhasil diterima:\n📱 Nomor HP: {context.user_data['phone']}\n👤 Username: {', '.join(usernames)}"
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Proses dibatalkan.")
    return ConversationHandler.END

async def receive_fullname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    fullname = update.message.text.strip()
    context.user_data["fullname"] = fullname
    await update.message.reply_text("Masukan username yang bisa diakses (pisahkan dengan koma):")
    return ASK_USERNAMES

def find_usernames():
    with open(USER_REPOSITORY_PATH, 'r', encoding='utf-8') as file:
        accounts = json.load(file)
    ls_account = []
    for account in accounts.values():
        # logger.info("Got account %s", account)
        ls_account.append(account["username"])
    return ls_account

conversation_handler = ConversationHandler(
    entry_points=[CommandHandler("reguser", start_cmd)],
    states={
        ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_phone)],
        ASK_FULLNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_fullname)],
        ASK_USERNAMES: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_usernames)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

# accounts = find_usernames()
# if "atang" in accounts:
#     print("valid")
# else:
#     print("invalid")