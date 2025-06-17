import os
from docx import Document
import PyPDF2


def read_text_file(file):
    return file.read().decode("utf-8")


def read_docx_file(file):
    doc = Document(file)
    paragraphs = doc.paragraphs
    text_list = [para.text for para in paragraphs]
    full_text = "\n".join(text_list)
    return full_text


def read_pdf_file(file):
    text = ""
    reader = PyPDF2.PdfReader(file)
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text


def load_file(uploaded_file):
    filename = uploaded_file.name
    ext = os.path.splitext(filename)[-1].lower()

    if ext == ".txt":
        return read_text_file(uploaded_file)
    elif ext == ".docx":
        return read_docx_file(uploaded_file)
    elif ext == ".pdf":
        return read_pdf_file(uploaded_file)
    else:
        raise ValueError(f"Unsupported file format: {ext}")
