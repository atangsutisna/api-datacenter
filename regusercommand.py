from reguser import add_user_to_db
import logging, os, re, requests
from telegram.ext import ConversationHandler
from telegram import Update
from telegram.ext import ContextTypes
import re
from telegram.ext import CommandHandler, MessageHandler, filters, ConversationHandler
from reguser import add_user_to_db

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
    await update.message.reply_text("Masukan username yang bisa diakses (pisahkan dengan koma):")
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

conversation_handler = ConversationHandler(
    entry_points=[CommandHandler("reguser", start_cmd)],
    states={
        ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_phone)],
        ASK_USERNAMES: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_usernames)],
    },
    fallbacks=[CommandHandler("batal", cancel)],
)