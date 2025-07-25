# file yang didukung oleh script ini adalah pdf, txt, docx, html
from openai import OpenAI
import time, os
from dotenv import load_dotenv
import subprocess, os
from pathlib import Path

load_dotenv()
API_KEY = os.getenv('OPENAI_APIKEY')

def convert_to_pdf(input_path) -> str:
    input_path = Path(input_path)
    subprocess.run([
        "libreoffice",
        "--headless",
        "--convert-to", "pdf",
        "--outdir", str(input_path.parent),
        str(input_path)
    ])

    return os.path.join(input_path.parent, input_path.stem +".pdf") 

# Inisialisasi client
client = OpenAI(api_key=API_KEY)

# Upload file
# Untuk file excel, perlu diubah dulu ke pdf untuk setiap sheet-nya.
fullpath = convert_to_pdf("/home/kangatang/git/filegator/repository/atang/master-tabel.xlsx")
print(f"fullpath {fullpath}")
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
