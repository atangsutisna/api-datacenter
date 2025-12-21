import logging, os, re, requests, json
from telegram.ext import ConversationHandler
from telegram import Update
from telegram.ext import ContextTypes
import re
from telegram.ext import CommandHandler, MessageHandler, filters, ConversationHandler
from dotenv import load_dotenv
import bcrypt
from datetime import datetime, timedelta
from userloggedin import get_user_logged_in
from myutils import is_phone_exist, format_mphone_number, read_db, hash_pin

load_dotenv()
REPOSITORY_PATH = os.getenv('REPOSITORY_PATH')
USER_REPOSITORY_PATH = os.getenv('USER_REPOSITORY_PATH')
DB_PATH = os.getenv('DB_PATH')
EXPIRY_MINUTES = os.getenv('EXPIRY_MINUTES')
# DEFAULT_PIN = os.getenv('DEFAULT_PIN')

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

ASK_PHONE = range(1)

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # start reguser-command
    await update.message.reply_text('Masukkan nomor telepon')
    return ASK_PHONE

async def reset_pin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text.strip()
    # Validasi sederhana nomor HP
    logger.info("attempting to validate phone %s", phone)
    if not re.match(r"^\d{10,15}$", phone):
        await update.message.reply_text("Nomor HP tidak valid! Coba lagi.")
        await update.message.reply_text("Gunakan /batal untuk mengakhiri perintah.")
        return ASK_PHONE

    logger.info("attempting to check phone on %s", DB_PATH)
    if not is_phone_exist(phone, DB_PATH):
        await update.message.reply_text("No. Hp tidak dikenali! silahkan gunakan yang lain.")
        await update.message.reply_text("Gunakan /batal untuk mengakhiri perintah.")
        return ASK_PHONE

    updated = update_pin(phone, "8888")
    if updated:
        await update.message.reply_text(f"PIN untuk nomor {phone} sudah direset")
    else:
        await update.message.reply_text(f"PIN gagal direset. Hubungi admin.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Proses dibatalkan..")
    return ConversationHandler.END

def update_pin(phone, pin):
    phone = format_mphone_number(phone)
    users = read_db(DB_PATH)
    updated = False
    for user in users:
        logger.info("attempting to find user with phone %s", phone)
        if user.get("phone") == phone:
            user["auth_pin"] = hash_pin(pin)
            session_expiry = datetime.now() + timedelta(minutes=int(EXPIRY_MINUTES))
            user["session_expiry"] = session_expiry.isoformat()
            updated = True

    logger.info("attempting to update pin user with phone %s", phone)
    with open(DB_PATH, "w") as f:
        json.dump(users, f)

    return updated

conversation_handler = ConversationHandler(
    entry_points=[CommandHandler("resetpin", start_cmd)],
    states={
        ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, reset_pin)],
    },
    fallbacks=[CommandHandler("batal", cancel)],
)
