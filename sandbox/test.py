# import re, os
import json, math, os
import base64
import zlib
import hashlib
import shutil

# def escape_hyphen(text):
#     return re.sub(r"-", r"\\-", text)

# Contoh penggunaan
# text = "1. Ayam-Goreng - Lihat resep di https://example.com/ayam-goreng"
# escaped_text = escape_hyphen(text)
# print(escaped_text)
# is_file = os.path.isfile("/home/kangatang/git/filegator/repository/sdd/Public Internal/shu-pinjaman.csv")
# print(is_file)
# print(math.pi)
# homedir = "/atang"
# print(homedir.lstrip("/"))

from pathlib import Path

def is_child(parent, child):
    try:
        Path(child).resolve().relative_to(Path(parent).resolve())
        return True
    except ValueError:
        return False

# Contoh penggunaan
parent_folder = "/home/kangatang/git/filegator/repository/spark"
child_folder = "/home/kangatang/git/filegator/repository/spark/samplepptx.pptx"

# if is_child(parent_folder, child_folder):
#     print(f"{child_folder} adalah child dari {parent_folder}")
# else:
#     print(f"{child_folder} BUKAN child dari {parent_folder}")

path = "/home/kangatang/git/filegator/repository/spark/Folder 6"
# dirname = os.path.dirname("/home/kangatang/git/filegator/repository/spark/Folder 6")
# folder_name = os.path.basename(child_folder)
# rep_path = path.split("/repository", 1)[1]
parent_path = os.path.dirname(path)
# folder_path = os.path.join(parent_path, folder_name)
print(parent_path)
# def encode_path(path):
#     return base64.urlsafe_b64encode(path.encode()).decode()

# def decode_path(encoded):
#     return base64.urlsafe_b64decode(encoded.encode()).decode()

# def hash_path(path):
#     return hashlib.sha1(path.encode()).hexdigest()[:10]

# encoded_path = encode_path(parent_folder)
# decoded_path = decode_path(encoded_path)
# print(f"encoded path: {encoded_path}")
# print(f"decoded path: {decoded_path}")
# print(len("L2hvbWUva2FuZ2F0YW5nL2dpdC9maWxlZ2F0b3IvcmVwb3NpdG9yeS9hdGFuZy9zdG9yeWxpbmUgaW5pc2lhdGlmLnhsc3g="))
# target_path = "/home/kangatang/git/filegator/repository/spark/Folder 1/"
# compressed = zlib.compress(path.encode())
# encoded = base64.urlsafe_b64encode(compressed).decode()
# print(encoded)

# path_hash = hash_path(path)
# print(path_hash)
# zip_path = shutil.make_archive("/home/kangatang/git/filegator/repository/spark/Folder 1", "zip", target_path)
# print(zip_path)

