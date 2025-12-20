import logging, os, re, requests, json
from telegram.ext import ConversationHandler
from telegram import Update
from telegram.ext import ContextTypes
import re
from telegram.ext import CommandHandler, MessageHandler, filters, ConversationHandler
from dotenv import load_dotenv
import bcrypt
from datetime import datetime, timedelta

load_dotenv()
REPOSITORY_PATH = os.getenv('REPOSITORY_PATH')
USER_REPOSITORY_PATH = os.getenv('USER_REPOSITORY_PATH')
DB_PATH = os.getenv('DB_PATH')
EXPIRY_MINUTES = os.getenv('EXPIRY_MINUTES')

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

ASK_PIN = range(1)

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # start reguser-command
    await update.message.reply_text('Masukkan PIN 4 angka. Tanpa huruf atau simbol.')
    return ASK_PIN

async def set_pin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pin = update.message.text.strip()
    # Validasi sederhana nomor HP
    logger.info("attempting to validate PIN %s", pin)
    if len(pin) == 4 and pin.isdigit():
        logger.info("attempting to save pin to db1")
        telegram_id = str(update.effective_user.id)
        update_pin(telegram_id, pin)
        
        await update.message.reply_text("PIN berhasil diperbarui. Keamanan akun Anda kini telah aktif menggunakan PIN baru Anda")
        return ConversationHandler.END

    await update.message.reply_text("Format salah. PIN hanya boleh terdiri dari angka (0-9)")
    return ASK_PIN

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Proses dibatalkan..")
    return ConversationHandler.END

def update_pin(telegram_id, pin):
    users = read_db(DB_PATH)
    updated = False
    for user in users:
        if user.get("telegram_id") == telegram_id:
            user["auth_pin"] = hash_pin(pin)
            session_expiry = datetime.now() + timedelta(minutes=int(EXPIRY_MINUTES))
            user["session_expiry"] = session_expiry.isoformat()
            updated = True

    logger.info("attempting to update pin user with telegram id %s", telegram_id)
    with open(DB_PATH, "w") as f:
        json.dump(users, f)

    return updated

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

def hash_pin(pin):
    # Mengubah string PIN menjadi bytes
    pin_bytes = pin.encode('utf-8')
    # Membuat 'salt' (garam) otomatis untuk menambah keamanan
    salt = bcrypt.gensalt()
    # Melakukan hashing
    hash_bytes = bcrypt.hashpw(pin_bytes, salt)
    hash_string = hash_bytes.decode('utf-8')
    return hash_string

def has_expired(expiry_string):
    """
    Mengembalikan True jika login sudah expired, False jika masih berlaku
    """
    if not expiry_string:
        return True
    # Ubah kembali string dari JSON menjadi objek datetime
    expiry_time = datetime.fromisoformat(expiry_string)
    # Jika waktu sekarang sudah melewati waktu expiry
    if datetime.now() > expiry_time:
        return True  # Sudah Expired
    else:
        return False # Masih Valid

conversation_handler = ConversationHandler(
    entry_points=[CommandHandler("setpin", start_cmd)],
    states={
        ASK_PIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_pin)],
    },
    fallbacks=[CommandHandler("batal", cancel)],
)

# print(update_pin("7272740693", "1234"))
# print(hash_pin("1234"))
# cara membaca auth pin
# input_user = "1234"
# hash_dari_file = "$2b$12$uBrRK4Ih8MJLD4ebCvJVAOm/ApLP0gE7cUK6PhHTigGhrY1OA4HyG"
# if bcrypt.checkpw(input_user.encode('utf-8'), hash_dari_file.encode('utf-8')):
#     print("PIN Cocok!")
# else:
#     print("PIN Salah!")
# session_expiry="2025-12-20T09:52:31.232300"
# print(has_expired(session_expiry))
