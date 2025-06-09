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
from rasa_sdk.events import SlotSet
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.events import AllSlotsReset, ActiveLoop
from datetime import datetime
from zoneinfo import ZoneInfo
import sys
import os
import random
import logging
import json
import shutil
import traceback

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
# logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# REPOSITORY_PATH = os.getenv('REPOSITORY_PATH')
# OPENAI_APIKEY = os.getenv('OPENAI_APIKEY')

def get_range_list(dictionary):
    if not dictionary:
        return "No data"
    min_key = min(int(k) for k in dictionary.keys())
    max_key = max(int(k) for k in dictionary.keys())
    return f"{min_key}..{max_key}"

def get_file_size_bytes(file_path):
    return os.path.getsize(file_path)

def get_folder_size_bytes(folder_path):
    total_size = 0
    for dirpath, _, filenames in os.walk(folder_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.isfile(fp):
                total_size += os.path.getsize(fp)
    return total_size    

def format_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024**2:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024**3:
        return f"{size_bytes / 1024**2:.2f} MB"
    else:
        return f"{size_bytes / 1024**3:.2f} GB"

def simplified_path(original_path: str) -> str:
    folder_name = os.path.basename(original_path)
    repository_path = original_path.split("/repository", 1)[1]
    
    parent_path = os.path.dirname(repository_path)
    return os.path.join(parent_path, folder_name)

def get_ask_to_open_remove_or_download() -> str:
    additional_responses = [
        "Ada hal lain yang perlu saya bantu dengan data ini? Misalnya, Kamu ingin menghapus, mengunduh, atau membuka folder lain? Kamu bisa sebutkan angkanya.",
        "Perlu bantuan lanjutan? Saya bisa bantu hapus, unduh, atau masuk ke folder lain. Cukup beritahu nomor yang Kamu inginkan.",
        "Apa lagi yang bisa saya lakukan untuk Kamu? Ada pilihan hapus, unduh, atau jelajahi folder. Silakan ketik angkanya.",
        "Apakah ada tindakan lain yang ingin Kamu lakukan? Misalnya, menghapus, mengunduh, atau membuka folder? Kamu bisa memilih dengan menyebutkan angkanya.",
        "Sudah selesai dengan ini, atau ada lagi yang bisa saya bantu? Mungkin menghapus, mengunduh, atau membuka folder lain? Sebutkan saja nomornya."
    ]
    return random.choice(additional_responses)

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
                message = f"Hai, selamat pagi *{fullname}*"
            elif 10 <= current_hour < 15:
                message = f"Hai {fullname}, selamat siang. Ada yang bisa saya bantu?"
            elif 15 <= current_hour < 18:
                message = f"Hai {fullname}, selamat sore. Ada yang bisa saya bantu?"
            else:
                message = f"Hai {fullname}, selamat malam. Ada yang bisa saya bantu?"
        
        dispatcher.utter_message(
            text=message,
            custom={
                "data": {
                    "username": "atang gombal",
                    "fullname": "Atang Sutisna, Ir",
                    "teks": "Silahkan pilih salah satu opsi:",
                    "reply_markup": {
                        "inline_keyboard": []
                    }
                }
            }
        )
        return []

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
            dispatcher.utter_message(text="""
            Maaf, saya belum mengenal kamu.
            Silahkan verifikasi nomor HP kamu dulu.
            """)
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

class ActionListWorkspace(Action):
    def __init__(self):
        from userloggedin import get_user_logged_in
        self.get_user_logged_in = get_user_logged_in

    def name(self) -> Text:
        return "action_show_data"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        fullname = tracker.sender_id
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
            for path in user_workspaces:
                file = os.path.isfile(path)
                simple_path = simplified_path(path)
                if not file:
                    message += f"\n{no}. `{simple_path}` (`{format_size(get_folder_size_bytes(path))}`)"
                else:
                    message += f"\n{no}. `{simple_path}` (`{format_size(get_file_size_bytes(path))}`)"
                search_results[no] = path
                no += 1

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
    
class ActionAccessData(Action):
    def name(self):
        return "action_to_open_data"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: dict):
        logger.info("starting to run access data")
        file_no = tracker.get_slot("file_no")
        logger.info("Get file no from slot %s", file_no)
        search_results = tracker.get_slot("search_results")
        # dispatcher.utter_message(text=f"Kamu memilih file no {file_no}")
        # return []
        if search_results:
            logger.info("attempting to load search results %s", search_results)
            user_files = json.loads(search_results)
            selected_path = user_files.get(file_no)
            if selected_path:
                is_file = os.path.isfile(selected_path)
                if is_file:
                    # open the file using openai
                    dispatcher.utter_message(text="Mohon ditunggu, saya sedang membuat rangkuman file tersebut")
                    return []
                else:
                    # list all child of the path
                    user_workspaces = []
                    simple_root_path = simplified_path(selected_path)
                    list_dir = os.listdir(selected_path)
                    if not list_dir:
                        messages = [
                            f"Folder ini kosong. Tidak ada file atau folder di dalam folder `{simple_root_path}`",
                            f"Saya sudah membuka folder `{simple_root_path}`, tapi sepertinya tidak ada isinya",
                            f"Folder `{simple_root_path}` saat ini kosong. Tidak ada data yang bisa saya tampilkan"
                        ]
                        message = random.choice(messages)
                        dispatcher.utter_message(text=message)
                        return [
                            SlotSet("current_path", selected_path),
                        ]
                    
                    for dir in list_dir:
                        child_path = os.path.join(selected_path, dir)
                        user_workspaces.append(child_path)

                    # format user workspaces
                    opening_messages = [
                        f"Baik, ini isi dari folder `{simple_root_path}`:",
                        f"Kamu sekarang berada di dalam folder `{simple_root_path}`. Ini semua yang ada di dalamnya:"
                    ]
                    message = random.choice(opening_messages)
                    no = 1
                    search_results = {}
                    for path in user_workspaces:
                        file = os.path.isfile(path)
                        simple_path = simplified_path(path)
                        if not file:
                            message += f"\n{no}. `{simple_path}` (`{format_size(get_folder_size_bytes(path))}`)"
                        else:
                            message += f"\n{no}. `{simple_path}` (`{format_size(get_file_size_bytes(path))}`)"
                        search_results[no] = path
                        no += 1

                additional_response = get_ask_to_open_remove_or_download()
                message += "\n"+ additional_response
                # message += "\nAda yang perlu saya bantu lagi? misal menghapus, mendownload, atau membuka folder. sebutkan saja angkanya"
                dispatcher.utter_message(text=message)

                search_results_json = json.dumps(search_results)
                return [
                    SlotSet("search_results", search_results_json), 
                    SlotSet("file_no", None),
                    SlotSet("current_path", selected_path),
                ]
                # return []
            else:
                range_list = get_range_list(user_files)
                max_no = max(int(k) for k in user_files.keys())
                messages = [
                    f"Hmm, nomor {file_no} di luar rentang data yang saya miliki 🤔. Saya punya data {range_list}. Apakah ada nomor lain yang kamu maksud?",
                    f"Maaf, saya tidak bisa menemukan data dengan nomor {file_no}. Data yang ada hanya sampai nomor {max_no}. Apakah ada nomor lain yang kamu maksud?",
                    f"Saya tidak menemukan data di posisi ke-{file_no}. Daftar data kamu berakhir di nomor {max_no}. Mungkin kamu ingin melihat data lain?"
                ]
                response = random.choice(messages)
                dispatcher.utter_message(text=response)
                return []
        else:
            dispatcher.utter_message(text=f"Data nomor {file_no} tidak ditemukan")
            return []

class ActionBackToPrevious(Action):
    def __init__(self):
        from userloggedin import get_user_logged_in
        self.get_user_logged_in = get_user_logged_in

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
            "Kamu sedang berada di direktori utama Kamu.",
            "Selamat datang di folder utama Kamu.",
            "Ini area utama penyimpanan Kamu.",
            "Kamu telah kembali ke folder utama Kamu."
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
            for path in user_workspaces:
                file = os.path.isfile(path)
                simple_path = simplified_path(path)
                if not file:
                    message += f"\n{no}. `{simple_path}` (`{format_size(get_folder_size_bytes(path))}`)"
                else:
                    message += f"\n{no}. `{simple_path}` (`{format_size(get_file_size_bytes(path))}`)"
                search_results[no] = path
                no += 1

            additional_response = get_ask_to_open_remove_or_download()
            message += "\n"+ additional_response

            dispatcher.utter_message(text=message)
            search_results_json = json.dumps(search_results)
            return [
                SlotSet("search_results", search_results_json),
            ]
        else:
            # list child of current path
            parent_path = os.path.dirname(current_path)
            list_dir = os.listdir(parent_path)
            user_workspaces = []
            for dir in list_dir:
                child_path = os.path.join(parent_path, dir)
                user_workspaces.append(child_path)

            simple_root_path = simplified_path(parent_path)
            opening_messages = [
                f"Baik, ini isi dari folder `{simple_root_path}`:",
                f"Kamu sekarang berada di dalam folder `{simple_root_path}`. Ini semua yang ada di dalamnya:"
            ]
            message = random.choice(opening_messages)

            no = 1
            search_results = {}
            for path in user_workspaces:
                file = os.path.isfile(path)
                simple_path = simplified_path(path)
                if not file:
                    message += f"\n{no}. `{simple_path}` (`{format_size(get_folder_size_bytes(path))}`)"
                else:
                    message += f"\n{no}. `{simple_path}` (`{format_size(get_file_size_bytes(path))}`)"
                search_results[no] = path
                no += 1
            message += "\n"+ get_ask_to_open_remove_or_download()
            dispatcher.utter_message(text=message)
            search_results_json = json.dumps(search_results)
            return [
                SlotSet("search_results", search_results_json), 
                SlotSet("file_no", None),
                SlotSet("current_path", parent_path)
            ]

class ActionRemoveData(Action):
    def __init__(self):
        from checkpermissions import is_permitted
        from myutils import list_dir, build_response, to_dict
        self.is_permitted = is_permitted
        self.list_dir = list_dir
        self.build_response = build_response
        self.to_dict = to_dict
        
    def name(self):
        return "action_remove_data"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: dict):
        logger.info("starting to remove data")
        file_no = tracker.get_slot("file_no")
        current_path = tracker.get_slot("current_path")

        metadata = tracker.latest_message.get("metadata")
        fullname = metadata.get("fullname")
        telegram_id = metadata.get("telegram_id")

        logger.info("Got current path %s", current_path)
        chmod_permitted = self.is_permitted(telegram_id, current_path, "chmod")
        if chmod_permitted:
            # check file or folder?
            search_results = tracker.get_slot("search_results")
            user_files = json.loads(search_results)
            logger.info("current user files %r", user_files)
            selected_path = user_files.get(file_no)
            file_exists = os.path.exists(selected_path)
            removed_path = simplified_path(selected_path)
            if selected_path and file_exists:
                is_file = os.path.isfile(selected_path)
                if is_file:         
                    # just remove the file    
                    os.remove(selected_path)
                else:
                    # remove the folder and it's childs
                    shutil.rmtree(selected_path)
                
                lspaths = self.list_dir(current_path)
                response = self.build_response(
                    opening_message=f"Data sudah `{removed_path}` dihapus",
                    ending_message=get_ask_to_open_remove_or_download(),
                    lspaths=lspaths
                )
                # prepare for response
                dispatcher.utter_message(text=response)
                lspaths_json = json.dumps(self.to_dict(lspaths))
                return [
                    SlotSet("search_results", lspaths_json), 
                    SlotSet("file_no", None)
                ]
            else:
                # data tidak ditemukan
                lspaths = self.list_dir(current_path)
                response = self.build_response(
                    opening_message=f"Data `{removed_path}` nggak ketemu",
                    ending_message=get_ask_to_open_remove_or_download(),
                    lspaths=lspaths
                )
                # prepare for response
                dispatcher.utter_message(text=response)
                lspaths_json = json.dumps(self.to_dict(lspaths))
                return [
                    SlotSet("search_results", lspaths_json), 
                    SlotSet("file_no", None)
                ]
        else:
            dispatcher.utter_message(text=f"Maaf, kamu nggak ada ijin menghapus")
            return []

class ActionCheckPermissionRemoveData(Action):
    def __init__(self):
        from checkpermissions import is_permitted
        self.is_permitted = is_permitted

    def name(self):
        return "action_check_permission_remove_data"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: dict):
        logger.info("starting to check permission")
        file_no = tracker.get_slot("file_no")
        # hapus, terus tampilkan list datanya
        # hapus dulu datanya, 
        chmod_permitted = is_permitted(telegram_id, path, "chmod")
        if chmod_permitted:
            return [
                SlotSet("remove_permitted", True)
            ]
        else:
            dispatcher.utter_message(text=f"Mohon maaf, kamu nggak punya akses untuk menghapus data")
            return [
                SlotSet("remove_permitted", False)
            ]

class ActionRemoveCurrentPath(Action):
    def __init__(self):
        from checkpermissions import is_permitted
        from myutils import list_dir, build_response, to_dict, get_root_path, get_workspaces
        self.is_permitted = is_permitted
        self.list_dir = list_dir
        self.build_response = build_response
        self.to_dict = to_dict
        self.get_root_path = get_root_path
        self.get_workspaces = get_workspaces
    
    def name(self):
        return "action_to_remove_current_path"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: dict):
        metadata = tracker.latest_message.get("metadata")
        telegram_id = metadata.get("telegram_id")
        current_path = tracker.get_slot("current_path")
        root_path = self.get_root_path(current_path)
        simple_path = simplified_path(current_path)

        logger.info("Got current path %s", current_path)
        chmod_permitted = self.is_permitted(telegram_id, current_path, "chmod")
        if not chmod_permitted:
            dispatcher.utter_message(text=f"Maaf, kamu tidak dijinkan untuk menghapus data")
            return []
        
        user_workspaces = self.get_workspaces(telegram_id)
        if current_path in user_workspaces:
            dispatcher.utter_message(text=f"Folder utama (`{simple_path}`) tidak diijinkan dihapus")
            return []

        logger.info("attempting to remove current path %s", current_path)
        # todo: jangan sampai menghapus root path -nya user
        shutil.rmtree(current_path)

        # re-list lagi 
        lspaths = self.list_dir(root_path)
        response = self.build_response(
            opening_message=f"Data sudah `{simple_path}` dihapus",
            ending_message=get_ask_to_open_remove_or_download(),
            lspaths=lspaths
        )
        # prepare for response
        dispatcher.utter_message(text=response)
        lspaths_json = json.dumps(self.to_dict(lspaths))
        return [
            SlotSet("search_results", lspaths_json), 
        ]

class ActionCreateFolder(Action):
    def __init__(self):
        from checkpermissions import is_permitted
        from myutils import get_root_path, list_dir, to_dict, build_response
        self.is_permitted = is_permitted
        self.get_root_path = get_root_path
        self.list_dir = list_dir
        self.to_dict = to_dict
        self.build_response = build_response

    def name(self):
        return "action_create_folder"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: dict):
        logger.info("action create folder form submit")
        current_path = tracker.get_slot("current_path")
        folder_name = tracker.get_slot("folder_name")
        logger.info("Got slot `folder_name` value: %s", folder_name)
        # dispatcher.utter_message(text=f"Folder '{folder_name}' berhasil dibuat")
        # return [
        #     SlotSet("folder_name", None),
        # ]

        if current_path is None:
            dispatcher.utter_message(text="Silahkan kamu pilih dulu lokasi folder-nya")
            return []

        metadata = tracker.latest_message.get("metadata")
        fullname = metadata.get("fullname")
        telegram_id = metadata.get("telegram_id")
        # telegram_id = "7272740693"
        creation_permitted = self.is_permitted(telegram_id, current_path, "write")
        logger.info("Is telegram id %s has creation permission: %s", telegram_id, creation_permitted)
        if creation_permitted is False:
            logger.info("User with id %s is not permitted to write", telegram_id)
            simple_path = simplified_path(current_path)
            message = f"Maaf, kamu tidak memiliki izin membuat folder di lokasi ini : `{simple_path}`"
            dispatcher.utter_message(text=message)
            return [
                SlotSet("folder_name", None),
                SlotSet("creation_permitted", None)
            ]

        """ create folder is premitted and folder is None """
        lspaths = None
        if folder_name is None:
            counter = 0
            folder_name = "New Folder"
            while True:
                try:
                    full_path = os.path.join(current_path, folder_name)
                    logger.info("attempting to create new folder with name %s", folder_name)
                    os.makedirs(full_path)

                    lspaths = self.list_dir(current_path)
                    response = self.build_response(
                        opening_message=f"Folder baru dengan nama `{folder_name}` sudah dibuat",
                        ending_message=get_ask_to_open_remove_or_download(),
                        lspaths=lspaths
                    )
                    # dispatcher.utter_message(response="utter_folder_created_success", folder_name=folder_name, current_path=current_path)
                    dispatcher.utter_message(text=response)
                    break
                except FileExistsError:
                    counter += 1
                    folder_name = f"New Folder {counter}"
                except Exception as e:
                    dispatcher.utter_message(response="utter_create_folder_failed", folder_name=folder_name)
                    traceback.print_exc()
                    break
            # TODO: sebelum direturn, tolong update search_result, agar folder baru masuk di dalamnya
            lspaths_json = json.dumps(self.to_dict(lspaths))
            return [
                SlotSet("search_results", lspaths_json)
            ]

        """ Ketika nama folder tidak didefinisikan, maka sistem akan membuat folder default"""
        if folder_name is not None:
            try:
                full_path = os.path.join(current_path, folder_name)
                logger.info("attempting to create new folder with name %s", folder_name)
                os.makedirs(full_path)

                lspaths = self.list_dir(current_path)
                response = self.build_response(
                    opening_message=f"Folder baru dengan nama '{folder_name}' sudah dibuat",
                    ending_message=get_ask_to_open_remove_or_download(),
                    lspaths=lspaths
                )
                dispatcher.utter_message(text=response)
            except FileExistsError:
                dispatcher.utter_message(response="utter_create_folder_failed", folder_name=folder_name)
                traceback.print_exc()
            except Exception as e:
                dispatcher.utter_message(response="utter_create_folder_failed", folder_name=folder_name)
                traceback.print_exc()

            return [
                SlotSet("folder_name", None),
                SlotSet("creation_permitted", None)
            ]

class ValidateCreateFolderForm(FormValidationAction):
    def __init__(self):
        from checkpermissions import is_permitted
        self.is_permitted = is_permitted

    def name(self) -> Text:
        """ 
        Nama validasi harus seperti ini 'validate_<form_name>'
        AI menyarankan untuk membuat nama seperti ini 'action_validate_<form_name>'. Saran seperti itu tidak bekerja.
        Gunakan pendekatan seperti ini: 'validate_<form_name>'
        """ 
        return "validate_create_folder_form"
    
    def validate_folder_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict
    ) -> Dict[Text, Any]:
        """ 
        validate folder name 
        - current path is exists
        - ensure folder name doest not exists
        """
        logger.info("attempting to validate folder name")
        current_path = tracker.get_slot("current_path")
        
        metadata = tracker.latest_message.get("metadata")
        fullname = metadata.get("fullname")
        telegram_id = metadata.get("telegram_id")
        # telegram_id = "7272740693"
        write_permitted = self.is_permitted(telegram_id, current_path, "write")
        logger.info("Is telegram id %s has write permission: %s", telegram_id, write_permitted)
        if write_permitted is False:
            dispatcher.utter_message(response="utter_permission_denied_create_folder")
            return {
                "folder_name": None, 
                "creation_permitted": False,
                "requested_slot": None
            }

        proposed_folder_path = os.path.join(current_path, slot_value)
        if os.path.exists(proposed_folder_path):
            logger.info("Failed to create folder, %s exists", slot_value)
            dispatcher.utter_message(response="utter_folder_exists")
            return {"folder_name": None, "creation_permitted": True}
        else:
            logger.info("Folder name is valid")
            return {"folder_name": slot_value, "creation_permitted": True}

""" action perform search """
class ActionPerformSearch(Action):
    def __init__(self):
        from userloggedin import get_user_logged_in
        from checkpermissions import is_permitted
        from myutils import get_root_path, list_dir, to_dict, build_response
        self.is_permitted = is_permitted
        self.get_root_path = get_root_path
        self.list_dir = list_dir
        self.to_dict = to_dict
        self.build_response = build_response
        self.get_user_logged_in = get_user_logged_in

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

                # find for a file
                for file in files:
                    if search_query.lower() in file.lower():
                        fullpath = os.path.join(root, file)
                        results.append(fullpath)

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
            ending_message=get_ask_to_open_remove_or_download(),
            lspaths=results
        )
        dispatcher.utter_message(text=response)
        search_results_json = json.dumps(results)
        return [
            SlotSet("search_query", None),
            SlotSet("search_results", search_results_json),
            SlotSet("current_path", None)
        ]
""" action perform to download """
class ActionPerformDownload(Action):
    def __init__(self):
        from userloggedin import get_user_logged_in
        from checkpermissions import is_permitted
        from myutils import get_root_path, list_dir, to_dict, build_response
        self.is_permitted = is_permitted
        self.get_root_path = get_root_path
        self.list_dir = list_dir
        self.to_dict = to_dict
        self.build_response = build_response
        self.get_user_logged_in = get_user_logged_in

    def name(self):
        return "action_perform_download"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: dict):
        file_no = tracker.get_slot("file_no")
        logger.info("attempting to send file no %s", file_no)
        dispatcher.utter_message(text="Baik, saya akan menyiapkan data untuk di download..")
        return [
            SlotSet("file_no", None)
        ]