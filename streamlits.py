import streamlit as st
from file_loader import load_file
from sentence_splitter import split_sentences
from preprocessing import preprocess_text
from embedding import encode_sentences
from similarity import find_similar_pairs
from plagiarism_detector import detect_plagiarism
import os

st.set_page_config(page_title="Phát hiện đạo văn", layout="wide")
st.title("  Hệ thống phát hiện đạo văn tiếng Việt")

# --- Tải file nghi vấn và các file nguồn ---
file_nghi_van = st.file_uploader("  Chọn file nghi vấn", type=["txt", "docx", "pdf"])
files_nguon = st.file_uploader(" Chọn các file tham chiếu", type=["txt", "docx", "pdf"], accept_multiple_files=True)

# --- Tham số ---
threshold = st.slider(" Ngưỡng đạo văn (cosine similarity)", 0.5, 1.0, 0.85, 0.01)

# --- Nút xử lý ---
if st.button("  Phát hiện đạo văn"):
    if file_nghi_van and files_nguon:
        # Đọc file nghi vấn
        text_nghi_van = load_file(file_nghi_van)
        filename_nghi_van = file_nghi_van.name

        # Tách câu + Tiền xử lý + Vector hóa
        sents_nghi_van = split_sentences(text_nghi_van)
        sents_nghi_van_clean = [preprocess_text(s) for s in sents_nghi_van]
        vecs_nghi_van = encode_sentences(sents_nghi_van_clean)

        # --- So sánh với từng file tham chiếu ---
        for file_nguon in files_nguon:
            text_nguon = load_file(file_nguon)
            filename_nguon = file_nguon.name

            sents_nguon = split_sentences(text_nguon)
            sents_nguon_clean = [preprocess_text(s) for s in sents_nguon]
            vecs_nguon = encode_sentences(sents_nguon_clean)

            similar_pairs = find_similar_pairs(vecs_nghi_van, vecs_nguon, threshold=threshold)
            results, rate = detect_plagiarism(sents_nghi_van, sents_nguon, similar_pairs)

            # --- Hiển thị kết quả ---
            st.markdown(f"##  So sánh giữa:")
            st.write(f"- **File nghi vấn:** `{filename_nghi_van}` ({len(sents_nghi_van)} câu)")
            st.write(f"- **File tham chiếu:** `{filename_nguon}` ({len(sents_nguon)} câu)")
            st.write(f"- **Số câu bị nghi đạo văn:** `{len(results)}`")
            st.write(f"- **Tỷ lệ câu nghi đạo văn:** `{rate:.2%}`")

            if rate >= 0.3:
                st.error(" CẢNH BÁO: Văn bản có dấu hiệu ĐẠO VĂN toàn phần!")
            else:
                st.success("Văn bản KHÔNG có dấu hiệu đạo văn toàn phần.")

            st.markdown("---")
            st.subheader(" Chi tiết các câu bị nghi đạo văn:")

            for i, (c1, c2, sc) in enumerate(results):
                st.markdown(
                    f"**{i+1}.** Câu nghi vấn: \"{c1}\"<br/>↪ Trùng với: \"{c2}\"<br/> Cosine Similarity: `{sc:.2f}`",
                    unsafe_allow_html=True
                )
            st.markdown("---")

    else:
        st.warning(" Vui lòng chọn **1 file nghi vấn** và **ít nhất 1 file tham chiếu** để so sánh.")
