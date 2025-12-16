from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

class ActionGuessingName(Action):
    def name(self) -> Text:
        return "action_guessing_name"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        fullname = tracker.sender_id

        metadata = tracker.latest_message.get("metadata")
        telegram_id = metadata.get("telegram_id")
        if fullname == "user":
            # belum login
            dispatcher.utter_message(text="Maaf, saya belum mengenal kamu. Silahkan verifikasi nomor HP kamu dulu")
        else:
            dispatcher.utter_message(
                text="😊 Tentu saja! ID kamu sudah terdaftar di dalam sistem.\nBaik, ada yang bisa saya bantu terkait data center?",
                custom={
                    "data": {
                        "username": telegram_id,
                        "fullname": fullname,
                        "teks": "Silahkan pilih salah satu opsi:",
                        "reply_markup": {
                            "inline_keyboard": []
                        }
                    }
                }
            )