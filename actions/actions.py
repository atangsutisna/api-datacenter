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

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
# logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

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
        if current_path is None:
            return [
                SlotSet("folder_name", None)
            ]
        # metadata = tracker.latest_message.get("metadata")
        # fullname = metadata.get("fullname")
        # telegram_id = metadata.get("telegram_id")
        # # telegram_id = "7272740693"
        # write_permitted = self.is_permitted(telegram_id, current_path, "write")
        # logger.info("Is telegram id %s has write permission: %s", telegram_id, write_permitted)
        # if write_permitted is False:
        #     dispatcher.utter_message(response="utter_permission_denied_create_folder")
        #     return {
        #         "folder_name": None, 
        #         "creation_permitted": False,
        #         "requested_slot": None
        #     }

        # proposed_folder_path = os.path.join(current_path, slot_value)
        # if os.path.exists(proposed_folder_path):
        #     logger.info("Failed to create folder, %s exists", slot_value)
        #     dispatcher.utter_message(response="utter_folder_exists")
        #     return {"folder_name": None, "creation_permitted": True}
        # else:
        #     logger.info("Folder name is valid")
        #     return {"folder_name": slot_value, "creation_permitted": True}