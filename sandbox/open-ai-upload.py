# file yang didukung oleh script ini adalah pdf, txt, docx, html
from openai import OpenAI
import time, os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('OPENAI_APIKEY')

# Inisialisasi client
client = OpenAI(api_key=API_KEY)

# Upload file
fullpath = "/home/kangatang/git/filegator/repository/atang/shu-pinjaman.pdf"
file = client.files.create(
    file=open(fullpath, "rb"),
    purpose="assistants"
)
print("File ID:", file.id)

# Buat assistant
assistant = client.beta.assistants.create(
    name="File Reader",
    instructions="Bantu baca dan ringkas file.",
    model="gpt-4-1106-preview",
    tools=[{"type": "file_search"}]
)

# Buat thread
thread = client.beta.threads.create()

# Tambahkan pesan dan file
client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="Tolong ringkas file ini.",
    attachments=[
        {
            "file_id": file.id,
            "tools": [{"type": "file_search"}]
        }
    ]
)

# Jalankan
run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id
)

# Tunggu sampai selesai
print("Processing...")
while True:
    run_status = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
    if run_status.status == "completed":
        break
    elif run_status.status in ["failed", "cancelled"]:
        raise Exception(f"Run error: {run_status.status}")
    time.sleep(2)

# Ambil hasilnya
messages = client.beta.threads.messages.list(thread_id=thread.id)
for msg in messages.data[::-1]:
    if msg.role == "assistant":
        print("\nJawaban:")
        print(msg.content[0].text.value)
        break
