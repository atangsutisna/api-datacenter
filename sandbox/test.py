# import re, os
import json, math
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

if is_child(parent_folder, child_folder):
    print(f"{child_folder} adalah child dari {parent_folder}")
else:
    print(f"{child_folder} BUKAN child dari {parent_folder}")

