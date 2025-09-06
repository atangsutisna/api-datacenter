from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import SlotSet
import logging,sys,os,random,json
import traceback

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)
logger = logging.getLogger(__name__)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class ActionCreateFolder(Action):
    def __init__(self):
        from checkpermissions import is_permitted
        from myutils import get_root_path,list_dir,to_dict,build_response,get_ask_to_open_remove_or_download,simplified_path

        self.is_permitted = is_permitted
        self.get_root_path = get_root_path
        self.list_dir = list_dir
        self.to_dict = to_dict
        self.build_response = build_response
        self.get_ask_to_open_remove_or_download = get_ask_to_open_remove_or_download
        self.simplified_path = simplified_path

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
            simple_path = self.simplified_path(current_path)
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
                        ending_message=self.get_ask_to_open_remove_or_download(),
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
                    opening_message=f"Folder baru dengan nama `{folder_name}` sudah dibuat",
                    ending_message=self.get_ask_to_open_remove_or_download(),
                    lspaths=lspaths
                )
                dispatcher.utter_message(text=response)
                lspaths_json = json.dumps(self.to_dict(lspaths))
                return [
                    SlotSet("folder_name", None),
                    SlotSet("creation_permitted", None),
                    SlotSet("search_results", lspaths_json)
                ]
            except FileExistsError:
                logger.info("Failed to create a new folder. The name %s alread exists.", folder_name)
                err_message = f"Nama folder `{folder_name}` sudah digunakan. Coba pilih nama berbeda."
                dispatcher.utter_message(text=err_message)
                traceback.print_exc()
                return [
                    SlotSet("folder_name", None),
                    SlotSet("creation_permitted", None),
                ]
            except Exception as e:
                logger.info("Failed to create folder %s", folder_name)
                dispatcher.utter_message(response="utter_create_folder_failed", folder_name=folder_name)
                traceback.print_exc()
                return [
                    SlotSet("folder_name", None),
                    SlotSet("creation_permitted", None),
                ]
