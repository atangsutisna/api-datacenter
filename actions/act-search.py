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

class ActionPerformSearch(Action):
    def __init__(self):
        from userloggedin import get_user_logged_in
        from checkpermissions import is_permitted
        from myutils import get_root_path, list_dir, to_dict, build_response,get_ask_to_open_remove_or_download

        self.is_permitted = is_permitted
        self.get_root_path = get_root_path
        self.list_dir = list_dir
        self.to_dict = to_dict
        self.build_response = build_response
        self.get_user_logged_in = get_user_logged_in
        self.get_ask_to_open_remove_or_download = get_ask_to_open_remove_or_download

    def name(self):
        return "action_perform_search"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: dict):
        REPOSITORY_PATH = os.getenv('REPOSITORY_PATH')
        search_query = tracker.get_slot("search_query")
        metadata = tracker.latest_message.get("metadata")
        fullname = metadata.get("fullname")
        telegram_id = metadata.get("telegram_id")
        # telegram_id = "7272740693"
        curr_user = self.get_user_logged_in(telegram_id)
        if curr_user is None:
            dispatcher.utter_message('Maaf, anda belum bisa mengakses data center. Silakan verifikasi nomor HP kamu')
            return [
                SlotSet("search_query", None)
            ]

        results = []
        accounts = curr_user['accounts']
        search_results = {}
        no = 1
        for account in accounts:
            homedir = account['homedir'].lstrip("/")
            base_path = os.path.join(REPOSITORY_PATH, homedir)
            logger.info("attempting to find file with key '%s' on path %s", search_query, base_path)
            for root, dirs, files in os.walk(base_path):
                # find a folder with name like keyword
                for dir_name in dirs:
                    if search_query.lower() in dir_name.lower():
                        fullpath = os.path.join(root, dir_name)
                        results.append(fullpath)
                        search_results[no] = fullpath
                        no += 1

                # find for a file
                for file in files:
                    if search_query.lower() in file.lower():
                        fullpath = os.path.join(root, file)
                        results.append(fullpath)
                        search_results[no] = fullpath
                        no += 1

        count_search_result = len(results)
        logger.info("Got result %d for query search %s", count_search_result, search_query)
        if len(results) == 0:
            dispatcher.utter_message(f"Saya tidak dapat menemukan file atau data yang mengandung kata `{search_query}` 😞")
            return [
                SlotSet("search_query", None)
            ]

        logger.info("attempting to find file or data with keyword: %s", search_query)
        response = self.build_response(
            opening_message=f"Saya menemukan beberapa data yang mengandung kata: `{search_query}`",
            ending_message=self.get_ask_to_open_remove_or_download(),
            lspaths=results[:20]
        )
        dispatcher.utter_message(text=response)
        search_results_json = json.dumps(search_results) # ini bermasalah
        return [
            SlotSet("search_query", None),
            SlotSet("search_results", search_results_json),
            SlotSet("current_path", None)
        ]