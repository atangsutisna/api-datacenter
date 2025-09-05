from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

class ActionNotifyProcessing(Action):
    def name(self): return "action_notify_processing"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(
            text="Mohon ditunggu..."
        )
        return []
    # async def run(self, dispatcher, tracker, domain):
    #     dispatcher.utter_message(
    #         text="Mohon ditunggu..."
    #     )
    #     # langsung panggil action berikutnya
    #     # return [FollowupAction("action_to_open_data")]
    #     return []