from underthesea import word_tokenize, text_normalize


def preprocess_for_vector(text):
    """
    Tiền xử lý TỐI ƯU CHO MÔ HÌNH VECTOR (AI):
    - KHÔNG xóa dấu câu và stopword để AI hiểu trọn vẹn ngữ cảnh và cấu trúc câu.
    - Chỉ thực hiện chuẩn hóa Unicode (vd: òa -> oà).
    - Thực hiện Word Segmentation (nối từ ghép bằng dấu _).
      (Ví dụ: "Học sinh" -> "Học_sinh" - Bắt buộc đối với model BKAI).
    """
    # 1. Chuẩn hóa Unicode tiếng Việt
    text = text_normalize(text)

    # 2. Tách từ tiếng Việt (format="text" sẽ tự động thêm dấu _)
    # Quá trình này tự động giữ lại nguyên vẹn dấu chấm, phẩy...
    text_segmented = word_tokenize(text, format="text")

    return text_segmented


# --- Test ---
if __name__ == "__main__":
    sample_sentence = "Tuy nhiên, AI không thể hoàn toàn thay thế con người."
    cleaned = preprocess_for_vector(sample_sentence)
    # Kết quả kỳ vọng: "Tuy_nhiên , AI không_thể hoàn_toàn thay_thế con_người ."
    print("Sau khi tiền xử lý cho Vector:", cleaned)
