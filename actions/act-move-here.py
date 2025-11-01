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

class ActionMoveHere(Action):
    def __init__(self):
        from checkpermissions import is_permitted
        from myutils import to_be_list,move_item
        
        self.is_permitted = is_permitted
        self.to_be_list = to_be_list
        self.move_item = move_item

    def name(self) -> Text:
        return "action_move_here"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        logger.info("starting to move action...")
        metadata = tracker.latest_message.get("metadata")
        fullname = metadata.get("fullname")
        telegram_id = metadata.get("telegram_id")

        source_path = tracker.get_slot("source_path")
        if source_path is None:
            dispatcher.utter_message(text=f"Kamu belum memilih file atau folder.")
            return []
        else:
            current_path = tracker.get_slot("current_path")

            logger.info("attempting to move %s to %s", source_path, current_path)

            response = self.move_item(source_path, current_path)
            dispatcher.utter_message(response)
            
            return [
                SlotSet("source_path", None),
                SlotSet("source_file_no", None)
            ]