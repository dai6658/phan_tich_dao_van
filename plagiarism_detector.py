def detect_plagiarism(sentences_1, sentences_2, similar_pairs):
    """
    Nhận vào:
    - sentences_1: list câu trong file nghi vấn
    - sentences_2: list câu trong file tham chiếu
    - similar_pairs: list các tuple (i, j, score) từ hàm find_similar_pairs

    Trả về:
    - danh sách chi tiết các câu bị nghi đạo văn: (câu nghi vấn, câu nguồn, điểm cosine)
    - tỉ lệ đạo văn trên tổng số câu nghi vấn
    """
    results = []
    for i, j, score in similar_pairs:
        results.append((sentences_1[i], sentences_2[j], score))

    plagiarism_rate = len(set([i for i, _, _ in similar_pairs])) / len(sentences_1)
    return results, plagiarism_rate

if __name__ == "__main__":
    sent_1 = ["tôi yêu lập trình", "xử lý ngôn ngữ tự nhiên là hay", "đây là câu khác"]
    sent_2 = ["tôi yêu lập trình", "xử lý ngôn ngữ tự nhiên"]
    similar = [(0, 0, 0.99), (1, 1, 0.89)]

    matched, rate = detect_plagiarism(sent_1, sent_2, similar)

    print("Các câu bị nghi đạo văn:")
    for s1, s2, score in matched:
        print(f'- "{s1}" bị nghi sao chép từ "{s2}" (Cosine: {score:.2f})')

    print(f"\n Tỉ lệ đạo văn: {rate:.2%}")