from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

class ActionGetCurrentPath(Action):
    def __init__(self):
        from myutils import simplified_path

        self.simplified_path = simplified_path

    def name(self) -> Text:
        return "action_get_current_path"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        fullname = tracker.sender_id

        metadata = tracker.latest_message.get("metadata")
        telegram_id = metadata.get("telegram_id")
        if fullname == "user":
            # belum login
            dispatcher.utter_message(text="""
            Maaf, saya belum mengenal kamu.
            Silahkan verifikasi nomor HP kamu dulu.
            """)
        else:
            current_path = tracker.get_slot("current_path")
            if current_path is None:
                dispatcher.utter_message(
                    text=f"Kamu sedang berada di beranda",
                )
            else:                
                simplified_current_path = self.simplified_path(current_path)
                dispatcher.utter_message(
                    text=f"Path saat ini: {simplified_current_path}",
                    custom={
                        "data": {
                            "current_path": simplified_current_path,
                            "full_current_path": current_path
                        }
                    }
                )