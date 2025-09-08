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
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class ActionPerformDownload(Action):
    def __init__(self):
        from userloggedin import get_user_logged_in
        from checkpermissions import is_permitted
        from myutils import get_root_path, list_dir, to_dict, build_response,simplified_path,upload_to_filebin,shorten_url

        self.is_permitted = is_permitted
        self.get_root_path = get_root_path
        self.list_dir = list_dir
        self.to_dict = to_dict
        self.build_response = build_response
        self.get_user_logged_in = get_user_logged_in
        self.simplified_path = simplified_path
        self.upload_to_filebin = upload_to_filebin
        self.shorten_url = shorten_url

    def name(self):
        return "action_perform_download"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: dict):
        file_no = tracker.get_slot("file_no")
        logger.info("attempting to send file no %s", file_no)
        search_results = tracker.get_slot("search_results")
        # TODO: check download
        if search_results:
            user_files = json.loads(search_results)
            selected_path = user_files.get(file_no)
            # check permission
            logger.info("Got the file on path %s", selected_path)
            metadata = tracker.latest_message.get("metadata")
            fullname = metadata.get("fullname")
            telegram_id = metadata.get("telegram_id")
            download_permitted = self.is_permitted(telegram_id, selected_path, "download")
            logger.info("Is telegram id %s has write permission: %s", telegram_id, download_permitted)
            if download_permitted is False:
                dispatcher.utter_message("Maaf, kamu tidak diijinkan untuk mendownload file disini.")
                return [
                    SlotSet("file_no", None)
                ]

            is_file = os.path.isfile(selected_path)
            if is_file:
                # preparing for download
                # todo: create zip file or a link
                simple_root_path = self.simplified_path(selected_path)
                file_name = os.path.basename(selected_path)

                logger.info("starting to upload %s to filebin to generate a link", selected_path)
                long_url = self.upload_to_filebin(selected_path)
                if long_url is None:
                    dispatcher.utter_message(text="Mohon maaf, ada kendala saat menyipkan file. Silakan hubungi admin untuk mengetahui lebih lanjut. Terima kasih.")
                else:
                    short_url = self.shorten_url(long_url)
                    dispatcher.utter_message(
                        text="Baik, mohon ditunggu...",
                        attachment={
                            "type": "file",
                            "payload": {
                                "url": short_url,
                                "title": "Download",
                                "name": file_name
                            }
                        }
                    )
            else:
                # create file attachment
                # todo: create zip file for download
                dispatcher.utter_message(text="Saya sedang menyiapkan file download untuk kamu")
        else:
            dispatcher.utter_message(text="Saya tidak menemukan data tersebut")

        return [
            SlotSet("file_no", None)
        ]