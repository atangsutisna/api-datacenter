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

class ActionPrepareRemove(Action):
    def __init__(self):
        from checkpermissions import is_permitted
        from myutils import to_be_list
        
        self.is_permitted = is_permitted
        self.to_be_list = to_be_list

    def name(self) -> Text:
        return "action_confirm_move_file"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        logger.info("starting to prepare move action...")

        metadata = tracker.latest_message.get("metadata")
        fullname = metadata.get("fullname")
        telegram_id = metadata.get("telegram_id")

        file_no = tracker.get_slot("source_file_no")
        search_results = tracker.get_slot("search_results")

        user_files = json.loads(search_results)
        # has_permission = True
        # for file_no in delete_indexes:
        #     logger.info("attempting to get path on line %s", file_no)
        #     selected_path = user_files.get(file_no)
        #     if selected_path:
        #         has_permission = has_permission and self.is_permitted(telegram_id, selected_path, "write")
        #     else:
        #         logger.info("Failed to find path on line %s", file_no)
    
        # logger.info("Is telegram id %s has rm permission: %s", telegram_id, has_permission)
        # if not has_permission:
        #     logger.info("user %s has no permission to remove", telegram_id)
        #     return [SlotSet("has_rm_permission", False)]
        
        # logger.info("ok, user %s has permission to remove", telegram_id)

        selected_path = user_files.get(file_no)
        logger.info("attempting to move file on path %s", selected_path)

        write_permitted = self.is_permitted(telegram_id, selected_path, "write")
        logger.info("Is telegram id %s has write permission: %s", telegram_id, write_permitted)
        if write_permitted is False:
            dispatcher.utter_message("Maaf, kamu tidak diijinkan untuk memindahkan file atau folder")
            return [
                SlotSet("source_path", None),
                SlotSet("source_file_no", None)
            ]            

        dispatcher.utter_message(text=f"Baik, saya akan pindahkan file nomor ini: {file_no}")
        return [
            SlotSet("source_path", selected_path),
            SlotSet("source_file_no", None)
        ]