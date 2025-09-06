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


class ActionDoRename(Action):
    def __init__(self):
        from checkpermissions import is_permitted
        from myutils import simplified_path

        self.is_permitted = is_permitted
        self.simplified_path = simplified_path

    def name(self) -> Text:
        return "action_do_rename"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        file_no = tracker.get_slot("file_no")
        new_name = tracker.get_slot("new_file_name")
        search_results = tracker.get_slot("search_results")
        # TODO: handle if the name has exist
        logger.info("attempting to rename file no %s to be %s", file_no, new_name)
        # dispatcher.utter_message(text=f"File line {file_no} will be rename to be {new_name}")
        # return [
        #     SlotSet("file_no", None),
        #     SlotSet("new_file_name", None)
        # ]

        if search_results:
            logger.info("attempting to load search results %s", search_results)
            user_files = json.loads(search_results)
            selected_path = user_files.get(file_no)
            
            # TODO: check permission
            # get old name
            if selected_path:
                metadata = tracker.latest_message.get("metadata")
                fullname = metadata.get("fullname")
                telegram_id = metadata.get("telegram_id")
                # telegram_id = "7272740693"
                write_permitted = self.is_permitted(telegram_id, selected_path, "write")
                logger.info("Is telegram id %s has write permission: %s", telegram_id, write_permitted)
                if write_permitted is False:
                    dispatcher.utter_message("Maaf, kamu tidak diijinkan untuk merubah nama folder atau file di sini.")
                    return [
                        SlotSet("file_no", None),
                        SlotSet("new_file_name", None),
                        SlotSet("has_rename_permission", None)
                    ]
                    # return {
                    #     "folder_name": None,
                    #     "new_file_name": None, 
                    #     "creation_permitted": False,
                    #     "requested_slot": None
                    # }
                # do rename
                is_file = os.path.isfile(selected_path)
                if is_file:
                    # rename file
                    directory = os.path.dirname(selected_path)
                    _, ext = os.path.splitext(selected_path)
                    logger.info("attempting to rename to be %s%s", new_name, ext)
                    new_path = os.path.join(directory, new_name + ext)
                    try:
                        os.rename(selected_path, new_path)
                        old_name = self.simplified_path(selected_path)
                        new_name = self.simplified_path(new_path)
                        dispatcher.utter_message(text=f"File `{old_name}` telah diubah namanya menjadi `{new_name}`")
                    except Exception as e:
                        logger.info("Failed to rename the file")
                        dispatcher.utter_message(text="Mohon maaf, sepertinya ada kesalahan sistem. Rename file gagal")
                else:
                    # rename folder
                    parent_dir = os.path.dirname(selected_path)
                    new_path = os.path.join(parent_dir, new_name)

                    # validate new_path
                    if os.path.exists(new_path):
                        old_name = self.simplified_path(selected_path)
                        dispatcher.utter_message(
                            text=f"Maaf, tidak dapat mengganti nama `{old_name}` menjadi `{new_name}`, "
                                f"karena sudah ada file/folder dengan nama tersebut."
                        )
                    else:
                        try:
                            os.rename(selected_path, new_path)
                            old_name = self.simplified_path(selected_path)
                            new_name = self.simplified_path(new_path)
                            dispatcher.utter_message(text=f"File `{old_name}` telah diubah namanya menjadi `{new_name}`")
                        except PermissionError:
                            dispatcher.utter_message(
                                text="Gagal mengganti nama file karena tidak ada izin."
                            )
                        except FileNotFoundError:
                            dispatcher.utter_message(
                                text="Gagal mengganti nama file. File asal tidak ditemukan."
                            )
                        except Exception as e:
                            logger.info(f"Failed to rename the folder {e}")
                            dispatcher.utter_message(text="Mohon maaf, sepertinya ada kesalahan sistem. Rename file gagal")                    
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
        else:
            dispatcher.utter_message(text=f"Saya tidak menemukan file dengan nomor atau baris {file_no}")

        return [
            SlotSet("file_no", None),
            SlotSet("new_file_name", None),
            SlotSet("has_rename_permission", None)
        ]