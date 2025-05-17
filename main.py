from typing import Final
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackQueryHandler
from dotenv import load_dotenv
import requests, json, bcrypt, os, re, logging

import logincommand, forgotpasscommand, findcommand, uploadfilecommand

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
# logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)
load_dotenv()

BOT_USERNAME: Final = '@dcinisiatifdev_bot'
REPOSITORY_PATH = os.getenv('REPOSITORY_PATH')
DB_PATH = os.getenv('DB_PATH')

# load user logged in
def get_user_logged_in(telegram_id: str):
    logger.info("attempting to find user with telegram id %s", telegram_id)
    with open(DB_PATH, 'r', encoding='utf-8') as file:
        users_loggedin = json.load(file)
    user = None
    for user_data in users_loggedin:
        if user_data["telegram_id"] == telegram_id:
            logger.info("Got user with telegram id %s", telegram_id)
            user = user_data
            break
    return user

# commands
def escape_special_chars(text):
    return re.sub(r"([-.])", r"\\\1", text)

async def share_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    if contact:
        nomor = contact.phone_number
        nama = contact.first_name
        await update.message.reply_text(f"Terima kasih, {nama}. Nomor HP kamu: {nomor}")
    else:
        await update.message.reply_text("Tidak menerima nomor kontak.")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = str(update.effective_user.id)
    curr_user = get_user_logged_in(telegram_id)
    logger.info("current user %r", curr_user)
    if curr_user is None:
        # await update.message.reply_text('Halo, saya asisten data center. Ada yang bisa saya bantu?')
        logger.info("failed to find user with telegram id %s", telegram_id)
        tombol_kontak = KeyboardButton("Verifikasi Nomor HP", request_contact=True)
        markup = ReplyKeyboardMarkup([[tombol_kontak]], one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            "Silakan bagikan nomor HP Anda dengan menekan tombol di bawah.",
            reply_markup=markup
        )
    else:
        fullname = curr_user['fullname']
        await update.message.reply_text(f"Halo,  {fullname} saya asisten data center. Ada yang bisa saya bantu?")

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f'Ok, terima kasih.')
    return ConversationHandler.END
# end login function

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('I am datacenter assitant.  Please type something so I can respond!')

# list all directory on user's home
async def ls_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # get current telegram id
    telegram_id = str(update.effective_user.id)
    logger.info("attempting to find user with telegram id %s", telegram_id)
    curr_user = get_user_logged_in(telegram_id)
    if curr_user is None:
        await update.message.reply_text('Maaf, anda belum bisa mengakses data center. Klik /login untuk mulai')
    else:
        accounts = curr_user['accounts']
        keyboard = []
        no = 1
        for account in accounts:
            homedir = account['homedir'].lstrip("/")
            no_str = str(no)
            button = InlineKeyboardButton(
                text=f"Folder {homedir}",
                callback_data=f"pilih_{no_str}"
            )
            keyboard.append([button])
            no += 1
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Ini workspace kamu: ", reply_markup=reply_markup)
    # homedir = context.user_data['homedir']
    # if is_logged_in:
    #     dir_list = os.listdir(REPOSITORY_PATH + homedir)
    #     no = 1
    #     results = []
    #     # message = "<b>Hasil Pencarian:</b>\n"
    #     keyboard = []
    #     for dir in dir_list:
    #         full_path = os.path.join(REPOSITORY_PATH + homedir, dir)
    #         results.append(full_path)
    #         is_file = os.path.isfile(REPOSITORY_PATH + homedir + "/" + dir)
    #         no_str = str(no)
    #         if is_file:
    #             button = InlineKeyboardButton(
    #                 text=f"{no_str} - {dir}",
    #                 callback_data=f"pilih_{no_str}"
    #             )
    #             keyboard.append([button])
    #         else:
    #             button = InlineKeyboardButton(
    #                 text=f"{no_str} - Folder {dir}",
    #                 callback_data=f"pilih_{no_str}"
    #             )
    #             keyboard.append([button])
    #         no += 1
    #     # message = (message)
    #     context.user_data['search_results'] = results
    #     # await update.message.reply_text(message, parse_mode="HTML")
    #     reply_markup = InlineKeyboardMarkup(keyboard)
    #     await update.message.reply_text("Hasil Pencarian: ", reply_markup=reply_markup)
    # else:
    #     await update.message.reply_text('Maaf, anda belum bisa mengakses data center. Klik /login untuk mulai')

# handle responses
def handle_response(text: str) -> str:
    url = "http://localhost:5005/webhooks/rest/webhook"
    processed: str = text.lower()
    data = {"sender": "user", "message": processed}
    response = requests.post(url, json=data)
    return response.json()
    # if 'hello' in processed:
    #     return 'Hey there'
    # if 'how are you' in processed:
    #     return 'I am good'
    # if 'you know ali?' in processed:
    #     return 'Yes, I know. He is handsome guy!'

    # return 'Maaf, saya tidak mengerti'

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    logger.info(f'User ({update.message.chat.id}) in {message_type}: "{text}"')
    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)
        logger.info('Bot: %s', response)
        await update.message.reply_text(response[0]['text'])
    # url = "http://localhost:5005/webhooks/rest/webhook"
    # processed: str = text.lower()
    # data = {"sender": "user", "message": processed}
    # responses = requests.post(url, json=data).json()
    # for resp in responses:
    #     if "image" in resp:
    #         await update.message.reply_photo(photo=resp['image'])
    #     elif "text" in resp:
    #         await update.message.reply_text(resp['text'])

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f'Update {update} caused error {context.error}')

async def fallback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Perintah tidak dikenal. Gunakan /cancel untuk keluar.")
    return USERNAME  # Kembali ke state sebelumnya

if __name__ == '__main__':
    logger.info('Starting bot...')
    # logger.debug('ini debugg...')
    app = Application.builder().token(os.getenv('TOKEN')).build()
    
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(MessageHandler(filters.CONTACT, share_contact))
    # login command
    app.add_handler(logincommand.login_convhandler)
    # forgot password command
    app.add_handler(forgotpasscommand.forgotpass_convhandler)
    # upload command
    app.add_handler(uploadfilecommand.upload_cmd_handler)
    # search command
    app.add_handler(findcommand.searching_handler)
    # download command
    app.add_handler(CommandHandler('kirim', findcommand.download_command))
    # summarize command
    app.add_handler(CallbackQueryHandler(findcommand.summarize_command, pattern=r"^pilih_\d+$"))
    # app.add_handler(CommandHandler('info', findcommand.summarize_command))
    # remove command
    app.add_handler(CommandHandler('hapus', findcommand.remove_command))

    # help command
    app.add_handler(CommandHandler('bantuan', help_command))

    # list homedir handler
    app.add_handler(CommandHandler('list', ls_command))
    # Message
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    # Error
    app.add_error_handler(error)
    logger.info('Starting polling...')
    app.run_polling(poll_interval=3)