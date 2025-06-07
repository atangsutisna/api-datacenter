import os

current_path = "/home/kangatang/git/filegator/repository/spark"
folder_name = "New Folder"
counter = 0
while True:
    try:
        full_path = os.path.join(current_path, folder_name)
        print(f"attempting to create new folder with name %s", folder_name)
        os.makedirs(full_path)
        break
    except FileExistsError:
        counter += 1
        folder_name = f"New Folder {counter}"
    except Exception:
        print("gagal membuat folder baru")
        break
