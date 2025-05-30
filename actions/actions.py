# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import SlotSet
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.events import AllSlotsReset, ActiveLoop
from datetime import datetime
from zoneinfo import ZoneInfo
import sys
import os
import random
import logging
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
# logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

def get_range_list(dictionary):
    if not dictionary:
        return "No data"
    min_key = min(int(k) for k in dictionary.keys())
    max_key = max(int(k) for k in dictionary.keys())
    return f"{min_key}..{max_key}"

def get_file_size_bytes(file_path):
    return os.path.getsize(file_path)

def get_folder_size_bytes(folder_path):
    total_size = 0
    for dirpath, _, filenames in os.walk(folder_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.isfile(fp):
                total_size += os.path.getsize(fp)
    return total_size    

def format_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024**2:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024**3:
        return f"{size_bytes / 1024**2:.2f} MB"
    else:
        return f"{size_bytes / 1024**3:.2f} GB"

def simplified_path(original_path: str) -> str:
    folder_name = os.path.basename(original_path)
    repository_path = original_path.split("/repository", 1)[1]
    
    parent_path = os.path.dirname(repository_path)
    return os.path.join(parent_path, folder_name)

class ActionGreeting(Action):
    def name(self) -> Text:
        return "action_greeting"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        tz = datetime.now(ZoneInfo("Asia/Jakarta"))
        current_hour = tz.hour
        sender_id = tracker.sender_id
        if sender_id == "user":
            # hallo biasa.
            if 4 <= current_hour < 10:
                message = f"Hai, selamat pagi. Ada yang bisa saya bantu?"
            elif 10 <= current_hour < 15:
                message = f"Hai, selamat siang. Ada yang bisa saya bantu?"
            elif 15 <= current_hour < 18:
                message = f"Hai, selamat sore. Ada yang bisa saya bantu?"
            else:
                message = f"Hai, selamat malam. Ada yang bisa saya bantu?"
        else:
            metadata = tracker.latest_message.get("metadata")
            telegram_id = metadata.get("telegram_id")
            fullname = metadata.get("fullname")
            if 4 <= current_hour < 10:
                message = f"Hai, selamat pagi *{fullname}*"
            elif 10 <= current_hour < 15:
                message = f"Hai {fullname}, selamat siang. Ada yang bisa saya bantu?"
            elif 15 <= current_hour < 18:
                message = f"Hai {fullname}, selamat sore. Ada yang bisa saya bantu?"
            else:
                message = f"Hai {fullname}, selamat malam. Ada yang bisa saya bantu?"
        
        dispatcher.utter_message(
            text=message,
            custom={
                "data": {
                    "username": "atang gombal",
                    "fullname": "Atang Sutisna, Ir",
                    "teks": "Silahkan pilih salah satu opsi:",
                    "reply_markup": {
                        "inline_keyboard": []
                    }
                }
            }
        )
        return []

class ActionGuessingName(Action):
    def name(self) -> Text:
        return "action_guessing_name"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        fullname = tracker.sender_id

        metadata = tracker.latest_message.get("metadata")
        telegram_id = metadata.get("telegram_id")
        if fullname == "user":
            # belum login
            dispatcher.utter_message(text="""
            Maaf, saya belum mengenal kamu.
            Silahkan verifikasi nomor HP kamu dulu.
            """)
        else:
            dispatcher.utter_message(
                text="😊 Tentu saja! ID kamu sudah terdaftar di dalam sistem.\nBaik, ada yang bisa saya bantu terkait data center?",
                custom={
                    "data": {
                        "username": telegram_id,
                        "fullname": fullname,
                        "teks": "Silahkan pilih salah satu opsi:",
                        "reply_markup": {
                            "inline_keyboard": []
                        }
                    }
                }
            )

class ActionListWorkspace(Action):
    def __init__(self):
        from userloggedin import get_user_logged_in
        self.get_user_logged_in = get_user_logged_in

    def name(self) -> Text:
        return "action_show_data"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        fullname = tracker.sender_id
        if fullname == "user":
            # belum login
            dispatcher.utter_message(text="""
            Maaf, saya belum mengenal kamu.
            Silahkan verifikasi nomor HP kamu dulu.
            """)

            return []
        else:
            # get telegram id 7272740693
            metadata = tracker.latest_message.get("metadata")
            fullname = metadata.get("fullname")
            telegram_id = metadata.get("telegram_id")
            
            # todo: jika user hanya punya satu folder, tampilkan saja langsung isinya
            curr_user = self.get_user_logged_in(telegram_id)
            accounts = curr_user['accounts']
            user_workspaces = []
            REPOSITORY_PATH = os.getenv('REPOSITORY_PATH')
            if len(accounts) > 1:
                for account in accounts:
                    homedir = account['homedir'].lstrip("/")
                    fullpath = os.path.join(REPOSITORY_PATH, homedir)
                    user_workspaces.append(fullpath)
            else:
                dirname = accounts[0]['homedir'].lstrip("/")
                logger.info("attempting to list all data in %s", dirname)
                home_path = os.path.join(REPOSITORY_PATH, dirname)
                list_dir = os.listdir(home_path)
                for dir in list_dir:
                    child_path = os.path.join(home_path, dir)
                    user_workspaces.append(child_path)

            opening_messages = [
                "Baik, ini semua data yang kamu miliki:",
                "Ini daftar data yang kamu miliki:",
                "Kamu memiliki beberapa data yang tersimpan. Ini daftarnya:"
            ]
            message = random.choice(opening_messages)
            no = 1
            search_results = {}
            for path in user_workspaces:
                file = os.path.isfile(path)
                simple_path = simplified_path(path)
                if not file:
                    message += f"\n{no}. `{simple_path}` (`{format_size(get_folder_size_bytes(path))}`)"
                else:
                    message += f"\n{no}. `{simple_path}` (`{format_size(get_file_size_bytes(path))}`)"
                search_results[no] = path
                no += 1

            message += "\nBila kamu mau membuka, menghapus, atau mendownload, sebutkan saja angkanya."
            dispatcher.utter_message(
                text=message
            )

            search_results_json = json.dumps(search_results)
            return [
                SlotSet("search_results", search_results_json)
            ]
    
class ActionAccessData(Action):
    def name(self):
        return "action_to_open_data"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: dict):
        logger.info("starting to run access data")
        file_no = tracker.get_slot("file_no")
        logger.info("Get file no from slot %s", file_no)
        search_results = tracker.get_slot("search_results")
        # dispatcher.utter_message(text=f"Kamu memilih file no {file_no}")
        # return []
        if search_results:
            logger.info("attempting to load search results %s", search_results)
            user_files = json.loads(search_results)
            selected_path = user_files.get(file_no)
            if selected_path:
                is_file = os.path.isfile(selected_path)
                if is_file:
                    # open the file using openai
                    dispatcher.utter_message(text="Mohon ditunggu, saya sedang membuat rangkuman file tersebut")
                    return []
                else:
                    # list all child of the path
                    user_workspaces = []
                    simple_root_path = simplified_path(selected_path)
                    list_dir = os.listdir(selected_path)
                    if not list_dir:
                        messages = [
                            f"Folder ini kosong. Tidak ada file atau folder di dalam folder `{simple_root_path}`",
                            f"Saya sudah membuka folder `{simple_root_path}`, tapi sepertinya tidak ada isinya",
                            f"Folder `{simple_root_path}` saat ini kosong. Tidak ada data yang bisa saya tampilkan"
                        ]
                        message = random.choice(messages)
                        dispatcher.utter_message(text=message)
                        return []
                    
                    for dir in list_dir:
                        child_path = os.path.join(selected_path, dir)
                        user_workspaces.append(child_path)

                    # format user workspaces
                    opening_messages = [
                        f"Baik, ini isi dari folder *{simple_root_path}*:",
                        f"Kamu sekarang berada di dalam folder *{simple_root_path}*. Ini semua yang ada di dalamnya:"
                    ]
                    message = random.choice(opening_messages)
                    no = 1
                    search_results = {}
                    for path in user_workspaces:
                        file = os.path.isfile(path)
                        simple_path = simplified_path(path)
                        if not file:
                            message += f"\n{no}. `{simple_path}` (`{format_size(get_folder_size_bytes(path))}`)"
                        else:
                            message += f"\n{no}. `{simple_path}` (`{format_size(get_file_size_bytes(path))}`)"
                        search_results[no] = path
                        no += 1

                # message += "\nData mana yang kamu inginkan? sebutkan angkanya"
                message += "\nAda yang perlu saya bantu lagi? misal menghapus, mendownload, atau membuka folder. sebutkan saja angkanya"
                dispatcher.utter_message(text=message)

                search_results_json = json.dumps(search_results)
                return [
                    SlotSet("search_results", search_results_json), 
                    SlotSet("file_no", None),
                    ActiveLoop(None)
                ]
                # return []
            else:
                range_list = get_range_list(user_files)
                max_no = max(int(k) for k in user_files.keys())
                messages = [
                    f"Hmm, nomor {file_no} di luar rentang data yang saya miliki 🤔. Saya punya data {range_list}. Apakah ada nomor lain yang kamu maksud?",
                    f"Maaf, saya tidak bisa menemukan data dengan nomor {file_no}. Data yang ada hanya sampai nomor {max_no}. Apakah ada nomor lain yang kamu maksud?",
                    f"Saya tidak menemukan data di posisi ke-{file_no}. Daftar data kamu berakhir di nomor {max_no}. Mungkin kamu ingin melihat data lain?"
                ]
                response = random.choice(messages)
                dispatcher.utter_message(text=response)
                return []
        else:
            dispatcher.utter_message(text=f"Data nomor {file_no} tidak ditemukan")
            return []

class ValidateFileSelectionForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_file_selection_form"

    async def validate_file_no(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        logger.info("validate file no %s", slot_value)
        search_results = tracker.get_slot("search_results")
        user_files = json.loads(search_results)
        if slot_value in user_files:
            selected_path = user_files.get(slot_value)
            return {"file_no": slot_value}
        else:
            return {"file_no": None}