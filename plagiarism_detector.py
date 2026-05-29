def detect_plagiarism(sentences_1, sentences_2, similar_pairs):

    results = []
    # Dùng set để đếm số câu đạo văn duy nhất (tránh 1 câu map với nhiều câu nguồn)
    plagiarized_indices = set()

    for i, j, cosine_score in similar_pairs:
        s1 = sentences_1[i]
        s2 = sentences_2[j]

        # Lọc nhiễu: Bỏ qua các câu quá ngắn (dưới 3 từ) để tránh bắt nhầm
        if len(s1.split()) < 3:
            continue

        results.append((s1, s2, cosine_score))
        plagiarized_indices.add(i)

    # Tính tỷ lệ đạo văn trên tổng số câu của văn bản nghi vấn
    total_sentences = len(sentences_1)
    rate = len(plagiarized_indices) / total_sentences if total_sentences > 0 else 0

    return results, rate
