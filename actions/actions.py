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
from datetime import datetime
from zoneinfo import ZoneInfo
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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
                message = f"Hai, selamat pagi *{fullname}*.\nAda yang bisa saya bantu?\nSaat ini, kamu punya dua akses folder utama:\n 1. atang\n 2. Spark \n"
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
                        "inline_keyboard": [
                            {"teks": "Cek Status", "callback_data": "/cek_status"},
                            {"teks": "Bantuan", "callback_data": "/bantuan"},
                        ]
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
            dispatcher.utter_message(text="😊 Tentu saja! ID kamu sudah terdaftar di dalam sistem.\nBaik, ada yang bisa saya bantu terkait data center?")

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

            message = "Baik, ini *workspace kamu*:\n"
            message += "\n".join(f"{no+1}. `{workspace}`" for no, workspace in enumerate(user_workspaces))
            message += "\nSilahkan kamu bisa meng-ekplore dengan menekan button \"Buka Folder\""
            dispatcher.utter_message(
                text=message,
                custom={
                "data": {
                    "teks": message,
                    "search_results": user_workspaces,
                    "reply_markup": {
                        "inline_keyboard": [
                            {"teks": "Buka Folder", "callback_data": "/open_folder"},
                        ]
                    }
                }
            }

            )
            # dispatcher.utter_message(text="😊 Saya akan menampilkan workspacemu segera!! Fitur ini sedang dalam pengembangan")
