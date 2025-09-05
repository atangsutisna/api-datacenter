from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import SlotSet
import logging,sys,os,random,json

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)
logger = logging.getLogger(__name__)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class ActionRemoveData(Action):
    def __init__(self):
        from checkpermissions import is_permitted
        from myutils import list_dir,build_response,to_dict,simplified_path,get_ask_to_open_remove_or_download
        self.is_permitted = is_permitted
        self.list_dir = list_dir
        self.build_response = build_response
        self.to_dict = to_dict
        self.simplified_path = simplified_path
        self.get_ask_to_open_remove_or_download = get_ask_to_open_remove_or_download
        
    def name(self):
        return "action_remove_data"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: dict):
        logger.info("starting to run action_remove_data")
        file_no = tracker.get_slot("file_no_to_be_removed")
        current_path = tracker.get_slot("current_path")

        metadata = tracker.latest_message.get("metadata")
        fullname = metadata.get("fullname")
        telegram_id = metadata.get("telegram_id")

        logger.info("Got current path %s", current_path)
        chmod_permitted = self.is_permitted(telegram_id, current_path, "write")
        if chmod_permitted:
            # check file or folder?
            search_results = tracker.get_slot("search_results")
            user_files = json.loads(search_results)
            # logger.info("current user files %r", user_files)
            selected_path = user_files.get(file_no)
            file_exists = os.path.exists(selected_path)
            removed_path = self.simplified_path(selected_path)
            if selected_path and file_exists:
                is_file = os.path.isfile(selected_path)
                if is_file:         
                    # just remove the file    
                    os.remove(selected_path)
                else:
                    # remove the folder and it's childs
                    shutil.rmtree(selected_path)
                
                lspaths = self.list_dir(current_path)
                response = self.build_response(
                    opening_message=f"Data `{removed_path}` sudah dihapus",
                    ending_message=self.get_ask_to_open_remove_or_download(),
                    lspaths=lspaths
                )
                # prepare for response
                dispatcher.utter_message(text=response)
                lspaths_json = json.dumps(self.to_dict(lspaths))
                return [
                    SlotSet("search_results", lspaths_json), 
                    SlotSet("file_no", None),
                    SlotSet("file_no_to_be_removed", None),
                    SlotSet("current_path", current_path)
                ]
            else:
                # data tidak ditemukan
                lspaths = self.list_dir(current_path)
                response = self.build_response(
                    opening_message=f"Data `{removed_path}` nggak ketemu",
                    ending_message=self.get_ask_to_open_remove_or_download(),
                    lspaths=lspaths
                )
                # prepare for response
                dispatcher.utter_message(text=response)
                lspaths_json = json.dumps(self.to_dict(lspaths))
                return [
                    SlotSet("search_results", lspaths_json), 
                    SlotSet("file_no", None),
                    SlotSet("file_no_to_be_removed", None),
                    SlotSet("current_path", current_path)
                ]
        else:
            dispatcher.utter_message(text=f"Maaf, kamu nggak ada ijin menghapus")
            return [
                SlotSet("file_no", None),
                SlotSet("file_no_to_be_removed", None),
                SlotSet("current_path", current_path)
            ]