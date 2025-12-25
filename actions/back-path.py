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

class ActionBackToPrevious(Action):
    def __init__(self):
        from userloggedin import get_user_logged_in
        from myutils import simplified_path,get_ask_to_open_remove_or_download
        
        self.get_user_logged_in = get_user_logged_in
        self.simplified_path = simplified_path
        self.get_ask_to_open_remove_or_download = get_ask_to_open_remove_or_download

    def name(self):
        return "action_back_to_previous"

    def ls_root(self, telegram_id: str):
        curr_user = self.get_user_logged_in(telegram_id)
        accounts = curr_user['accounts']
        root_path = os.getenv('REPOSITORY_PATH')
        user_workspaces = []
        if len(accounts) > 1:
            for account in accounts:
                homedir = account['homedir'].lstrip("/")
                fullpath = os.path.join(root_path, homedir)
                user_workspaces.append(fullpath)
        else:
            dirname = accounts[0]['homedir'].lstrip("/")
            logger.info("attempting to list all data in %s", dirname)
            home_path = os.path.join(root_path, dirname)
            list_dir = os.listdir(home_path)
            for dir in list_dir:
                child_path = os.path.join(home_path, dir)
                user_workspaces.append(child_path)
        
        return user_workspaces

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: dict):
        # get telegram id 7272740693
        metadata = tracker.latest_message.get("metadata")
        fullname = metadata.get("fullname")
        telegram_id = metadata.get("telegram_id")

        opening_messages = [
            "Ini adalah folder utama Kamu.",
            "Kamu sedang berada di direktori utama",
            "Folder utama Kamu.",
            "Ini area utama penyimpanan Kamu.",
            "Kamu telah kembali ke folder utama"
        ]

        current_path = tracker.get_slot("current_path")
        root_paths = tracker.get_slot("root_paths")
        logger.info("root paths %r", root_paths)
        root_paths = json.loads(root_paths)

        logger.info("Got current path %s", current_path)
        # root_path = os.getenv('REPOSITORY_PATH')
        # fixme: jangan sampai root_path
        if current_path in root_paths:
            # tampilkan root path setiap user
            user_workspaces = self.ls_root(telegram_id)
            message = random.choice(opening_messages)
            no = 1
            search_results = {}
            sorted_paths = sorted(user_workspaces, key=lambda x: x.lower())
            for path in sorted_paths:
                file = os.path.isfile(path)
                # simple_path = self.simplified_path(path)
                simple_path = os.path.basename(path)
                if not file:
                    message += f"\n{no}. `{simple_path}`"
                else:
                    message += f"\n{no}. `{simple_path}`"
                search_results[no] = path
                no += 1

            additional_response = "Data mana yang kamu inginkan? sebutkan angkanya.."
            message += "\n"+ additional_response

            dispatcher.utter_message(text=message)
            search_results_json = json.dumps(search_results)
            return [
                SlotSet("current_path", None),
                SlotSet("search_results", search_results_json),
            ]
        else:
            # list child of current path
            parent_path = os.path.dirname(current_path)
            list_dir = os.listdir(parent_path)
            user_workspaces = []
            for dir in list_dir:
                child_path = os.path.join(parent_path, dir)

                # mtime = os.path.getmtime(child_path)
                user_workspaces.append(child_path)

            simple_root_path = self.simplified_path(parent_path)
            opening_messages = [
                f"Baik, ini isi dari folder `{simple_root_path}`:",
                f"Kamu sekarang berada di dalam folder `{simple_root_path}`. Ini semua yang ada di dalamnya:"
            ]
            message = random.choice(opening_messages)

            no = 1
            search_results = {}
            sorted_paths = sorted(user_workspaces, key=lambda x: x.lower())
            # sorted_list = sorted(user_workspaces, key=lambda x: x.lower())
            logger.info("Saya yakin masuk ke sini...")
            for path in sorted_paths:
                file = os.path.isfile(path)
                # simple_path = self.simplified_path(path)
                simple_path = os.path.basename(path)
                if not file:
                    message += f"\n{no}. `{simple_path}`"
                else:
                    message += f"\n{no}. `{simple_path}`"
                search_results[no] = path
                no += 1
            message += "\n"+ self.get_ask_to_open_remove_or_download()
            dispatcher.utter_message(text=message)
            search_results_json = json.dumps(search_results)
            return [
                SlotSet("search_results", search_results_json), 
                SlotSet("file_no", None),
                SlotSet("current_path", parent_path)
            ]