from celery import Celery
import requests
from telegram import Bot
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()
app = Celery("hello", broker='redis://localhost:6379/0')
RASA_API_URL = "http://localhost:5005"

bot = Bot(token=os.getenv("TOKEN"))

# Buat event loop global sekali saja
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

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

# print("start")
# asyncio.run(bot.send_message(chat_id="7272740693", text="Selesai, bro.."))
# print("finish")