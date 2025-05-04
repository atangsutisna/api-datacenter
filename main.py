from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from dotenv import load_dotenv
import requests, json, bcrypt, os, re, logging

import logincommand, forgotpasscommand, findcommand, uploadfilecommand

BOT_USERNAME: Final = '@dcinisiatifdev_bot'
REPOSITORY_PATH = os.getenv('REPOSITORY_PATH')

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)
load_dotenv()

# commands
def escape_special_chars(text):
    return re.sub(r"([-.])", r"\\\1", text)

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f'Ok, terima kasih.')
    return ConversationHandler.END
# end login function

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('I am datacenter assitant.  Please type something so I can respond!')

# list all directory on user's home
async def ls_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_logged_in = context.user_data['is_logged_in']
    homedir = context.user_data['homedir']
    if is_logged_in:
        dir_list = os.listdir(REPOSITORY_PATH + homedir)
        no = 1
        results = []
        message = "<b>Hasil Pencarian:</b>\n"
        for dir in dir_list:
            full_path = os.path.join(REPOSITORY_PATH + homedir, dir)
            results.append(full_path)
            is_file = os.path.isfile(REPOSITORY_PATH + homedir + "/" + dir)
            no_str = str(no)
            if is_file:
                message += f"{no_str}. {dir}\n"
            else:
                message += f"{no_str}. <b>Folder</b> {dir}\n"
            no += 1
        message = (message)
        context.user_data['search_results'] = results
        await update.message.reply_text(message, parse_mode="HTML")
    else:
        await update.message.reply_text('Maaf, anda belum bisa mengakses data center.')

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
    app = Application.builder().token(os.getenv('TOKEN')).build()
    
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
    app.add_handler(CommandHandler('info', findcommand.summarize_command))
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