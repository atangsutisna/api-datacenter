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

class ActionGoHome(Action):
    def __init__(self):
        from userloggedin import get_user_logged_in
        from myutils import simplified_path

        self.get_user_logged_in = get_user_logged_in
        self.simplified_path = simplified_path

    def name(self) -> Text:
        return "action_go_home"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        logger.info("call go home...")
        fullname = tracker.sender_id
        dispatcher.utter_message(text="Baik, mohon ditunggu...")

        if fullname == "user":
            # belum login
            dispatcher.utter_message(text="""
            Maaf, saya belum mengenal kamu.
            Silahkan verifikasi nomor HP kamu dulu.
            """)

            return []
        else:
            # get telegram id 7272740693
            metadata = tracker.latest_message.get("metadata")
            fullname = metadata.get("fullname")
            telegram_id = metadata.get("telegram_id")
            
            # todo: jika user hanya punya satu folder, tampilkan saja langsung isinya
            curr_user = self.get_user_logged_in(telegram_id)
            # todo: check sudah konfirmasi nomor atau belum
            accounts = curr_user['accounts']
            user_workspaces = []
            root_paths = []
            REPOSITORY_PATH = os.getenv('REPOSITORY_PATH')
            current_path = None
            logger.info("total account for user %s : %d", telegram_id, len(accounts))
            if len(accounts) > 1:
                for account in accounts:
                    homedir = account['homedir'].lstrip("/")
                    root_path = os.path.join(REPOSITORY_PATH, homedir)
                    root_paths.append(root_path)
                    user_workspaces.append(root_path)
            else:
                dirname = accounts[0]['homedir'].lstrip("/")
                logger.info("attempting to list all data in %s", dirname)
                root_path = os.path.join(REPOSITORY_PATH, dirname)
                current_path = root_path
                list_dir = os.listdir(root_path)
                for dir in list_dir:
                    child_path = os.path.join(root_path, dir)
                    root_paths.append(root_path)
                    user_workspaces.append(child_path)

            opening_messages = [
                "Baik, ini semua data yang kamu miliki:",
                "Ini daftar data yang kamu miliki:",
                "Kamu memiliki beberapa data yang tersimpan. Ini daftarnya:"
            ]
            message = random.choice(opening_messages)
            no = 1
            search_results = {}
            sorted_list = sorted(user_workspaces, key=lambda x: x.lower())
            for path in sorted_list:
                file = os.path.isfile(path)
                simple_path = self.simplified_path(path)
                if not file:
                    message += f"\n{no}. `{simple_path}`"
                else:
                    message += f"\n{no}. `{simple_path}`"
                search_results[no] = path
                no += 1

            if len(accounts) > 1:
                additional_response = "Jika kamu ingin membuka salah satunya, cukup ketik angkanya."
            else:
                additional_response = get_ask_to_open_remove_or_download()
            message += "\n"+ additional_response

            dispatcher.utter_message(
                text=message
            )

            root_paths_json = json.dumps(root_paths)
            search_results_json = json.dumps(search_results)
            return [
                SlotSet("root_paths", root_paths_json),
                SlotSet("search_results", search_results_json),
                SlotSet("current_path", current_path)
            ]