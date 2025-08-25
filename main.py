from typing import Final
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackQueryHandler
from dotenv import load_dotenv
import requests, json, bcrypt, os, re, logging

import logincommand, forgotpasscommand, findcommand, uploadfilecommand, regusercommand, addaccount, rmaccount
from userloggedin import get_user_logged_in
from mappinguser import verify_phone_number
from myutils import hash_path
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException

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
    context.user_data.clear()

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
            fullpath = os.path.join(REPOSITORY_PATH, homedir)

            hashed_path = hash_path(fullpath)
            context.user_data[hashed_path] = fullpath    

            # no_str = str(no)
            button = [
                InlineKeyboardButton(
                    text=f"📁 {homedir}",
                    callback_data=f"info|{hashed_path}"
                )
            ]
            keyboard.append(button)
            no += 1
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Ini workspace kamu: ", reply_markup=reply_markup)

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
        "metadata": {
            "telegram_id": telegram_id,
            "fullname": curr_user["fullname"]
        }
    }
    logger.info("attempting to send request with params %r", data)
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
        if text.isdigit():
            # kemungkinan besar, user sedang berada di folder utama
            message = "tolong buka nomor "+ text
            responses: str = handle_response(update, message)
        else:
            responses: str = handle_response(update, text)
        chat_id = update.effective_chat.id
        # logger.info('Bot: %r', responses)
        for response in responses:
            logger.info("response %r", response)
            if "text" in response:
                await update.message.reply_text(
                    response['text'],
                    parse_mode="Markdown"
                )
            if "attachment" in response:
                attachment = response['attachment']
                path_to_file = attachment["payload"]["url"]
                caption = attachment['payload']['title']
                logger.info("Got path to file %s with capton %s", path_to_file, caption)
                # caption = "Sample.pdf"
                await context.bot.send_document(
                    chat_id=chat_id,
                    document=open(path_to_file, "rb"),
                    caption=f"📎 Klik untuk mengunduh",
                    parse_mode="Markdown"
                )

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f'Update {update} caused error {context.error}')

async def fallback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Perintah tidak dikenal. Gunakan /cancel untuk keluar.")
    return USERNAME  # Kembali ke state sebelumnya

async def check_status_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.message.reply_text("Cek status callback")

if __name__ == '__main__':
    logger.info('Starting bot...')
    # logger.debug('ini debugg...')
    app = Application.builder().token(os.getenv('TOKEN')).build()
    
    app.add_handler(CommandHandler('start', start_command))
    
    # share contact handler
    app.add_handler(MessageHandler(filters.CONTACT, share_contact))
    
    # login command
    app.add_handler(logincommand.login_convhandler)
    
    # forgot password command
    app.add_handler(forgotpasscommand.forgotpass_convhandler)
    
    # upload command
    app.add_handler(uploadfilecommand.upload_cmd_handler)
    
    # search command handler
    app.add_handler(CommandHandler('cari', findcommand.search_command_handler))

    # download callback query handler
    app.add_handler(CallbackQueryHandler(findcommand.handle_download_btn_callback, pattern=r"^download\|"))
    
    # summarize command
    app.add_handler(CallbackQueryHandler(findcommand.summarize_command, pattern=r"^info\|"))
    
    # remove command
    app.add_handler(CallbackQueryHandler(findcommand.remove_command, pattern=r"^remove\|"))

    # just for test /cek_status handler
    app.add_handler(CallbackQueryHandler(check_status_query_handler, pattern=r"/cek_status"))
    
    # create folder command
    app.add_handler(findcommand.create_folder_handler)
    
    # add user to db (usermapping)
    app.add_handler(regusercommand.conversation_handler)

    # add account to user
    app.add_handler(addaccount.conversation_handler)

    # remove account to user
    app.add_handler(rmaccount.conversation_handler)

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