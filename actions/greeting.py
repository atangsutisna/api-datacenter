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
        sender_id = tracker.sender_id
        if sender_id == "user":
            # hallo biasa.
            if 4 <= current_hour < 10:
                message = f"Hai, selamat pagi. Ada yang bisa saya bantu?"
            elif 10 <= current_hour < 15:
                message = f"Hai, selamat siang. Ada yang bisa saya bantu?"
            elif 15 <= current_hour < 18:
                message = f"Hai, selamat sore. Ada yang bisa saya bantu?"
            else:
                message = f"Hai, selamat malam. Ada yang bisa saya bantu?"
        else:
            metadata = tracker.latest_message.get("metadata")
            telegram_id = metadata.get("telegram_id")
            fullname = metadata.get("fullname")
            if 4 <= current_hour < 10:
                message = f"Hai, selamat pagi *{fullname}*. Ada yang bisa saya bantu?"
            elif 10 <= current_hour < 15:
                message = f"Hai {fullname}, selamat siang. Ada yang bisa saya bantu?"
            elif 15 <= current_hour < 18:
                message = f"Hai {fullname}, selamat sore. Ada yang bisa saya bantu?"
            else:
                message = f"Hai {fullname}, selamat malam. Ada yang bisa saya bantu?"
        
        dispatcher.utter_message(
            text=message
        )
        return []