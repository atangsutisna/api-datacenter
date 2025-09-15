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

class ActionPrepareRemove(Action):
    def __init__(self):
        from checkpermissions import is_permitted
        from myutils import to_be_list
        
        self.is_permitted = is_permitted
        self.to_be_list = to_be_list

    def name(self) -> Text:
        return "action_prepare_remove"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        logger.info("starting to prepare rm action...")
        metadata = tracker.latest_message.get("metadata")
        fullname = metadata.get("fullname")
        telegram_id = metadata.get("telegram_id")

        slot_value = tracker.get_slot("file_no_to_be_removed")
        delete_indexes = []
        if isinstance(slot_value, str):
            delete_indexes.extend(self.to_be_list(slot_value))
        elif isinstance(slot_value, list):
            for val in slot_value:
                delete_indexes.extend(self.to_be_list(val))
        
        logger.info("attempting to get path on line %s", delete_indexes)
        search_results = tracker.get_slot("search_results")

        # logger.info("attempting to load search results %s", search_results)
        user_files = json.loads(search_results)
        logger.info("attempting to get path on line %s", file_no)
        selected_path = user_files.get(file_no)

        has_permission = self.is_permitted(telegram_id, selected_path, "write")
        logger.info("Is telegram id %s has rm permission: %s", telegram_id, has_permission)
        if not has_permission:
            logger.info("user %s has no permission to remove", telegram_id)
            return [SlotSet("has_rm_permission", False)]
        
        logger.info("ok, user %s has permission to remove", telegram_id)
        return [SlotSet("has_rm_permission", True)]