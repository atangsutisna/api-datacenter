import logging, os, re
from telegram import Update
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
            await update.message.reply_text('Mohon tentukan terlebih dahulu di folder mana kamu akan menyimpan filenya. \nKirim perintah /list untuk melihat semua folder.')
        else:  
            await update.message.reply_text('Silakan kirim file satu per satu. Ketik /selesai jika sudah.')
            context.user_data["uploaded_files"] = []
            return WAITING_FOR_FILE        


async def receive_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info('starting to process upload file')
    # todo: check permissions
    # ensure folder path exists
    if "current_directory" not in context.user_data:
        await update.message.reply_text('Mohon tentukan terlebih dahulu di folder mana kamu akan menyimpan filenya')
        return WAITING_FOR_FILE
    
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
        await update.message.reply_text(
            f"{len(uploaded)} file berhasil diunggah:\n" + "\n".join(uploaded)
        )
    else:
        await update.message.reply_text("Tidak ada file yang dikirim.")
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