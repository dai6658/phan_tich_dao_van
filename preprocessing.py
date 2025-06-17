import re
from underthesea import word_tokenize

def preprocess_text(text):
    """
    Tiền xử lý 1 câu tiếng Việt để chuẩn bị đưa vào mô hình embedding:
    - Chuyển về chữ thường
    - Loại bỏ ký tự đặc biệt
    - Tách từ bằng underthesea
    - (Tùy chọn) Loại bỏ stopword (nếu có)
    """
    text = text.lower()  # Chuyển về chữ thường
    text = re.sub(r"[^a-zA-Z0-9À-ỹ\s]", "", text)  # Bỏ ký tự đặc biệt nhưng giữ tiếng Việt
    tokens = word_tokenize(text, format="text")      # Tách từ bằng underthesea (format="text" để có dạng chuỗi)
    return tokens

if __name__ == "__main__":
    sample_sentence = "Xử lý ngôn ngữ tự nhiên (NLP) giúp máy hiểu tiếng Việt!"
    cleaned = preprocess_text(sample_sentence)
    print("Sau khi tiền xử lý:", cleaned)