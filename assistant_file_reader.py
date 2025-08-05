from openai import OpenAI
import time
import time, os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('OPENAI_APIKEY')

def read_file_with_file_search(
    api_key: str,
    file_path: str,
    prompt: str = "Tolong baca dan ringkas isi file ini.") -> str:
    client = OpenAI(api_key=api_key)

    # Upload file
    uploaded_file = client.files.create(
        file=open(file_path, "rb"),
        purpose="assistants"
    )

    # Buat Assistant dengan file_search (jika belum punya, kamu bisa reuse ID)
            # "Bacalah file ini dan ringkas isinya."
            # "Jika tidak dapat dibaca, jelaskan penyebabnya secara singkat, tanpa mengajukan pertanyaan."
    assistant = client.beta.assistants.create(
        name="File Reader",
        instructions=prompt,
        model="gpt-4-1106-preview",
        tools=[{"type": "file_search"}]
    )

    # Buat thread baru
    thread = client.beta.threads.create()

    # Kirim pesan ke thread dengan attachment
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=prompt,
        attachments=[
            {
                "file_id": uploaded_file.id,
                "tools": [{"type": "file_search"}]
            }
        ]
    )

    # Jalankan assistant
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )

    # Tunggu sampai proses selesai
    while True:
        run_status = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        if run_status.status == "completed":
            break
        elif run_status.status in ["failed", "cancelled"]:
            raise Exception(f"Run gagal: {run_status.status}")
        time.sleep(2)

    # Ambil hasilnya
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    for msg in messages.data[::-1]:
        if msg.role == "assistant":
            return msg.content[0].text.value

    return "Tidak ada jawaban dari Assistant."

selected_path = "/home/kangatang/git/filegator/repository/atang/master-tabel.pdf"
prompt=(
    "Tolong bacakan isi halaman 1 sampai 3 dari file ini."
    "Jika tidak dapat dibaca, jelaskan penyebabnya secara singkat, tanpa mengajukan pertanyaan."
)
result = read_file_with_file_search(
    api_key=API_KEY,
    file_path=selected_path,
    prompt=prompt
)