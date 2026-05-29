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
    Tìm các cặp câu có cosine similarity >= threshold.

    TỐI ƯU HÓA:
    - Sử dụng np.where để lọc chỉ số thay vì dùng 2 vòng for lồng nhau.
    - Giảm độ phức tạp từ O(N*M) trong Python thuần xuống tốc độ C của NumPy.

    Trả về: List[Tuple(int, int, float)] -> (index_nghi_van, index_nguon, score)
    """
    # 1. Tính ma trận tương đồng
    sim_matrix = compute_similarity_matrix(vectors_1, vectors_2)

    # 2. Lấy các tọa độ (hàng, cột) có giá trị >= threshold
    # rows tương ứng với chỉ số trong vectors_1 (nghi vấn)
    # cols tương ứng với chỉ số trong vectors_2 (nguồn)
    rows, cols = np.where(sim_matrix >= threshold)

    # 3. Lấy giá trị score tương ứng tại các tọa độ đó
    scores = sim_matrix[rows, cols]

    # 4. Đóng gói thành danh sách các tuple
    similar_pairs = list(zip(rows, cols, scores))

    return similar_pairs


if __name__ == "__main__":
    # Test nhanh hiệu năng và độ chính xác
    print("--- Test Similarity Optimization ---")

    # Tạo dữ liệu giả lập (3 câu nghi vấn x 3 câu nguồn)
    vectors_1 = np.array([
        [0.1, 0.3, 0.5],
        [0.9, 0.1, 0.0],  # Giống vector tương ứng bên dưới
        [0.5, 0.5, 0.5]
    ])

    # Vectors nguồn (giả sử giống hệt để test độ trùng)
    vectors_2 = vectors_1.copy()

    # Chạy thử
    results = find_similar_pairs(vectors_1, vectors_2, threshold=0.99)

    print(f"Tìm thấy {len(results)} cặp giống nhau (Threshold 0.99):")
    for i, j, score in results:
        print(f"Câu {i} (Nghi vấn) <--> Câu {j} (Nguồn) | Score: {score:.4f}")
