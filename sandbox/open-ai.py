import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('OPENAI_APIKEY')

client = OpenAI(
    api_key=API_KEY
)

messages = [
    {"role": "system", "content": "You are a kind helpful assistant."}
]
while True:
    message = input("User: ")
    if message:
        messages.append(
            {"role": "user", "content": message}
        )
        chat = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )

    reply = chat.choices[0].message.content
    print(f"ChatGPT: {reply}")
    messages.append({"role": "assistant", "content": reply})

# print("Tahun beres...")
# response = client.responses.create(
#     model="gpt-4o",
#     instructions="You are a coding assistant that talks like a pirate.",
#     input="How do I check if a Python object is an instance of a class?",
# )

# print(response.output_text)