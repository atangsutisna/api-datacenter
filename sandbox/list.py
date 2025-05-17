import os
from dotenv import load_dotenv

load_dotenv()
REPOSITORY_PATH = os.getenv('REPOSITORY_PATH')

# homedir = '/atang'
dir_list = os.listdir(REPOSITORY_PATH)
allowed_dirs = {"atang", "spark"}

dir_list = os.listdir(REPOSITORY_PATH)
filtered_dirs = [
    dir for dir in dir_list
    if dir in allowed_dirs and os.path.isdir(os.path.join(REPOSITORY_PATH, dir))
]

# print(filtered_dirs)

folder_spark_level_1 = "/home/kangatang/git/filegator/repository/spark"
parent_path = os.path.dirname(folder_spark_level_1)
print(parent_path)
# for dir in dir_list:
#     fullpath = os.path.join(REPOSITORY_PATH, dir)
#     print(fullpath)
    # full_path = os.path.join(REPOSITORY_PATH + homedir, dir)
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
# is_file = os.path.isfile('/home/kangatang/git/filegator/repository/atang/e-ticket.pdf')
# print(is_file)