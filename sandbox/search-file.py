import os

folder_path = "/home/kangatang/git/filegator/repository/atang/"
keyword = "inisiatif"

for root, dirs, files in os.walk(folder_path):
    for file in files:
        if keyword in file:
            full_path = os.path.join(root.split("/atang/", 1)[1], file)
            print("File ditemukan: ", full_path)