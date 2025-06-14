import logging, os, re
from checkpermissions import is_permitted
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from dotenv import load_dotenv
from userloggedin import get_user_logged_in

load_dotenv()

REPOSITORY_PATH = os.getenv('REPOSITORY_PATH')

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

WAITING_FOR_FILE = range(1)

# fix me, do not hard code
# FOLDER_PATH = "/home/kangatang/git/filegator/repository/atang"
async def start_upload_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = str(update.effective_user.id)
    curr_user = get_user_logged_in(telegram_id)
    if curr_user is None:
        await update.message.reply_text('Maaf, saya belum bisa melayani kamu. Silahkan verifikasi dulu nomor HPmu.')
    else:
        if "current_directory" not in context.user_data:
            await update.message.reply_text('Mohon tentukan terlebih dahulu di folder mana kamu akan menyimpan filenya')
        else:
            # todo: check permissions
            telegram_id = str(update.effective_user.id)
            
            target_path = context.user_data['current_directory']
            upload_permitted = is_permitted(telegram_id, target_path, "upload")
            if not upload_permitted:
                await update.message.reply_text("Mohon maaf, kamu tidak punya ijin untuk melakukan upload.")
                return

            await update.message.reply_text('Silakan kirim file satu per satu. Ketik /selesai jika sudah.')
            context.user_data["uploaded_files"] = []
            return WAITING_FOR_FILE        


async def receive_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info('starting to process upload file')
    # ensure folder path exists
    if "current_directory" not in context.user_data:
        await update.message.reply_text('Mohon tentukan terlebih dahulu di folder mana kamu akan menyimpan filenya')
        return ConversationHandler.END
    
    # cek foto
    if update.message.photo:
        photo_list = update.message.photo
        photo = photo_list[-1] # mengambil gambar dengan resolusi tertinggi
        logger.info('attempting to process photo with id %s', photo.file_id)
        file = await context.bot.get_file(photo.file_id)

        os.makedirs(FOLDER_PATH, exist_ok=True)
        filename = f"photo_{photo.file_id}.jpg"
        file_path = os.path.join(FOLDER_PATH, filename)
        await file.download_to_drive(file_path)

        context.user_data['uploaded_files'].append(filename)
        await update.message.reply_text(f"File {filename} telah disimpan. Klik atau ketik /selesai jika sudah.")
        return WAITING_FOR_FILE
    elif update.message.document:
        document = update.message.document
        file_id = document.file_id
        file = await context.bot.get_file(file_id)

        # ensure folder path exists
        FOLDER_PATH = context.user_data['current_directory']
        logger.info('attempting to upload file with id %s to %s', file_id, FOLDER_PATH)
        os.makedirs(FOLDER_PATH, exist_ok=True)

        file_path = os.path.join(FOLDER_PATH, document.file_name)
        await file.download_to_drive(file_path)

        context.user_data['uploaded_files'].append(document.file_name)
        await update.message.reply_text(f"File {document.file_name} telah disimpan. Klik atau ketik /selesai jika sudah.")
        return WAITING_FOR_FILE
    else:
        await update.message.reply_text("Tolong kirim file. Atau ketik /selesai jika sudah.")
        return WAITING_FOR_FILE
    # document = update.message.document
    # if not document:
    #     logger.info('The message is not document')
    #     await update.message.reply_text("Tolong kirim file. Atau ketik /selesai jika sudah.")
    #     return WAITING_FOR_FILE
    
async def done_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uploaded = context.user_data.get('uploaded_files', [])
    if uploaded:
        current_dir = context.user_data['current_directory']
        dir_list = os.listdir(current_dir)
        keyboard = []
        no = 1
        results = []
        for dir in dir_list:
            child_path = os.path.join(current_dir, dir)
            results.append(child_path)

            no_str = str(no)
            file = os.path.isfile(child_path)
            if not file:
                buttons = [
                    InlineKeyboardButton(
                        text=f"File {dir}",
                        callback_data=f"info_{no_str}"
                    ),
                    InlineKeyboardButton(
                        text=f"❌",
                        callback_data=f"remove_{no_str}"
                    )
                ]
            else:
                buttons = [
                    InlineKeyboardButton(
                        text=f"{dir}",
                        callback_data=f"info_{no_str}"
                    ),
                    InlineKeyboardButton(
                        text=f"❌",
                        callback_data=f"remove_{no_str}"
                    )
                ]
            keyboard.append(buttons)
            no += 1
            
        parent_dir = os.path.dirname(current_dir)
        results.append(os.path.join(REPOSITORY_PATH, parent_dir))
        context.user_data['search_results'] = results
        
        no_str = str(no)
        button = InlineKeyboardButton(
            text=f"<< Kembali ",
            callback_data=f"info_{no_str}"
        )
        keyboard.append([button])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(f"📂 {len(uploaded)} file berhasil diunggah. \n 📂 : {current_dir}", reply_markup=reply_markup)
    else:
        results = []
        keyboard = []

        current_dir = context.user_data['current_directory']
        parent_dir = os.path.dirname(current_dir)
        results.append(os.path.join(REPOSITORY_PATH, parent_dir))
        context.user_data['search_results'] = results

        button = InlineKeyboardButton(
            text=f"<< Kembali ",
            callback_data=f"info_{1}"
        )
        keyboard.append([button])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(f"Tidak ada file yang dikirim.\n 📂 : {current_dir}", reply_markup=reply_markup)

    return ConversationHandler.END

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Upload dibatalkan. Terima kasih.')
    return ConversationHandler.END

upload_cmd_handler = ConversationHandler(
    entry_points=[CommandHandler("upload", start_upload_cmd)],
    states={
        WAITING_FOR_FILE: [
            CommandHandler("selesai", done_upload),
            MessageHandler(filters.ALL, receive_file)
        ],
    },
    fallbacks=[CommandHandler("batal", cancel_command)]
)