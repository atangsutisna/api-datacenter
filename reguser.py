import json
import os
# todo: validate username
def add_user_to_db(file_path, new_entry):
    # Buat file jika belum ada
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            json.dump([], f)

    # Baca data lama
    with open(file_path, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = []

    # Cek apakah phoneNumber sudah ada
    phone_exists = any(user.get("phoneNumber") == new_entry["phoneNumber"] for user in data)

    if phone_exists:
        print(f"Phone number {new_entry['phoneNumber']} sudah ada. Tidak ditambahkan.")
    else:
        data.append(new_entry)
        with open(file_path, "w") as f:
            json.dump(data, f, separators=(",", ":"))
        print(f"Phone number {new_entry['phoneNumber']} berhasil ditambahkan.")

# Contoh pemakaian
# db_file = "mappinguser.json"
# new_object = {
#     "phoneNumber": "6287283838383",
#     "accounts": ["cici-paramida"]
# }

# add_user_to_db(db_file, new_object)