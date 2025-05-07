import PyPDF2

def read_pdf(filepath: str) -> str:
    with open(filepath, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text

# Contoh pemakaian
path_pdf = "/home/kangatang/git/filegator/repository/atang/PPT Per Puskesmas (non).pdf"
pdf_content = read_pdf(path_pdf)
print(pdf_content[:1000])  # Print first 1000 characters