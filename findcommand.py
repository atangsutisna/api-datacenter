# File bukan hanya script untuk mencari file, tapi juga untuk command donwload atau summarize
# format pencarian file /cari abc.xls
# format summarize /ringkas-no 1
# format hapus /hapus-no

import logging, os, re, requests, hashlib
import PyPDF2
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from dotenv import load_dotenv
from docx import Document
from pathlib import Path
import assistant_file_reader, fileconverter;
from userloggedin import get_user_logged_in
from checkpermissions import is_permitted
import shutil

load_dotenv()

ASK_SEARCH = range(1)
ASK_SUMMARIZE = range(1)
ASK_FOLDER_NAME = range(1)

REPOSITORY_PATH = os.getenv('REPOSITORY_PATH')
OPENAI_APIKEY = os.getenv('OPENAI_APIKEY')

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

def hash_path(path):
    return hashlib.sha1(path.encode()).hexdigest()[:10]

def get_ext(path: str) -> str:
    fullpath = Path(path)
    return fullpath.suffix.lstrip(".")

# cukup kembalikan dalam bentuk list saja
def search(base_path: str, keyword: str):
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

def get_folder_size_bytes(folder_path):
    total_size = 0
    for dirpath, _, filenames in os.walk(folder_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.isfile(fp):
                total_size += os.path.getsize(fp)
    return total_size    

def get_folder_size(folder_path):
    # total_size = 0
    # for dirpath, dirnames, filenames in os.walk(folder_path):
    #     for filename in filenames:
    #         filepath = os.path.join(dirpath, filename)
    #         if os.path.isfile(filepath):  # pastikan benar-benar file
    #             total_size += os.path.getsize(filepath)
    
    # total_size = total_size / (1024 * 1024)
    total_size = 0
    for dirpath, _, filenames in os.walk(folder_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.isfile(fp):
                total_size += os.path.getsize(fp)
    return total_size

def get_file_size(file_path):
    return os.path.getsize(file_path)

def format_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024**2:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024**3:
        return f"{size_bytes / 1024**2:.2f} MB"
    else:
        return f"{size_bytes / 1024**3:.2f} GB"
    # units = ['B', 'kB', 'MB', 'GB', 'TB']
    # i = 0
    # while size_bytes >= 1024 and i < len(units) - 1:
    #     size_bytes /= 1024.0
    #     i += 1
    # return f"{size_bytes:,.2f} {units[i]}"

def list_dir(current_dir: str):
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
            
    no_str = str(no)
    logger.info(f"button back is place for no {no_str}")
    button = InlineKeyboardButton(
        text=f"<< Kembali ",
        callback_data=f"info_{no_str}"
    )
    keyboard.append([button])
    return {
        "results": results,
        "keyboard": keyboard 
    }


async def search_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = str(update.effective_user.id)
    curr_user = get_user_logged_in(telegram_id)
    if curr_user is None:
        await update.message.reply_text('Maaf, anda belum bisa mengakses data center. Silakan verifikasi nomor HP kamu')
        return

    args = context.args
    if not args:
        await update.message.reply_text('❌ Format pencarian data keliru. Gunakan perintah seperti ini: /cari [nama file]')
        return
    else:
        # keyword = args[0]
        keyword = ' '.join([arg for arg in context.args if arg.strip()])

        results = []
        accounts = curr_user['accounts']
        for account in accounts:
            homedir = account['homedir'].lstrip("/")
            base_path = os.path.join(REPOSITORY_PATH, homedir)
            logger.info("attempting to find file with key %s on path %s", keyword, base_path)
            for root, dirs, files in os.walk(base_path):
                # find a folder with name like keyword
                for dir_name in dirs:
                    if keyword.lower() in dir_name.lower():
                        fullpath = os.path.join(root, dir_name)
                        results.append(fullpath)

                # find for a file
                for file in files:
                    if keyword.lower() in file.lower():
                        fullpath = os.path.join(root, file)
                        results.append(fullpath)

        if len(results) == 0:
            await update.message.reply_text(f"Saya tidak dapat menemukan file atau data yang mengandung kata \"{keyword}\" 😞")
        else:
            # show all in the buttons
            no = 1
            await update.message.reply_text(f"Hasil pencarian: {keyword}")
            for dir in results:
                # save to user_data
                hashed_path = hash_path(dir)
                context.user_data[hashed_path] = dir
                
                no_str = str(no)
                file = os.path.isfile(dir)
                if not file:
                    # folder
                    total_size = get_folder_size(dir)
                    logger.info("%s is not a file but dir", file)
                    folder_name = os.path.basename(dir)
                    rep_path = dir.split("/repository", 1)[1]
                    parent_path = os.path.dirname(rep_path)
                    folder_path = os.path.join(parent_path, folder_name)

                    keyboard = []
                    buttons = [
                        InlineKeyboardButton(
                            text="\u2139 Info",
                            callback_data=f"info_{no_str}"
                        ),
                        InlineKeyboardButton(
                            text="⬇️ Zip & Unduh",
                            callback_data=f"download|{hashed_path}"
                        ),
                        InlineKeyboardButton(
                            text="❌ Hapus",
                            callback_data=f"remove_{no_str}"
                        )
                    ]
                    keyboard.append(buttons)
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    size = format_size(total_size)
                    await update.message.reply_text(f"📂 `{folder_path}` (`{size}`)", reply_markup=reply_markup, parse_mode="Markdown")
                else:
                    logger.info("%s is a file", dir)
                    total_size = get_file_size(dir)

                    file_name = os.path.basename(dir)
                    rep_path = dir.split("/repository", 1)[1]
                    parent_path = os.path.dirname(rep_path)
                    file_path = os.path.join(parent_path, file_name)

                    keyboard = []                
                    buttons = [
                        InlineKeyboardButton(
                            text="\u2139 Info",
                            callback_data=f"info_{no_str}"
                        ),
                        InlineKeyboardButton(
                            text="⬇️ Unduh",
                            callback_data=f"download|{hashed_path}"
                        ),
                        InlineKeyboardButton(
                            text=f"❌ Hapus",
                            callback_data=f"remove|{hashed_path}"
                        )
                    ]
                    keyboard.append(buttons)
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    size = format_size(total_size)
                    await update.message.reply_text(f"📂 `{file_path}` (`{size}`)", reply_markup=reply_markup, parse_mode="Markdown")
                no += 1
        return ConversationHandler.END


async def summarize_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

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
            await query.edit_message_text(f"📂 : {current_dir}. \n Gunakan perintah /buatfolder [nama folder] untuk membuat folder baru.", reply_markup=reply_markup)
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

async def handle_download_btn_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        command, hashed_path = query.data.split("|", 1)
        logger.info("hashed_path: %s", hashed_path)

        if hashed_path in context.user_data:
            path = context.user_data[hashed_path]
            # Misal: cek apakah folder masih ada
            if os.path.exists(path):
                file = os.path.isfile(path)

                file_name = os.path.basename(path)
                rep_path = path.split("/repository", 1)[1]
                parent_path = os.path.dirname(rep_path)
                short_path = os.path.join(parent_path, file_name)

                if not file:
                    # preparing for zip, but check for permissions
                    chat_id = query.message.chat_id
                    telegram_id = str(update.effective_user.id)
                    zip_permitted = is_permitted(telegram_id, path, "zip")
                    if not zip_permitted:
                        await query.message.reply_text(f"Mohon maaf, folder `{short_path}` tidak dapat diunduh. \nTidak ijin untuk melakukan zip 😞", parse_mode="Markdown")

                    # download folder here
                    await query.message.reply_text("Mohon tunggu\nSaya sedang membuat zip untuk folder tersebut...")
                    # cek the size of file
                    max_size_mb = 50
                    max_size_bytes = max_size_mb * 1024 * 1024
                    folder_size = get_folder_size_bytes(path)
                    if folder_size > max_size_bytes:
                        await query.message.reply_text("❌ Folder melebihi batas 50 MB. Batal dizip.")
                        return
                    
                    logger.info("rep_path: %s, parent_path %s", REPOSITORY_PATH, parent_path)
                    root_path = os.path.join(REPOSITORY_PATH, parent_path.lstrip("/"))
                    logger.info("parent path: %s, folder wil be zipped %s", root_path, path)
                    ziped_path = shutil.make_archive(os.path.join(root_path, file_name), "zip", path)
                    logger.info("zipped path %s", ziped_path)

                    # tolong dibatasi hingga 
                    await context.bot.send_document(
                        chat_id=chat_id,
                        document=open(ziped_path, "rb"),
                        caption=f"📦 `{short_path}`",
                        parse_mode="Markdown"
                    )
                    os.remove(ziped_path)
                else:
                    # send the file
                    chat_id = query.message.chat_id
                    await context.bot.send_document(
                        chat_id=chat_id, 
                        document=open(path, "rb"),
                        caption=f"📎 Berikut adalah dokumen yang kamu minta\n`{short_path}`).",
                        parse_mode="Markdown")
                    
                # await query.edit_message_text(f"📂 Kamu memilih folder:\n`{path}`", parse_mode="Markdown")
            else:
                await query.edit_message_text(f"⚠️ Folder tidak ditemukan:\n`{path}`", parse_mode="Markdown")
        else:
            await query.edit_message_text(f"⚠️ Folder sudah tidak ditemukan:\n`{path}`\n. Silahkan melakukan pencarian ulang.", parse_mode="Markdown")
    except Exception as e:
        await query.edit_message_text("❌ Terjadi kesalahan saat memproses tombol.")
        print("Error:", e)
    # todo: check before searching the file
    # args = context.args
    # if not args:
    #     await update.message.reply_text('Silakan balas dengan format /kirim-file nomor-file')
    # else:
    #     file_no = args[0]
    #     search_results = context.user_data['search_results']
    #     if file_no.isdigit():
    #         index = int(file_no) - 1
    #         if 0 <= index < len(search_results):
    #             path = search_results[index]
    #             filename = os.path.basename(path)
    #             # rep_path = path.split("/repository", 1)[1]
    #             # folder_path = os.path.dirname(rep_path)
    #             # filename_wpath = os.path.join(folder_path, filename)
    #             logger.info('attempting to send file on %s', path)
    #             try:
    #                 await update.message.reply_document(document=open(path, 'rb'))
    #             except FileNotFoundError:
    #                 await update.message.reply_text("File tidak ditemukan.")
    #         else:
    #             await update.message.reply_text(f"Ah, yang bener dong! Tolong masukan angka.")
    #     else:
    #         count_results = len(context.user_data['search_results'])
    #         await update.message.reply_text(f"Silakan balas dengan angka 1 sampai {count_results}.")

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Ok, terima kasih.')
    return ConversationHandler.END

async def create_folder_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # check current user
    telegram_id = str(update.effective_user.id)
    curr_user = get_user_logged_in(telegram_id)
    if curr_user is None:
        await update.message.reply_text("Maaf, kamu belum bisa mengakses data center sebelum melakukan verifikasi nomor HP")
        return
    # check current directory
    if "current_directory" not in context.user_data:
        await update.message.reply_text("Silahkan tentukan terlebih dahulu di mana kamu akan menyimpan folder-nya")
        return
    # check permission
    current_directory = context.user_data['current_directory']
    write_permitted = is_permitted(telegram_id, current_directory, "write")
    if not write_permitted:
        await update.message.reply_text("Mohon maaf, kamu tidak diijinkan untuk membuat folder")
        return

    await update.message.reply_text("Apa nama folder-nya?")
    return ASK_FOLDER_NAME

async def do_create_folder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    folder_name = update.message.text.strip()
    current_dir = context.user_data['current_directory']

    # os.makedirs(current_dir, exist_ok=True)
    folder_path = os.path.join(current_dir, folder_name)
    try:
        os.makedirs(folder_path)
        results = list_dir(current_dir)
        context.user_data['search_results'] = results['results']
        reply_markup = InlineKeyboardMarkup(results['keyboard'])
        # await query.edit_message_text(f"📂 : {current_dir}. \n Gunakan perintah /buatfolder [nama folder] untuk membuat folder baru.", reply_markup=reply_markup)
        await update.message.reply_text(f"✅ Folder '{folder_name}' berhasil dibuat", reply_markup=reply_markup)
    except FileExistsError:
        await update.message.reply_text(f"⚠️ Folder '{folder_name}' sudah ada.")
    except Exception as e:
        await update.message.reply_text(f"❌ Gagal membuat folder: {e}")

    return ConversationHandler.END

create_folder_handler = ConversationHandler(
    entry_points=[CommandHandler("buatfolder", create_folder_command)],
    states={
        ASK_FOLDER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, do_create_folder)],
    },
    fallbacks=[CommandHandler("batal", cancel_command)]
)