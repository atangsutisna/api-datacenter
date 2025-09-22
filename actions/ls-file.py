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

class ActionAccessData(Action):
    def __init__(self):
        from assistant_file_reader import read_file_with_file_search
        from fileconverter import convert_to_pdf
        from userloggedin import get_user_logged_in
        from myutils import simplified_path,get_ask_to_open_remove_or_download

        self.get_user_logged_in = get_user_logged_in
        self.read_file_with_file_search = read_file_with_file_search
        self.convert_to_pdf = convert_to_pdf
        self.simplified_path = simplified_path
        self.get_ask_to_open_remove_or_download = get_ask_to_open_remove_or_download

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
            logger.info("attempting to open dir on path %s", selected_path)
            if selected_path:
                is_file = os.path.isfile(selected_path)
                if is_file:
                    # open the file using openai
                    # dispatcher.utter_message(text="Mohon ditunggu, saya sedang membuat rangkuman file tersebut")
                    # call open api
                    ext = get_ext(selected_path)
                    supported_extension = {"pdf", "doc", "docx", "txt"}
                    OPENAI_APIKEY = os.getenv('OPENAI_APIKEY')
                    if ext in supported_extension:
                        logger.info("attempting to send request to openai")
                        prompt=(
                            "Tolong bacakan isi halaman 1 sampai 3 dari file ini."
                            "Jika tidak dapat dibaca, jelaskan penyebabnya secara singkat, tanpa mengajukan pertanyaan."
                        )
                        result = self.read_file_with_file_search(
                            api_key=OPENAI_APIKEY,
                            file_path=selected_path,
                            prompt=prompt
                        )
                        dispatcher.utter_message(text=result)
                    else:
                        # convert to pdf
                        logger.info(f"attempting to convert {selected_path} to pdf")
                        tmp_file_fullpath = self.convert_to_pdf(selected_path)
                        logger.info("attempting to ask to openai")
                        # perlu optimasi
                        result = self.read_file_with_file_search(
                            api_key=OPENAI_APIKEY,
                            file_path=tmp_file_fullpath
                        )
                        dispatcher.utter_message(text=result)
                        os.remove(tmp_file_fullpath)
                    return [
                        SlotSet("file_no", None),
                    ]
                else:
                    # list all child of the path
                    user_workspaces = []
                    simple_root_path = self.simplified_path(selected_path)
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

                additional_response = self.get_ask_to_open_remove_or_download()
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