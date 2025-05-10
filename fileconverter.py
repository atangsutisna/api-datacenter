import subprocess
from pathlib import Path

def pptx_to_pdf(input_path):
    input_path = Path(input_path)
    subprocess.run([
        "libreoffice",
        "--headless",
        "--convert-to", "pdf",
        "--outdir", str(input_path.parent),
        str(input_path)
    ])

pptx_to_pdf("/home/kangatang/git/filegator/repository/atang/file_example_XLS_100.xls")