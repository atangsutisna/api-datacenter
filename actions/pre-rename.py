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


class ActionPrepareRename(Action):
    def __init__(self):
        from checkpermissions import is_permitted

        self.is_permitted = is_permitted

    def name(self) -> Text:
        return "action_prepare_rename"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        metadata = tracker.latest_message.get("metadata")
        fullname = metadata.get("fullname")
        telegram_id = metadata.get("telegram_id")

        file_no = tracker.get_slot("file_no")
        search_results = tracker.get_slot("search_results")

        # logger.info("attempting to load search results %s", search_results)
        user_files = json.loads(search_results)
        selected_path = user_files.get(file_no)

        has_permission = self.is_permitted(telegram_id, selected_path, "write")
        logger.info("Is telegram id %s has rename permission: %s", telegram_id, has_permission)
        if not has_permission:
            logger.info("user %s has no permission to rename", telegram_id)
            return [SlotSet("has_rename_permission", False)]
        
        logger.info("ok, user %s has permission to rename", telegram_id)
        return [SlotSet("has_rename_permission", True)]