import logging, os, re, requests, json
from telegram.ext import ConversationHandler
from telegram import Update
from telegram.ext import ContextTypes
import re
from telegram.ext import CommandHandler, MessageHandler, filters, ConversationHandler
from dotenv import load_dotenv
from myutils import is_phone_exist

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
    removed = True
    if removed:
        await update.message.reply_text(
            f"✅ Sukses! Akun telah berhasil ditambahkan ke nomor Hp {phone_no}"
        )
    else:
        await update.message.reply_text(
            f"❌ Gagal! Tidak ada satupun akun yang ditambahkan ke nomor Hp {phone_no}"
        )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Proses dibatalkan.")
    return ConversationHandler.END

conversation_handler = ConversationHandler(
    entry_points=[CommandHandler("rmaccount", start_cmd)],
    states={
        ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_phone)],
        ASK_USERNAMES: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_usernames)],
    },
    fallbacks=[CommandHandler("batal", cancel)],
)