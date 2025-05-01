import os
from dotenv import load_dotenv

load_dotenv()
REPOSITORY_PATH = os.getenv('REPOSITORY_PATH')

# homedir = '/atang'
# dir_list = os.listdir(REPOSITORY_PATH + homedir)
# no = 1
# message = "<b>Hasil Pencarian:</b>\n"
# for dir in dir_list:
#     # full_path = os.path.join(root, dir)
#     full_path = os.path.join(REPOSITORY_PATH + homedir, dir)
#     print(full_path)
#     is_file = os.path.isfile(REPOSITORY_PATH + homedir + "/" + dir)
#     no_str = str(no)
#     if is_file:
#         # message += str(no) +"\\. ["+ escape_special_chars(dir) + "]\n"
#         message += f"{no_str}. {dir}\n"
#     else:
#         # message += str(no) +"\\. *Folder* \- "+ escape_special_chars(dir) + "\n"
#         message += f"{no_str}. <b>Folder</b> {dir}\n"
#     # message += "\\.\n"
#     no += 1
# print(message)
is_file = os.path.isfile('/home/kangatang/git/filegator/repository/atang/e-ticket.pdf')
print(is_file)