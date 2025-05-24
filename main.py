from typing import Final
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackQueryHandler
from dotenv import load_dotenv
import requests, json, bcrypt, os, re, logging

import logincommand, forgotpasscommand, findcommand, uploadfilecommand
from userloggedin import get_user_logged_in
from mappinguser import verify_phone_number

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

# commands
def escape_special_chars(text):
    return re.sub(r"([-.])", r"\\\1", text)

async def share_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    telegram_id = str(update.effective_user.id)
    if contact:
        phone_number = contact.phone_number
        name = contact.first_name
        verified = verify_phone_number(telegram_id, phone_number)
        if verified:
            await update.message.reply_text(
                f"Terima kasih {name} atas kepercayaannya. \n" 
                "Baik, ada yang bisa saya bantu?", 
                reply_markup=ReplyKeyboardRemove())
        else:
            await update.message.reply_text(
                "Maaf, nomor HP kamu belum terdaftar. Silahkan hubungi administrator."
            )
    else:
        await update.message.reply_text("Maaf, kamu belum bisa mengakses data center sebelum melakukan verifikasi nomor HP")

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
            "Hai, terima kasih sudah menghubungi.\n" 
            "Mohon maaf, bisakah kamu verifikasi nomor teleponmu? \n" 
            "Silakan klik \"Verifikasi Nomor HP\" ",
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
        results = []
        for account in accounts:
            homedir = account['homedir'].lstrip("/")
            fullpath = os.path.join(REPOSITORY_PATH, homedir)
            results.append(fullpath)

            no_str = str(no)
            button = [
                InlineKeyboardButton(
                    text=f"📁 {homedir}",
                    callback_data=f"info_{no_str}"
                )
            ]
            keyboard.append(button)
            no += 1
        
        context.user_data['search_results'] = results
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
    #                 callback_data=f"info_{no_str}"
    #             )
    #             keyboard.append([button])
    #         else:
    #             button = InlineKeyboardButton(
    #                 text=f"{no_str} - Folder {dir}",
    #                 callback_data=f"info_{no_str}"
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
def handle_response(update: Update, text: str) -> str:
    url = "http://localhost:5005/webhooks/rest/webhook"
    processed: str = text.lower()

    telegram_id = str(update.effective_user.id)
    curr_user = get_user_logged_in(telegram_id)
    sender = curr_user["fullname"] if curr_user is not None else "user"
    data = {
        "sender": sender, 
        "message": processed, 
        # "metadata": {
        #     "telegram_id": telegram_id,
        #     "fullname": curr_user["fullname"]
        # }
    }
    response = requests.post(url, json=data)
    return response.json()

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
        response: str = handle_response(update, text)
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
    # download callback query handler
    app.add_handler(CallbackQueryHandler(findcommand.handle_download_btn_callback, pattern=r"^download\|"))
    # buat folder baru command
    # summarize command
    # app.add_handler(CommandHandler('info', findcommand.summarize_command))
    app.add_handler(CallbackQueryHandler(findcommand.summarize_command, pattern=r"^info_\d+$"))
    # remove command
    # app.add_handler(CommandHandler('hapus', findcommand.remove_command))
    app.add_handler(CallbackQueryHandler(findcommand.remove_command, pattern=r"^remove_\d+$"))
    app.add_handler(findcommand.create_folder_handler)
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