from sentence_transformers import SentenceTransformer

def load_embedding_model():
    """
    Load model AI. Hàm này tách biệt để Streamlit có thể cache.
    Sử dụng model Bi-encoder của BKAI tối ưu cho tiếng Việt.
    """
    return SentenceTransformer('bkai-foundation-models/vietnamese-bi-encoder')

def encode_sentences(sentences, model, batch_size=32):
    """
    Mã hóa danh sách câu thành vector.
    - batch_size=32: Tối ưu cho máy tính không có GPU mạnh, chống tràn RAM.
    - show_progress_bar=False: Giúp Streamlit không bị in rác ra terminal.
    """
    if not sentences:
        return []
    return model.encode(sentences, batch_size=batch_size, show_progress_bar=False)

if __name__ == "__main__":
    # Test local
    print("Đang tải model để test...")
    test_model = load_embedding_model()
    sample = ["Kiểm tra thử nghiệm"]
    vec = encode_sentences(sample, test_model)
    print(f"Embedding shape: {vec.shape}")
