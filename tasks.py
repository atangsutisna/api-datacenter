from celery import Celery
import requests
from telegram import Bot
from dotenv import load_dotenv
import os
import asyncio
import logging
from myutils import compress_folder,compress_file,upload_to_filebin,shorten_url

load_dotenv()
app = Celery("hello", broker='redis://localhost:6379/0')
RASA_API_URL = "http://localhost:5005"

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
    # batasi besaran file, jangan sampai melebihi satu gb atau 500gb
    is_file = os.path.isfile(base_path)
    if is_file:
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
        long_url = upload_to_filebin(output_path)
        short_url = shorten_url(long_url)

        loop.run_until_complete(
            bot.send_message(
                chat_id=chat_id, 
                text=f"📎 Klik untuk mengunduh: [Download]({short_url})",
                parse_mode="Markdown"
            )
        )    
# async def send_document_async(bot: Bot, chat_id: int, output_path: str, caption: str):
#     """Fungsi pembantu async untuk mengirim dokumen."""
#     try:
#         with open(output_path, 'rb') as doc_file:
#             await bot.send_document(
#                 chat_id=chat_id, 
#                 document=doc_file,
#                 caption=caption,
#                 parse_mode="Markdown"
#             )
#         return True
#     except FileNotFoundError:
#         # Log error di sini
#         return False
#     except Exception as e:
#         # Log error Telegram/jaringan di sini
#         full_traceback = traceback.format_exc()
#         logger.error(
#             "Error: Gagal mengirim dokumen ke Telegram. Detail: %s\nStack Trace:\n%s", 
#             e, 
#             full_traceback
#         )
#         return False