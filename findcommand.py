# File bukan hanya script untuk mencari file, tapi juga untuk command donwload atau summarize
# format pencarian file /cari abc.xls
# format summarize /ringkas-no 1
# format hapus /hapus-no

import logging, os, re, requests
import PyPDF2
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from dotenv import load_dotenv
from docx import Document
from pathlib import Path
import assistant_file_reader, fileconverter;
from userloggedin import get_user_logged_in

load_dotenv()

ASK_SEARCH = range(1)
ASK_SUMMARIZE = range(1)

REPOSITORY_PATH = os.getenv('REPOSITORY_PATH')
OPENAI_APIKEY = os.getenv('OPENAI_APIKEY')

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

def get_ext(path: str) -> str:
    fullpath = Path(path)
    return fullpath.suffix.lstrip(".")

# def escape_special_chars(text):
#     return re.sub(r"([-.])", r"\\\1", text)

# cukup kembalikan dalam bentuk list saja
def search(base_path: str, keyword: str) -> str:
    results = []
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if keyword.lower() in file.lower():
                full_path = os.path.join(root, file)
                results.append(full_path)
    return results

def is_child(parent, child):
    try:
        Path(child).resolve().relative_to(Path(parent).resolve())
        return True
    except ValueError:
        return False

# def format_to_list(results: list[str]) -> str:
#     output = "<b>Hasil Pencarian: </b>\n"
#     no = 1
#     for path in results:
#         filename = os.path.basename(path)
#         rep_path = path.split("/repository", 1)[1]
#         folder_path = os.path.dirname(rep_path)
#         filename_wpath = os.path.join(folder_path, filename)
#         output += f"{no} - {filename_wpath}\n"
#         no += 1

#     return output

# # read docx
# def read_docx(file_path: str) -> str:
#     doc = Document(file_path)
#     hasil = []
#     for paragraf in doc.paragraphs:
#         isi = paragraf.text.strip()
#         if isi:  # hanya ambil paragraf yang tidak kosong
#             hasil.append(isi)
#         if len(hasil) == 5:
#             break
#     return "\n\n".join(hasil)

# # read pdf
# def read_pdf(filepath: str) -> str:
#     with open(filepath, "rb") as file:
#         reader = PyPDF2.PdfReader(file)
#         text = ""
#         for page in reader.pages:
#             text += page.extract_text() or ""
#         return text[:1000]

async def ask_search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text('File apa yang kamu cari? klik /batal jika kamu urung mencarinya')
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
                if not results:
                    await update.message.reply_text(f"Tidak ditemukan file dengan keyword {keyword}", parse_mode="HTML")
                else:
                    # lalu, masukan ke dalam context.user_data sebagai list
                    # context.user_data['search_results'] = []
                    context.user_data['search_results'] = results
                    no = 1
                    keyboard = []
                    for path in results:
                        filename = os.path.basename(path)
                        rep_path = path.split("/repository", 1)[1]
                        folder_path = os.path.dirname(rep_path)
                        filename_wpath = os.path.join(folder_path, filename)
                        button = InlineKeyboardButton(
                            text=f"{no} - {filename_wpath} /info",
                            callback_data=f"info_{no}"
                        )
                        keyboard.append([button])
                        no += 1
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await update.message.reply_text("Hasil Pencarian: ", reply_markup=reply_markup)
        else:
            await update.message.reply_text('Maaf, saya tidak bisa melayani kamu. Ketik /login untuk mulai.')
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
            if not result:
                await update.message.reply_text(f"Tidak ditemukan file dengan keyword {keyword}")
            else:
                await update.message.reply_text(results, parse_mode="HTML")
    else:
        await update.message.reply_text('Maaf, saya tidak mengenali kamu. Silakan login terlebih dahulu. Ketik /login untuk mulai.')
        return ConversationHandler.END

async def summarize_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    # cek permissions: apakah diperbolehkan untuk read?
    # permission dicek berdasarkan path folder
    # misal: homedir atang: /atang
    # get current user dicek homdir-nya juga permissionnya
    data = query.data
    file_no = int(data.split("_")[1])
    logger.info("Got params with id %s", file_no)

    index = int(file_no) - 1
    search_results = context.user_data['search_results']
    logger.info("attempting to find array with idx %d", index)
    current_dir = search_results[index]
    logger.info("current directory: %s", current_dir)
    # set current directory
    context.user_data['current_directory'] = current_dir
    # check current directory name
    if current_dir == REPOSITORY_PATH:
        # get home directory the user
        telegram_id = str(update.effective_user.id)
        curr_user = get_user_logged_in(telegram_id)
        if curr_user is None:
            await update.message.reply_text('Maaf, anda belum bisa mengakses data center. Silakan verifikasi nomor HP kamu')
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
                button = InlineKeyboardButton(
                    text=f"📁 {homedir}",
                    callback_data=f"info_{no_str}"
                )
                keyboard.append([button])
                no += 1
            context.user_data['search_results'] = results
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("Ini workspace kamu: ", reply_markup=reply_markup)
    else:
        # dirname = os.path.dirname(current_dir)
        is_file = os.path.isfile(current_dir)
        path = current_dir
        # context.user_data['current_directory'] = os.path.dirname(current_dir)
        if is_file:
            # summarize file
            button = [
                InlineKeyboardButton(
                    text=f"<< Kembali ",
                    callback_data=f"info_0"
                )
            ]
            reply_markup = InlineKeyboardMarkup([button])

            ext = get_ext(path)
            supported_extension = {"pdf", "doc", "docx", "txt"}
            if ext in supported_extension:
                logger.info("attempting to send request to openai")
                result = assistant_file_reader.read_file_with_file_search(
                    api_key=OPENAI_APIKEY,
                    file_path=path
                )
                await query.edit_message_text(result, reply_markup=reply_markup)
            else:
                logger.info(f"attempting to convert {path} to pdf")
                tmp_file_fullpath = fileconverter.convert_to_pdf(path)
                logger.info("attempting to ask to openai")
                result = assistant_file_reader.read_file_with_file_search(
                    api_key=OPENAI_APIKEY,
                    file_path=tmp_file_fullpath
                )
                await query.edit_message_text(result, reply_markup=reply_markup)
                os.remove(tmp_file_fullpath)
        else:
            # list of childs folder
            logger.info("list all child of %s", current_dir)
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
            await query.edit_message_text(f"📂 : {current_dir} ", reply_markup=reply_markup)
    # args = context.args
    # if not args:
    #     await update.message.reply_text('Silakan balas dengan format /info nomor-file')
    # else:
    #     file_no = args[0]
    #     search_results = context.user_data['search_results']
    #     if file_no.isdigit():
    #         index = int(file_no) - 1
    #         if 0 <= index < len(search_results):
    #             path = search_results[index]
    #             # cek apakah folder atau file
    #             is_file = os.path.isfile(path)
    #             if is_file:
    #                 logger.debug("attempting to read file %s", path)
    #                 ext = get_ext(path)
    #                 supported_extension = {"pdf", "doc", "docx", "txt"}
    #                 if ext in supported_extension:
    #                     logger.info("attempting to send request to openai")
    #                     result = assistant_file_reader.read_file_with_file_search(
    #                         api_key=OPENAI_APIKEY,
    #                         file_path=path
    #                     )
    #                     await update.message.reply_text(result)
    #                 else:
    #                     # should be convert to pdf
    #                     logger.info(f"attempting to convert {path} to pdf")
    #                     tmp_file_fullpath = fileconverter.convert_to_pdf(path)
    #                     logger.info("attempting to ask to openai")
    #                     result = assistant_file_reader.read_file_with_file_search(
    #                         api_key=OPENAI_APIKEY,
    #                         file_path=tmp_file_fullpath
    #                     )
    #                     await update.message.reply_text(result)
    #                     os.remove(tmp_file_fullpath)
    #             else:
    #                 logger.debug("attempting to open folder %s", path)
    #                 homedir = context.user_data['homedir']
    #                 dir_list = os.listdir(path)
    #                 no = 1
    #                 results = []
    #                 message = "<b>Hasil Pencarian:</b>\n"
    #                 for dir in dir_list:
    #                     full_path = os.path.join(path, dir)
    #                     logger.info("full path %s",full_path)
    #                     results.append(full_path)
    #                     is_file = os.path.isfile(path + "/" + dir)
    #                     no_str = str(no)
    #                     if is_file:
    #                         message += f"{no_str}. {dir}\n"
    #                     else:
    #                         message += f"{no_str}. <b>Folder</b> {dir}\n"
    #                     no += 1
    #                 message = (message)
    #                 context.user_data['search_results'] = results
    #                 await update.message.reply_text(message, parse_mode="HTML")
    #         else:
    #             await update.message.reply_text(f"Ah, kamu ini bercanda!")
    #     else:
    #         await update.message.reply_text("Silakan balas dengan angka 1 sampai 5.")

async def remove_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    file_no = int(data.split("_")[1])
    logger.info("attempting to find file to be delete with no %s", file_no)
    if 'search_results' not in context.user_data:
        await query.message.reply_text("Mohon maaf, data gagal dihapus. Ada proses perbaikan sistem, sehingga saya lupa file apa yang akan kamu hapus. Silahkan diulang dari awal.")
    else:
        index = int(file_no) - 1
        search_results = context.user_data['search_results']
        if 0 <= index < len(search_results):
            path = search_results[index]
            # get parent directory
            # telegram_id = str(update.effective_user.id)
            # logger.info("attempting to find current user with telegram id %s", telegram_id)
            # curr_user = get_user_logged_in(telegram_id)
            # accounts = curr_user['accounts']
            # for account in accounts:
            #     parent_dir = account['parentdir']
            #     if is_child(parent_dir, path):
            #         logger.info("The %s is child of %s, so then checking permission for delete", path, parent_dir)
            #         permissions = account['permissions'].split("|")
                    # if permitted then remove it
                    # else show error message

            # remove the folder or file
            filename = os.path.basename(path)
            
            rep_path = path.split("/repository", 1)[1]
            folder_path = os.path.dirname(rep_path)
            filename_wpath = os.path.join(folder_path, filename)
            os.remove(path)
            # todo: reload all file
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
            await query.edit_message_text(f"File sudah dihapus\n. 📂 : {current_dir} ", reply_markup=reply_markup)
            # await query.message.reply_text(f"File {filename_wpath} telah dihapus")
        else:
            await query.message.reply_text(f"Ah, kamu ini bercanda!")
    # args = context.args
    # if not args:
    #     await update.message.reply_text('Silakan balas dengan format /info nomor-file')
    # else:
    #     file_no = args[0]
    #     search_results = context.user_data['search_results']
    #     if file_no.isdigit():
    #         index = int(file_no) - 1
    #         if 0 <= index < len(search_results):
    #             path = search_results[index]
    #             filename = os.path.basename(path)
                
    #             rep_path = path.split("/repository", 1)[1]
    #             folder_path = os.path.dirname(rep_path)
    #             filename_wpath = os.path.join(folder_path, filename)
    #             os.remove(path)
    #             await update.message.reply_text(f"File {filename_wpath} telah dihapus")
    #         else:
    #             await update.message.reply_text(f"Ah, kamu ini bercanda!")
    #     else:
    #         count_results = len(context.user_data['search_results'])
    #         await update.message.reply_text("Silakan balas dengan angka 1 sampai {count_results}.")

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