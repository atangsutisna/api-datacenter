import subprocess, os
from pathlib import Path

path_to_file = Path("/home/kangatang/git/filegator/repository/atang/file_example_XLS_100.xls")
filename = path_to_file.stem

def convert_to_pdf(input_path) -> str:
    input_path = Path(input_path)
    subprocess.run([
        "libreoffice",
        "--headless",
        "--convert-to", "pdf",
        "--outdir", str(input_path.parent),
        str(input_path)
    ])

    return os.path.join(input_path.parent, input_path.stem +".pdf") 

# print(filename)
# print(os.path.join(path_to_file.parent, filename +".pdf"))
# output = pptx_to_pdf("/home/kangatang/git/filegator/repository/atang/file_example_XLS_100.xls")
# print(f"Output: {output}")
# print("attempting to remove file")
# os.remove(output)