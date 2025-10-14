from celery import Celery
import requests
from telegram import Bot
from dotenv import load_dotenv
import os
import asyncio
import logging
from myutils import compress_folder,compress_file,upload_to_filebin,shorten_url,is_folder_less_than_1gb,is_folder_larger_than_2mb,estimate_upload_time,get_ext,is_file_smaller_than_100mb
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
    logger.info("starting to run zip with params %s", base_path)
    # disini kita bisa mengirimkan pesan,estimasi waktu yang diperlukan
    # batasi besaran file, jangan sampai melebihi satu gb atau 500gb
    if is_folder_less_than_1gb(base_path):
        is_file = os.path.isfile(base_path)
        if is_file:
            if is_folder_larger_than_2mb(base_path): # harusnya bukan folder, tapi cek ukuran filenya
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
                    text=f"📎 Klik untuk mengunduh: [Download]({short_url})",
                    parse_mode="Markdown"
                )
            )
        else:
            output_path = compress_folder(base_path)
            if is_folder_larger_than_2mb(output_path): # harusnya bukan folder, tapi cek ukuran filenya
                estimate_message = estimate_upload_time(output_path)
                loop.run_until_complete(
                    bot.send_message(
                        chat_id=chat_id, 
                        text=estimate_message,
                        parse_mode="Markdown"
                    )
                )

            long_url = upload_to_filebin(output_path)
            short_url = shorten_url(long_url)

            loop.run_until_complete(
                bot.send_message(
                    chat_id=chat_id, 
                    text=f"📎 Klik untuk mengunduh: [Download]({short_url})",
                    parse_mode="Markdown"
                )
            )
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
        else:
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
                text="Maaf, saya hanya bisa melayani file dibawah `100 MB`",
                parse_mode="MarkdownV2"
            )
        )
