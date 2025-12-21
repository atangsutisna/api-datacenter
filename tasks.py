from celery import Celery
import requests
from telegram import Bot
from dotenv import load_dotenv
import os
import asyncio
import logging
from myutils import *
from assistant_file_reader import read_file_with_file_search
from excelutils import export_to_pdf

load_dotenv()
app = Celery("hello", broker='redis://localhost:6379/0')
RASA_API_URL = "http://localhost:5005"
OPENAI_APIKEY = os.getenv('OPENAI_APIKEY')
bot = Bot(token=os.getenv("TOKEN"))

# Buat event loop global sekali saja
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)
logger = logging.getLogger(__name__)

@app.task
def hello():
    return "hello world"

@app.task
def add(x, y):
    """A simple task to add two numbers."""
    print(f"Executing task 'add' with arguments: {x}, {y}")
    return x + y

@app.task
def long_running_task(duration):
    """Simulates a task that takes a long time."""
    import time
    print(f"Starting long_running_task for {duration} seconds.")
    time.sleep(duration)
    print(f"Finished long_running_task.")
    return f"Task completed after {duration} seconds."

@app.task
def run_zip(sender_id):
    """Simulates a task that takes a long time."""
    import time

    duration = 10
    print(f"Starting zip for {duration} seconds.")
    loop.run_until_complete(bot.send_message(chat_id="7272740693", text="Mohon ditunggu, sepertinya proses ini memerlukan waktu sekitar 1 menit"))
    time.sleep(duration)
    print(f"Finished zip..")
    
    # Callback: Memanggil Rasa Event API
    payload = {
        "event": "bot",
        "text": "Zip process has been done",
        "metadata": {
            "utter_action": "utter_zip_done"
        } 
    }

    # Endpoint: POST /conversations/{sender_id}/tracker/events
    try:
        # response = requests.post(
        #     f"{RASA_API_URL}/conversations/{sender_id}/tracker/events",
        #     json=payload
        # )
        # response = requests.post(
        #     "http://localhost:5005/webhooks/rest/webhook",
        #     json={"sender": sender_id, "message": "check zip status"},
        #     timeout=5
        # )
        # response.raise_for_status()
        print("send to bot")
        loop.run_until_complete(bot.send_message(chat_id="7272740693", text="Selesai, bro.."))
        print("sent to bot")
        print(f"[{sender_id}] Notifikasi hasil berhasil dikirim melalui Rasa API.")
    except requests.exceptions.RequestException as e:
        print(f"[{sender_id}] GAGAL mengirim notifikasi ke Rasa: {e}")

@app.task
def do_zip(chat_id, base_path):
    import time

    logger.info("starting to run zip with params %s", base_path)
    # disini kita bisa mengirimkan pesan,estimasi waktu yang diperlukan
    # batasi besaran file, jangan sampai melebihi satu gb atau 500gb
    if is_folder_less_than_1gb(base_path):
        is_file = os.path.isfile(base_path)
        if is_file:
            if not is_file_smaller_than_100mb(base_path): # harusnya bukan folder, tapi cek ukuran filenya
                # estimate_time = estimate_zip_time(base_path)
                estimate_message = estimate_upload_time(base_path)
                loop.run_until_complete(
                    bot.send_message(
                        chat_id=chat_id, 
                        text=estimate_message,
                        parse_mode="Markdown"
                    )
                )

            output_path = compress_file(base_path)
            long_url = upload_to_filebin(output_path)
            short_url = shorten_url(long_url)

            loop.run_until_complete(
                bot.send_message(
                    chat_id=chat_id, 
                    text=f"📎 Terima kasih atas kesabaran Anda. File ZIP siap, unduh sekarang di: [Download]({short_url})",
                    parse_mode="Markdown"
                )
            )
        else:
            # est_zip_time = estimate_zip_time(base_path)
            output_path = compress_folder(base_path)
            if not is_file_smaller_than_100mb(output_path): # harusnya bukan folder, tapi cek ukuran filenya
                logger.info("attempting to calculate upload time estimation")
                estimate_message = estimate_upload_time(output_path)
                loop.run_until_complete(
                    bot.send_message(
                        chat_id=chat_id, 
                        text=estimate_message,
                        parse_mode="Markdown"
                    )
                )
            else:
                logger.info("Folder %s is less than 2mb", output_path)

            long_url = upload_to_filebin(output_path)
            short_url = shorten_url(long_url)

            loop.run_until_complete(
                bot.send_message(
                    chat_id=chat_id, 
                    text=f"📎 Terima kasih atas kesabaran Anda. File ZIP siap, unduh sekarang di: [Download]({short_url})",
                    parse_mode="Markdown"
                )
            )
            
            # just for testing
            # duration = 10
            # time.sleep(duration)
            # loop.run_until_complete(bot.send_message(chat_id=chat_id, text="Selesai, bro.."))

    else:
        loop.run_until_complete(
            bot.send_message(
                chat_id=chat_id, 
                text="Maaf, saya tidak dapat memproses file atau folder di atas 1GB",
                parse_mode="Markdown"
            )
        )

@app.task
def get_summarize(chat_id: str, selected_path: str):
    ext = get_ext(selected_path)
    supported_extension = {"pdf", "doc", "docx", "txt"}
    img_extensions = {"pdf", "doc", "docx", "txt"}
    msoffice_extensions = {"pdf","xls","xlsx","ppt","pptx"}
    
    logger.info(f"attempting to read file with ext {ext}")
    if is_file_smaller_than_100mb(selected_path):
        if ext in supported_extension:
            logger.info("attempting to send request to openai")
            prompt=(
                "Tolong bacakan isi halaman 1 sampai 3 dari file ini."
                "Jika tidak dapat dibaca, jelaskan penyebabnya secara singkat, tanpa mengajukan pertanyaan."
            )
            result = read_file_with_file_search(
                api_key=OPENAI_APIKEY,
                file_path=selected_path,
                prompt=prompt
            )
            # dispatcher.utter_message(text=result)
            logger.info("Got info summarize from openAI %s", result)
            loop.run_until_complete(
                bot.send_message(
                    chat_id=chat_id, 
                    text=result,
                    parse_mode="HTML"
                )
            )
        elif ext in msoffice_extensions:
            logger.info(f"attempting to convert {selected_path} to pdf")
            tmp_file_fullpath = export_to_pdf(selected_path)
            logger.info("attempting to ask to openai")
            # perlu optimasi
            result = read_file_with_file_search(
                api_key=OPENAI_APIKEY,
                file_path=tmp_file_fullpath
            )
            # dispatcher.utter_message(text=result)
            logger.info("Got info summarize from openAI %s", result)
            loop.run_until_complete(
                bot.send_message(
                    chat_id=chat_id, 
                    text=result,
                    parse_mode="HTML"
                )
            )
            os.remove(tmp_file_fullpath)            
        else:
            loop.run_until_complete(
                bot.send_message(
                    chat_id=chat_id, 
                    text="Mohon maaf, file ini tidak bisa saya baca karena formatnya bukan teks. Saya hanya menerima file dalam format teks.",
                    parse_mode="HTML"
                )
            )
    else:
        loop.run_until_complete(
            bot.send_message(
                chat_id=chat_id, 
                text="Maaf, saya hanya bisa melayani file dibawah `100 MB`",
                parse_mode="MarkdownV2"
            )
        )

# ini hanya untuk fiel download, tidak support untuk folder
@app.task
def generate_link_for_download(chat_id: str, selected_path: str):
    # import time
    logger.info("preparing link download for file %s", selected_path)
    # time.sleep(10)
    # is_file = os.path.isfile(selected_path)
    # short_url = "https://file-examples.com/wp-content/storage/2017/10/file-sample_150kB.pdf"
    # loop.run_until_complete(
    #     bot.send_message(
    #         chat_id=chat_id, 
    #         text=f"📎 Terima kasih atas kesabaran Anda. File ZIP siap, unduh sekarang di: [Download]({short_url})",
    #         parse_mode="Markdown"
    #     )
    # )
    file_name = os.path.basename(selected_path)
    logger.info("starting to upload %s to filebin to generate a link", selected_path)
    long_url = upload_to_filebin(selected_path)
    if long_url is None:
        loop.run_until_complete(
            bot.send_message(
                chat_id=chat_id, 
                text="Mohon maaf, gagal saat menyiapkan file. Silakan hubungi admin untuk mengetahui lebih lanjut. Terima kasih.",
                parse_mode="Markdown"
            )
        )
    else:
        short_url = shorten_url(long_url)
        loop.run_until_complete(
            bot.send_message(
                chat_id=chat_id, 
                text=f"📎 Terima kasih sudah menunggu. Silakan unduh di: [Download]({short_url})",
                parse_mode="Markdown"
            )
        )