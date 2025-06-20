import re
from underthesea import word_tokenize
from underthesea import text_normalize

def load_stopwords(file_path):
    """
    Đọc danh sách stopwords từ file .txt (1 từ/cụm từ mỗi dòng)
    Trả về set các stopword
    """
    with open(file_path, "r", encoding="utf-8") as f:
        stopwords = set(line.strip() for line in f if line.strip())
    return stopwords


def preprocess_text(text, stopwords=None):
    """
    Tiền xử lý 1 câu tiếng Việt để chuẩn bị embedding:
    - Chuyển về chữ thường
    - chuẩn hóa bằng text normalize
    - Loại bỏ ký tự đặc biệt (giữ tiếng Việt)
    - Tách từ bằng underthesea
    - Lọc stopword (nếu có)

    Trả về chuỗi đã tiền xử lý
    """
    text = text.lower()
    text=text_normalize(text)
    text = re.sub(r"[^a-zA-Z0-9À-ỹ\s]", "", text)
    tokenized_text_with_underscores = word_tokenize(text, format="text")
    tokens = tokenized_text_with_underscores.split()
    tokens = [t for t in tokens if not stopwords or t not in stopwords]
    return " ".join(tokens)


# --- Test ---
if __name__ == "__main__":
    stopwords_vn = load_stopwords("vietnamese-stopwords.txt")

    sample_sentence = "Blockchain được ứng dụng để xác thực nguồn gốc sản phẩm"

    cleaned = preprocess_text(sample_sentence, stopwords=stopwords_vn)

    print("Sau khi tiền xử lý:", cleaned)
