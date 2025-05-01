# File bukan hanya script untuk mencari file, tapi juga untuk command donwload atau summarize
# format pencarian file /cari abc.xls
# format summarize /ringkas-no 1
# format hapus /hapus-no

import logging, os, re, requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from dotenv import load_dotenv
from docx import Document

load_dotenv()

ASK_SEARCH = range(1)
ASK_SUMMARIZE = range(1)

REPOSITORY_PATH = os.getenv('REPOSITORY_PATH')

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def escape_special_chars(text):
    return re.sub(r"([-.])", r"\\\1", text)

# cukup kembalikan dalam bentuk list saja
def search(base_path: str, keyword: str) -> str:
    results = []
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if keyword.lower() in file.lower():
                full_path = os.path.join(root, file)
                results.append(full_path)
    return results

def format_to_list(results: list[str]) -> str:
    output = "<b>Hasil Pencarian: </b>\n"
    no = 1
    for path in results:
        filename = os.path.basename(path)
        rep_path = path.split("/repository", 1)[1]
        folder_path = os.path.dirname(rep_path)
        filename_wpath = os.path.join(folder_path, filename)
        output += f"{no} - {filename_wpath}\n"
        no += 1

    return output

def read_docx(file_path: str) -> str:
    doc = Document(file_path)
    hasil = []
    for paragraf in doc.paragraphs:
        isi = paragraf.text.strip()
        if isi:  # hanya ambil paragraf yang tidak kosong
            hasil.append(isi)
        if len(hasil) == 5:
            break
    return "\n\n".join(hasil)

async def ask_search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text('File apa yang sedang kamu cari?')
        return ASK_SEARCH
    else:
        if 'is_logged_in' in context.user_data:
            is_logged_in = context.user_data['is_logged_in']
            if is_logged_in:
                keyword = args[0]
                homedir = context.user_data['homedir']
                fullpath = REPOSITORY_PATH + homedir
                # cukup dapatkan listnya saja
                results = search(fullpath, keyword)
                # lalu, masukan ke dalam context.user_data sebagai list
                # context.user_data['search_results'] = []
                context.user_data['search_results'] = results
                output = format_to_list(results)
                await update.message.reply_text(output, parse_mode="HTML")
        else:
            await update.message.reply_text('Maaf, saya tidak bisa melayani kamu. Ketik /start untuk mulai.')
        return ConversationHandler.END

async def do_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'is_logged_in' in context.user_data:
        is_logged_in = context.user_data['is_logged_in']
        if is_logged_in:
            keyword = update.message.text
            homedir = context.user_data['homedir']
            logger.debug("base path %s", REPOSITORY_PATH)
            fullpath = REPOSITORY_PATH + homedir
            logger.debug("attempting to find %s on %s", keyword, fullpath)
            results = search(fullpath, keyword)
            await update.message.reply_text(results, parse_mode="HTML")
    else:
        await update.message.reply_text('Maaf, saya tidak mengenali kamu. Silakan login terlebih dahulu.')
        return ConversationHandler.END

async def summarize_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text('Silakan balas dengan format /info nomor-file')
    else:
        file_no = args[0]
        search_results = context.user_data['search_results']
        if file_no.isdigit():
            index = int(file_no) - 1
            if 0 <= index < len(search_results):
                path = search_results[index]
                url = "http://localhost:5000/summarize"
                processed = read_docx(path)
                data = {"message": processed}
                # logger.debug("Teks processed: %s", processed)
                response = requests.post(url, json=data)
                response_json = response.json()
                await update.message.reply_text(response_json['summary_text'].lower())
            else:
                await update.message.reply_text(f"Ah, kamu ini bercanda!")
        else:
            await update.message.reply_text("Silakan balas dengan angka 1 sampai 5.")

async def remove_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text('Silakan balas dengan format /info nomor-file')
    else:
        file_no = args[0]
        search_results = context.user_data['search_results']
        if file_no.isdigit():
            index = int(file_no) - 1
            if 0 <= index < len(search_results):
                path = search_results[index]
                filename = os.path.basename(path)
                
                rep_path = path.split("/repository", 1)[1]
                folder_path = os.path.dirname(rep_path)
                filename_wpath = os.path.join(folder_path, filename)
                os.remove(path)
                await update.message.reply_text(f"File {filename_wpath} telah dihapus")
            else:
                await update.message.reply_text(f"Ah, kamu ini bercanda!")
        else:
            count_results = len(context.user_data['search_results'])
            await update.message.reply_text("Silakan balas dengan angka 1 sampai {count_results}.")

async def download_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # todo: check before searching the file
    args = context.args
    if not args:
        await update.message.reply_text('Silakan balas dengan format /kirim-file nomor-file')
    else:
        file_no = args[0]
        search_results = context.user_data['search_results']
        if file_no.isdigit():
            index = int(file_no) - 1
            if 0 <= index < len(search_results):
                path = search_results[index]
                filename = os.path.basename(path)
                # rep_path = path.split("/repository", 1)[1]
                # folder_path = os.path.dirname(rep_path)
                # filename_wpath = os.path.join(folder_path, filename)
                logger.info('attempting to send file on %s', path)
                try:
                    await update.message.reply_document(document=open(path, 'rb'))
                except FileNotFoundError:
                    await update.message.reply_text("File tidak ditemukan.")
            else:
                await update.message.reply_text(f"Ah, yang bener dong! Tolong masukan angka.")
        else:
            count_results = len(context.user_data['search_results'])
            await update.message.reply_text(f"Silakan balas dengan angka 1 sampai {count_results}.")

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f'Ok, terima kasih.')
    return ConversationHandler.END

searching_handler = ConversationHandler(
    entry_points=[CommandHandler("cari", ask_search_command)],
    states={
        ASK_SEARCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, do_search)],
    },
    fallbacks=[CommandHandler("batal", cancel_command)]
)

# tambahkan fungsi untuk summarize
# print(REPOSITORY_PATH + '/atang')
# results = search(REPOSITORY_PATH + '/atang', 'puskesmas')
# print(format_to_list(results))
# path = REPOSITORY_PATH + '/atang/surat-pernyataan-ahli-waris.docx'
# processed = read_docx(path)
# url = "http://localhost:5000/summarize"
# data = {"message": processed}
# logger.debug("Teks processed: %s", processed)
# response = requests.post(url, json=data)
# print(response.json())
# print(processed)