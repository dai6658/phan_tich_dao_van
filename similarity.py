from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def compute_similarity_matrix(vectors_1, vectors_2):
    """
    So sánh tất cả vector trong vectors_1 với vectors_2
    Trả về ma trận similarity (shape: len(vectors_1) x len(vectors_2))
    """
    return cosine_similarity(vectors_1, vectors_2)

def find_similar_pairs(vectors_1, vectors_2, threshold=0.85):
    """
    Tìm các cặp câu có cosine similarity >= threshold
    Trả về danh sách tuple: (chỉ số câu 1, chỉ số câu 2, điểm giống nhau)
    """
    sim_matrix = compute_similarity_matrix(vectors_1, vectors_2)
    similar_pairs = []
    for i in range(sim_matrix.shape[0]):
        for j in range(sim_matrix.shape[1]):
            score = sim_matrix[i][j]
            if score >= threshold:
                similar_pairs.append((i, j, score))
    return similar_pairs

if __name__ == "__main__":
    # 3 vector mẫu (giả lập): câu 1 gần câu 2, câu 3 khác hẳn
    vectors_1 = np.array([
        [0.1, 0.3, 0.5],
        [0.1, 0.31, 0.49],
        [0.9, -0.5, 0.2]
    ])
    vectors_2 = vectors_1.copy()

    results = find_similar_pairs(vectors_1, vectors_2, threshold=0.98)
    for i, j, score in results:
        print(f"Câu {i+1} ↔ Câu {j+1} | Cosine: {score:.4f}")
