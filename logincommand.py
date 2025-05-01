import logging, os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from dotenv import load_dotenv
import json,bcrypt

load_dotenv()

USERNAME, PASSWORD = range(2)
USER_REPOSITORY_PATH = os.getenv('USER_REPOSITORY_PATH')

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

def find_user(username: str):
    with open(USER_REPOSITORY_PATH, 'r', encoding='utf-8') as file:
        users = json.load(file)

    user = None
    for user_id, user_data in users.items():
        if user_data["username"] == username:
            user = user_data
            break
    return user

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Halo, selamat datang di datacenter inisiatif. Bisa tolong sebutkan username anda?')
    return USERNAME

async def get_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.text
    found_user = find_user(username)

    if not found_user:
        await update.message.reply_text('''
        Username tidak dikenali,\n silahkan ulangi atau /cancel untuk membatalkan
        ''', parse_mode='MarkdownV2') 
        return USERNAME 

    context.user_data['username'] = update.message.text
    await update.message.reply_text('Baik, bisa sebutkan passwordnya?')
    return PASSWORD

async def get_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # simpan di dalam context data user
    username = context.user_data['username']
    password = update.message.text

    with open(USER_REPOSITORY_PATH, 'r', encoding='utf-8') as file:
        users = json.load(file)

    # checking username
    found_user = None
    for user_id, user_data in users.items():
        if user_data["username"] == username:
            found_user = user_data
            break

    if not found_user:
        await update.message.reply_text('''
        Username tidak dikenali, 
        silahkan coba lagi atau /cancel untuk membatalkan
        ''') 
        return USERNAME 
    else:
        # checking password
        hashed_passwd = found_user['password'].encode('utf-8')
        pass_value = password.encode('utf-8')
        if bcrypt.checkpw(pass_value, hashed_passwd):
            fullname = found_user['name']
            context.user_data['is_logged_in'] = True
            context.user_data['homedir'] = found_user['homedir']
            context.user_data['permissions'] = found_user['permissions']
            await update.message.reply_text(f'Hai, {fullname}. Selamat datang kembali')
        else:
            await update.message.reply_text('''
            Password salah, silakan ulangi atau /cancel untuk membatalkan
            ''')
            return PASSWORD
    
    return ConversationHandler.END

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f'Ok, terima kasih.')
    return ConversationHandler.END

async def fallback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Perintah tidak dikenal. Gunakan /cancel untuk keluar.")
    return USERNAME  # Kembali ke state sebelumnya

login_convhandler = ConversationHandler(
    entry_points=[CommandHandler("start", start_command)],
    states={
        USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_username)],
        PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_password)]
    },
    fallbacks=[CommandHandler("cancel", cancel_command), MessageHandler(filters.ALL, fallback_handler)]
)

# user = find_user("atang")
# if not user:
#     print("user not found")
# else:
#     print("user ditemukan")