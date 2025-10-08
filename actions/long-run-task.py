from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)
logger = logging.getLogger(__name__)

class ActionLongRunTask(Action):
    def __init__(self):
        from tasks import run_zip
        
        self.run_zip = run_zip

    def name(self): return "action_long_run_task"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        sender_id = tracker.sender_id
        logger.info("long running task action is called. The sender id is %s", sender_id)
        dispatcher.utter_message(
            text="Run long running task..."
        )

        logger.info("starting to run long process...")

        metadata = tracker.latest_message.get("metadata")
        chat_id = metadata.get("chat_id")
        logger.info("send delay with chat_id %s", chat_id)
        self.run_zip.delay(chat_id)

        return []
    # async def run(self, dispatcher, tracker, domain):
    #     dispatcher.utter_message(
    #         text="Mohon ditunggu..."
    #     )
    #     # langsung panggil action berikutnya
    #     # return [FollowupAction("action_to_open_data")]
    #     return []