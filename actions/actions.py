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
from datetime import datetime
from zoneinfo import ZoneInfo
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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

class ActionGreeting(Action):
    def name(self) -> Text:
        return "action_greeting"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        tz = datetime.now(ZoneInfo("Asia/Jakarta"))
        current_hour = tz.hour
        fullname = tracker.sender_id
        if fullname == "user":
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
                        "username": "atang gombal",
                        "fullname": "Atang Sutisna, Ir",
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
        return "action_list_workspace"
    
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
        else:
            # get telegram id 7272740693
            metadata = tracker.latest_message.get("metadata")
            fullname = metadata.get("fullname")
            telegram_id = metadata.get("telegram_id")
            
            curr_user = self.get_user_logged_in(telegram_id)
            accounts = curr_user['accounts']
            user_workspaces = []
            REPOSITORY_PATH = os.getenv('REPOSITORY_PATH')
            for account in accounts:
                homedir = account['homedir'].lstrip("/")
                fullpath = os.path.join(REPOSITORY_PATH, homedir)
                user_workspaces.append(fullpath)

            message = "Baik, ini *workspace kamu*:"
            no = 1
            # simplified workspace, use short path not fullpath
            for workspace in user_workspaces:
                message += f"\n{no}. `{workspace}` (`{format_size(get_folder_size_bytes(workspace))}`)"
                no += 1
            # message += "\n".join(f"{no+1}. `{workspace}` ({get_folder_size_bytes()})" for no, workspace in enumerate(user_workspaces))
            message += "\nSilahkan kamu bisa meng-ekplore dengan menekan button \"Buka Folder\""
            dispatcher.utter_message(
                text=message,
                custom={
                    "data": {
                        "teks": message,
                        "search_results": user_workspaces,
                        "reply_markup": {
                            "inline_keyboard": []
                        }
                    }
                }

            )

class ActionSapaNama(Action):
    def name(self) -> Text:
        return "action_simpan_nama"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        nama_user = tracker.get_slot("nama")
        print(f"[DEBUG] Nama user yang disimpan: {nama_user}")
        dispatcher.utter_message(text=f"Halo {nama_user}, senang bertemu kamu!")
        return []
    