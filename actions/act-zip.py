from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import SlotSet
import logging,sys,os,random,json
import traceback

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)
logger = logging.getLogger(__name__)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class ActionZip(Action):
    def __init__(self):
        from checkpermissions import is_permitted
        from myutils import get_root_path,list_dir,to_dict,build_response,get_ask_to_open_remove_or_download,simplified_path,compress_folder,compress_file

        self.is_permitted = is_permitted
        self.get_root_path = get_root_path
        self.list_dir = list_dir
        self.to_dict = to_dict
        self.build_response = build_response
        self.get_ask_to_open_remove_or_download = get_ask_to_open_remove_or_download
        self.simplified_path = simplified_path,
        self.compress_folder = compress_folder
        self.compress_file = compress_file

    def name(self):
        return "action_zip"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: dict):
        logger.info("action zip called...")

        file_no = tracker.get_slot("file_no")
        logger.info("attempting to zip folder number %s", file_no)
        search_results = tracker.get_slot("search_results")

        if search_results:
            user_files = json.loads(search_results)
            selected_path = user_files.get(file_no)
            # check permission
            logger.info("Got the file on path %s", selected_path)
            dispatcher.utter_message(text="Saya sedang menyiapkan file download untuk kamu")
        else:
            dispatcher.utter_message(text="Saya tidak menemukan data tersebut")

        return [
            SlotSet("file_no", None)
        ]