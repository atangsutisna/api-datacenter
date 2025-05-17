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
from datetime import datetime
from zoneinfo import ZoneInfo

class ActionGreeting(Action):
    def name(self) -> Text:
        return "action_greeting"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        tz = datetime.now(ZoneInfo("Asia/Jakarta"))
        current_hour = tz.hour
        # telegram_id = tracker.sender_id
        # metadata = tracker.metadata
        # fullname = metadata.get("fullname") if metadata else None
        fullname = tracker.sender_id
        if 4 <= current_hour < 10:
            message = f"Hai {fullname}, selamat pagi"
        elif 10 <= current_hour < 15:
            message = f"Hai {fullname}, selamat siang"
        elif 15 <= current_hour < 18:
            message = f"Hai {fullname}, selamat sore"
        else:
            message = f"Hai {fullname}, selamat malam"
        dispatcher.utter_message(text=message)
        return []
