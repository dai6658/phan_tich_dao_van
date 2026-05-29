import os
from docx import Document
import pdfplumber  # Thư viện đọc PDF tiếng Việt tốt nhất hiện nay


def read_text_file(file):
    """Đọc file .txt"""
    return file.read().decode("utf-8")


def read_docx_file(file):
    """Đọc file .docx giữ nguyên cấu trúc đoạn"""
    doc = Document(file)
    # Lọc bỏ các đoạn văn rỗng để giảm nhiễu
    text_list = [para.text for para in doc.paragraphs if para.text.strip()]
    full_text = "\n".join(text_list)
    return full_text


def read_pdf_file(file):
    """
    Đọc file .pdf bằng pdfplumber.
    Ưu điểm: Xử lý tiếng Việt tốt, ít bị lỗi font đè chữ.
    """
    text = ""
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                # extract_text của pdfplumber thông minh hơn PyPDF2
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Lỗi khi đọc PDF: {e}")
        return ""

    return text


def load_file(uploaded_file):
    """
    Hàm main điều phối việc đọc file dựa trên đuôi mở rộng.
    Input: uploaded_file (đối tượng file từ Streamlit)
    """
    filename = uploaded_file.name
    ext = os.path.splitext(filename)[-1].lower()

    if ext == ".txt":
        return read_text_file(uploaded_file)
    elif ext == ".docx":
        return read_docx_file(uploaded_file)
    elif ext == ".pdf":
        return read_pdf_file(uploaded_file)
    else:
        raise ValueError(f"Định dạng file không hỗ trợ: {ext}")
