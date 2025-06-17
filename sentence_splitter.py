from underthesea import sent_tokenize

def split_sentences(text):
    """
    Tách một đoạn văn thành danh sách các câu tiếng Việt
    Sử dụng thư viện underthesea để đảm bảo tách đúng ngữ pháp
    """
    return sent_tokenize(text)

if __name__ == "__main__":
    sample_text = """
    Xử lý ngôn ngữ tự nhiên là một lĩnh vực của trí tuệ nhân tạo.
    Nó giúp máy tính hiểu và xử lý ngôn ngữ con người.
    Các ứng dụng phổ biến gồm dịch máy, chatbot, và phân tích cảm xúc.
    """
    sentences = split_sentences(sample_text)
    for i, sentence in enumerate(sentences, 1):
        print(f"Câu {i}: {sentence}")
