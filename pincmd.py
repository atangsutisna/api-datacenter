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
    await update.message.reply_text('Masukkan PIN')
    return ASK_PIN

async def check_pin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pin = update.message.text.strip()
    # Validasi sederhana nomor HP
    logger.info("attempting to validate PIN %s", pin)
    if len(pin) == 4 and pin.isdigit():
        logger.info("attempting to save pin to db1")
        telegram_id = str(update.effective_user.id)

        users = read_db(DB_PATH)
        found_user = False
        has_pin = False
        auth_pin = None
        for user in users:
            if user.get("telegram_id") == telegram_id:
                found_user = True
                if "auth_pin" in user:
                    has_pin = True
                    auth_pin = user["auth_pin"]

        if found_user:
            logger.info("found user with telegram id %s", telegram_id)
            if has_pin:
                logger.info("attempting to validate pin for telegram id %s", telegram_id)
                # hash_dari_file = "$2b$12$uBrRK4Ih8MJLD4ebCvJVAOm/ApLP0gE7cUK6PhHTigGhrY1OA4HyG"
                if bcrypt.checkpw(pin.encode('utf-8'), auth_pin.encode('utf-8')):
                    # update session_expiry
                    updated = update_session_expiry(telegram_id)
                    if (updated):
                        resp = go_home_cmd(update, "ke beranda")
                        await update.message.reply_text("Verifikasi berhasil. Silahkan utk memulai pembicaraan kembali dingan kembali ke beranda")
                        # await update.message.reply_text("*Pemberitahuan:* Sesi penanganan file telah berakhir karena reset sistem. Mohon akses kembali ke *Beranda* dan kirimkan instruksi Anda untuk memulihkan konteks dokumen")

                    else:
                        await update.message.reply_text("Gagal saat mengupdate session expiry. Silahkan hubungi admin")
                else:
                    await update.message.reply_text("PIN salah! Silahkan hubungi admin")
                    # return ASK_PIN
                    return ConversationHandler.END
            else:
                await update.message.reply_text("Anda belum mengatur PIN keamanan. Silakan buat PIN terlebih dahulu untuk meningkatkan keamanan akun Anda")
        else:
            await update.message.reply_text("Maaf, saya belum mengenal kamu")
        return ConversationHandler.END

    await update.message.reply_text("Format salah. PIN hanya boleh terdiri dari angka (0-9). Gunakan perintah /batal untuk membatalkan atau mengakhiri perintah.")
    return ASK_PIN

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Proses dibatalkan..")
    return ConversationHandler.END

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

def update_session_expiry(telegram_id):
    users = read_db(DB_PATH)
    updated = False
    for user in users:
        if user.get("telegram_id") == telegram_id:
            session_expiry = datetime.now() + timedelta(minutes=int(EXPIRY_MINUTES))
            user["session_expiry"] = session_expiry.isoformat()
            updated = True

    logger.info("attempting to update session expiry for telegram id %s", telegram_id)
    with open(DB_PATH, "w") as f:
        json.dump(users, f)

    return updated

def get_current_user(telegram_id):
    current_user = None
    users = read_db(DB_PATH)
    for user in users:
        if user.get("telegram_id") == telegram_id:
            current_user = user

    return current_user

def go_home_cmd(update: Update, text: str) -> str:
    url = "http://localhost:5005/webhooks/rest/webhook"
    processed: str = text.lower()

    telegram_id = str(update.effective_user.id)
    chat_id = update.effective_chat.id
    curr_user = get_user_logged_in(telegram_id)
    sender = curr_user["fullname"] if curr_user is not None else "user"

    data = {
        "sender": sender, 
        "message": processed, 
        "metadata": {
            "telegram_id": telegram_id,
            "fullname": curr_user["fullname"] if curr_user is not None else "Guest",
            "chat_id": chat_id 
        }
    }
    logger.info("attempting to reset go home %r", data)
    # todo: jangan tambahkan jika request belum selesai, kasih flag. jangan sampai request numpuk
    try:
        response = requests.post(url, json=data)
        return response.json()
    except Timeout:
        # request timeout
        logger.info("request timeout...")
        return [{
            "recipient_id": curr_user["fullname"],
            "text": "Mohon maaf, bot belum bisa melayani perintah. Bot sedang mengalami kendala saat mengakses sistem data center."
        }]
    except ConnectionError:
        # connection error
        logger.info("connection error...")
        return [{
            "recipient_id": curr_user["fullname"],
            "text": "Mohon maaf, bot belum bisa melayani perintah. Bot sedang mengalami kendala saat mengakses sistem data center."
        }]
    except HTTPError as err:
        if response.status_code == 503:
            # service tidak tersedia
            logger.info("service is not available...")
            return [{
                "recipient_id": curr_user["fullname"],
                "text": "Mohon maaf, bot belum bisa menerima melayani perintah. Service bot mungkin sedang dimatikan atau dalam perbaikan."
            }]
        else:
            # http error terjadi
            logger.info("there something wrong...")
            return [{
                "recipient_id": curr_user["fullname"],
                "text": "Mohon maaf, bot belum bisa menerima melayani perintah. Service bot sedang ada kendala teknis."
            }]

conversation_handler = ConversationHandler(
    entry_points=[CommandHandler("pin", start_cmd)],
    states={
        ASK_PIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_pin)],
    },
    fallbacks=[CommandHandler("batal", cancel)],
)
