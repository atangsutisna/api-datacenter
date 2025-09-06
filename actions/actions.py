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
from rasa_sdk.events import AllSlotsReset, ActiveLoop, FollowupAction
from datetime import datetime
from zoneinfo import ZoneInfo
import sys
import os
import random
import logging
import json
import shutil
import traceback
from pathlib import Path
# from rasa_sdk.events import 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
# logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# REPOSITORY_PATH = os.getenv('REPOSITORY_PATH')
# OPENAI_APIKEY = os.getenv('OPENAI_APIKEY')

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

def get_ask_to_open_remove_or_download() -> str:
    additional_responses = [
        "Ada hal lain yang perlu saya bantu dengan data ini? Misalnya, Kamu ingin menghapus, mengunduh, atau membuka folder lain?",
        "Perlu bantuan lanjutan? Saya bisa bantu hapus, unduh, atau masuk ke folder lain.",
        "Apa lagi yang bisa saya lakukan untuk Kamu? Ada pilihan hapus, unduh, atau jelajahi folder.",
        "Apakah ada tindakan lain yang ingin Kamu lakukan? Misalnya, menghapus, mengunduh, atau membuka folder?",
        "Sudah selesai dengan ini, atau ada lagi yang bisa saya bantu? Mungkin menghapus, mengunduh, atau membuka folder lain?"
    ]
    return random.choice(additional_responses)

def get_ext(path: str) -> str:
    fullpath = Path(path)
    return fullpath.suffix.lstrip(".")

class ActionCheckPermissionRemoveData(Action):
    def __init__(self):
        from checkpermissions import is_permitted
        self.is_permitted = is_permitted

    def name(self):
        return "action_check_permission_remove_data"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: dict):
        logger.info("starting to check permission")
        file_no = tracker.get_slot("file_no")
        # hapus, terus tampilkan list datanya
        # hapus dulu datanya, 
        chmod_permitted = is_permitted(telegram_id, path, "write")
        if chmod_permitted:
            return [
                SlotSet("remove_permitted", True)
            ]
        else:
            dispatcher.utter_message(text=f"Mohon maaf, kamu nggak punya akses untuk menghapus data")
            return [
                SlotSet("remove_permitted", False)
            ]

class ActionRemoveCurrentPath(Action):
    def __init__(self):
        from checkpermissions import is_permitted
        from myutils import list_dir, build_response, to_dict, get_root_path, get_workspaces
        self.is_permitted = is_permitted
        self.list_dir = list_dir
        self.build_response = build_response
        self.to_dict = to_dict
        self.get_root_path = get_root_path
        self.get_workspaces = get_workspaces
    
    def name(self):
        return "action_to_remove_current_path"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: dict):
        metadata = tracker.latest_message.get("metadata")
        telegram_id = metadata.get("telegram_id")
        current_path = tracker.get_slot("current_path")
        root_path = self.get_root_path(current_path)
        simple_path = simplified_path(current_path)

        logger.info("Got current path %s", current_path)
        chmod_permitted = self.is_permitted(telegram_id, current_path, "write")
        if not chmod_permitted:
            dispatcher.utter_message(text=f"Maaf, kamu tidak dijinkan untuk menghapus data")
            return []
        
        user_workspaces = self.get_workspaces(telegram_id)
        if current_path in user_workspaces:
            dispatcher.utter_message(text=f"Folder utama (`{simple_path}`) tidak diijinkan dihapus")
            return []

        logger.info("attempting to remove current path %s", current_path)
        # todo: jangan sampai menghapus root path -nya user
        shutil.rmtree(current_path)

        # re-list lagi 
        lspaths = self.list_dir(root_path)
        response = self.build_response(
            opening_message=f"Data sudah `{simple_path}` dihapus",
            ending_message=get_ask_to_open_remove_or_download(),
            lspaths=lspaths
        )
        # prepare for response
        dispatcher.utter_message(text=response)
        lspaths_json = json.dumps(self.to_dict(lspaths))
        return [
            SlotSet("search_results", lspaths_json), 
        ]

class ValidateCreateFolderForm(FormValidationAction):
    def __init__(self):
        from checkpermissions import is_permitted
        self.is_permitted = is_permitted

    def name(self) -> Text:
        """ 
        Nama validasi harus seperti ini 'validate_<form_name>'
        AI menyarankan untuk membuat nama seperti ini 'action_validate_<form_name>'. Saran seperti itu tidak bekerja.
        Gunakan pendekatan seperti ini: 'validate_<form_name>'
        """ 
        return "validate_create_folder_form"
    
    def validate_folder_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict
    ) -> Dict[Text, Any]:
        """ 
        validate folder name 
        - current path is exists
        - ensure folder name doest not exists
        """
        logger.info("attempting to validate folder name")
        current_path = tracker.get_slot("current_path")
        
        metadata = tracker.latest_message.get("metadata")
        fullname = metadata.get("fullname")
        telegram_id = metadata.get("telegram_id")
        # telegram_id = "7272740693"
        write_permitted = self.is_permitted(telegram_id, current_path, "write")
        logger.info("Is telegram id %s has write permission: %s", telegram_id, write_permitted)
        if write_permitted is False:
            dispatcher.utter_message(response="utter_permission_denied_create_folder")
            return {
                "folder_name": None, 
                "creation_permitted": False,
                "requested_slot": None
            }

        proposed_folder_path = os.path.join(current_path, slot_value)
        if os.path.exists(proposed_folder_path):
            logger.info("Failed to create folder, %s exists", slot_value)
            dispatcher.utter_message(response="utter_folder_exists")
            return {"folder_name": None, "creation_permitted": True}
        else:
            logger.info("Folder name is valid")
            return {"folder_name": slot_value, "creation_permitted": True}