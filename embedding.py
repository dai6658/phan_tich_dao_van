from sentence_transformers import SentenceTransformer

model = SentenceTransformer('keepitreal/vietnamese-sbert')

def encode_sentences(sentences):
    """
    Mã hóa danh sách câu thành danh sách vector ngữ nghĩa
    Đầu vào: List[str]  ← các câu đã tiền xử lý
    Đầu ra: List[ndarray] ← vector dạng numpy
    """
    return model.encode(sentences)

if __name__ == "__main__":
    sample_sentences = [
        "xử_lý ngôn_ngữ tự_nhiên",
        "ngôn_ngữ học máy tính",
        "máy học và trí tuệ nhân tạo"
    ]
    vectors = encode_sentences(sample_sentences)
    for i, vec in enumerate(vectors):
        print(f"Câu {i+1} vector hóa: {vec[:5]} ...")  # In 5 phần tử đầu mỗi vector
