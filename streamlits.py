import streamlit as st
import pandas as pd
import os
import zipfile
import io
import itertools
import sqlite3
import plotly.express as px
from datetime import datetime

# --- Import modules ---
from file_loader import load_file
from sentence_splitter import split_sentences
from preprocessing import preprocess_for_vector
from embedding import load_embedding_model, encode_sentences
from similarity import find_similar_pairs
from plagiarism_detector import detect_plagiarism
from web_search import get_smart_queries, search_internet, fetch_url_content
import cloudscraper

# ==========================================
# CÁC HÀM XỬ LÝ DATABASE (SQLITE)
# ==========================================
def init_history_db():
    conn = sqlite3.connect('scan_history.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS scan_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_date TEXT, scan_mode TEXT, file_name TEXT,
                    plagiarism_rate TEXT, note TEXT
                )''')
    conn.commit()
    conn.close()


def add_history_record(scan_mode, file_name, plagiarism_rate, note=""):
    conn = sqlite3.connect('scan_history.db')
    c = conn.cursor()
    current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    c.execute(
        "INSERT INTO scan_history (scan_date, scan_mode, file_name, plagiarism_rate, note) VALUES (?, ?, ?, ?, ?)",
        (current_time, scan_mode, file_name, plagiarism_rate, note))
    conn.commit()
    conn.close()


def load_history_df():
    conn = sqlite3.connect('scan_history.db')
    df = pd.read_sql_query(
        "SELECT scan_date as 'Thời gian', scan_mode as 'Chế độ', file_name as 'Tên File', plagiarism_rate as 'Tỷ lệ vi phạm', note as 'Ghi chú' FROM scan_history ORDER BY id DESC",
        conn)
    conn.close()
    return df


def clear_history():
    conn = sqlite3.connect('scan_history.db')
    c = conn.cursor()
    c.execute("DELETE FROM scan_history")
    conn.commit()
    conn.close()


init_history_db()


class VirtualFile(io.BytesIO):
    def __init__(self, buffer, name):
        super().__init__(buffer)
        self.name = name


# --- Cấu hình trang ---
st.set_page_config(page_title="Phát hiện đạo văn", layout="wide")

st.title(" Hệ thống phát hiện đạo văn")
st.markdown("Hệ thống so sánh văn bản nghi vấn với dữ liệu nguồn (Local/Internet) hoặc kiểm tra chéo nội bộ lớp học.")

st.markdown("""
<style>
    .stDataFrame {font-size: 14px;}
    .report-card { 
        background-color: #ffffff; 
        border: 1px solid #e0e0e0; 
        padding: 15px; 
        border-radius: 8px; 
        margin-bottom: 10px; 
        color: #2c3e50; 
    }
    .suspect-text { color: #c0392b; font-weight: 600; font-size: 1.05em;}
    .source-text { color: #2980b9; font-style: italic; font-weight: 500;}
</style>
""", unsafe_allow_html=True)


# --- CACHE MODEL ---
@st.cache_resource
def get_ai_model():
    with st.spinner("Đang khởi tạo AI Model..."):
        return load_embedding_model()


model = get_ai_model()

# --- Sidebar ---
# --- Sidebar ---
with st.sidebar:
    st.header(" Cấu hình AI")
    threshold = st.slider("Ngưỡng Vector Cosine", 0.5, 1.0, 0.70, 0.01)
    st.info(f"Logic: Báo cáo vi phạm khi điểm Vector > {threshold}")

# ==========================================
# CHIA TAB GIAO DIỆN
# ==========================================
tab1, tab2, tab3 = st.tabs([" Kiểm tra Đơn lẻ (1 Bài)", " Kiểm tra Chéo (Lô/Zip)", " Lịch sử quét"])

# ------------------------------------------
# TAB 1: KIỂM TRA ĐƠN LẺ
# ------------------------------------------
with tab1:
    col_1, col_2 = st.columns([1, 1])
    with col_1:
        st.subheader("1. Văn bản cần kiểm tra")
        file_nghi_van = st.file_uploader("Upload file nghi vấn", type=["txt", "docx", "pdf"])

    text_nghi_van = ""
    if file_nghi_van:
        try:
            text_nghi_van = load_file(file_nghi_van)
            st.success(f" Đã tải: {file_nghi_van.name}")
        except Exception as e:
            st.error(f"Lỗi đọc file: {e}")

    with col_2:
        st.subheader("2. Nguồn đối chiếu")
        check_mode = st.radio("Chế độ:", ("Local Files", "Online Search"), horizontal=True)

    source_data = []

    if check_mode == "Local Files":
        files_nguon = st.file_uploader("Upload file nguồn", type=["txt", "docx", "pdf"], accept_multiple_files=True)
        if files_nguon:
            for f in files_nguon:
                try:
                    content = load_file(f)
                    if content.strip(): source_data.append((f.name, content))
                except Exception as e:
                    st.warning(f"Lỗi đọc {f.name}: {e}")


    elif check_mode == "Online Search":

        if 'web_sources' not in st.session_state:
            st.session_state['web_sources'] = []

        if 'current_file_name' not in st.session_state:
            st.session_state['current_file_name'] = ""

        # Tự động xóa nguồn Internet cũ nếu upload file mới

        if file_nghi_van and file_nghi_van.name != st.session_state['current_file_name']:
            st.session_state['web_sources'] = []

            st.session_state['current_file_name'] = file_nghi_van.name

        if text_nghi_van and st.button("Quét Internet ngay", type="primary", key="btn_scan_web"):
            with st.status("Đang rà soát Internet...", expanded=True) as status:
                sentences = split_sentences(text_nghi_van)
                queries = get_smart_queries(sentences)
                urls = search_internet(queries)

                if urls:
                    new_sources = []
                    prog = st.progress(0)
                    for i, url in enumerate(urls):
                        c = fetch_url_content(url)
                        if c and len(c) > 200: new_sources.append((url, c))
                        prog.progress((i + 1) / len(urls))

                    st.session_state['web_sources'] = new_sources
                    status.update(label=f"Đã tải {len(new_sources)} nguồn!", state="complete")
                else:
                    status.update(label="Không tìm thấy kết quả.", state="error")

        if st.session_state['web_sources']:
            source_data = st.session_state['web_sources']
            with st.expander(f"Xem {len(source_data)} nguồn online"):
                for url, _ in source_data: st.write(f"- {url}")

    if st.button(" BẮT ĐẦU PHÂN TÍCH", type="primary", width="stretch", key="btn_analyze_single"):
        if not text_nghi_van or not source_data:
            st.error("Thiếu dữ liệu (File nghi vấn hoặc Nguồn)!")
        else:
            st.divider()
            with st.spinner("Đang mã hóa vector văn bản của bạn..."):
                sents_nv = split_sentences(text_nghi_van)
                sents_nv_clean = [preprocess_for_vector(s) for s in sents_nv]
                # THÊM BATCH_SIZE=32
                vecs_nv = encode_sentences(sents_nv_clean, model, batch_size=32)

            total_plagiarized_sents = set()
            all_matches_data = []
            my_bar = st.progress(0, text="Đang so sánh...")

            for idx, (name_src, text_src) in enumerate(source_data):
                sents_src = split_sentences(text_src)
                if not sents_src: continue
                ##with st.expander(f" DEBUG: Xem nội dung gốc cào từ {name_src}"):
                    ##st.write(sents_src)

                vecs_src = encode_sentences([preprocess_for_vector(s) for s in sents_src], model, batch_size=32)

                sim_pairs = find_similar_pairs(vecs_nv, vecs_src, threshold=threshold)


                results, rate = detect_plagiarism(sents_nv, sents_src, sim_pairs)

               
                if results:
                    # Sắp xếp kết quả theo điểm Vector Cosine (x[2]) từ cao xuống thấp
                    results.sort(key=lambda x: x[2], reverse=True)
                    
                    filtered_results = []
                    seen_s1 = set() # Tập hợp lưu vết các câu đã hiển thị
                    
                    for s1, s2, cos in results:
                        if s1 not in seen_s1: # Nếu câu này chưa từng xuất hiện
                            filtered_results.append((s1, s2, cos))
                            seen_s1.add(s1)   # Đánh dấu là đã xuất hiện
                            
                    results = filtered_results # Cập nhật lại danh sách kết quả cuối cùng
                # --- KẾT THÚC BỘ LỌC ---

                if results:
                    with st.expander(f"️Phát hiện từ: {name_src} ({len(results)} câu)", expanded=False):
                        for s1, s2, cos in results:
                            total_plagiarized_sents.add(s1)
                            # ... (Các đoạn code HTML phía dưới giữ nguyên) ...
                            all_matches_data.append({
                                "Câu của bạn": s1, "Câu Nguồn": s2, "Nguồn": name_src,
                                "Vector": round(cos, 3)
                            })

                            st.markdown(f"""
                                            <div class="report-card">
                                                <div style="margin-bottom: 4px;"> <span class="suspect-text">{s1}</span></div>
                                                <div style="margin-bottom: 8px;"><span class="source-text">{s2}</span></div>
                                                <div style="display:flex; gap:10px; font-size:0.85em;">
                                                    <span style="background:#e6f7ff; padding:2px 8px; border-radius:4px; color:#0050b3; border:1px solid #91d5ff">
                                                         Cosine similarity: {cos:.2f}
                                                    </span>
                                                </div>
                                            </div>
                                            """, unsafe_allow_html=True)
                my_bar.progress((idx + 1) / len(source_data))

            my_bar.empty()
            rate_total = len(total_plagiarized_sents) / len(sents_nv) if sents_nv else 0

            add_history_record(
                scan_mode="Kiểm tra đơn lẻ",
                file_name=file_nghi_van.name,
                plagiarism_rate=f"{rate_total:.1%}",
                note=f"Phát hiện {len(total_plagiarized_sents)} câu vi phạm"
            )

            if all_matches_data:
                st.subheader(" Kết quả chi tiết")
                df_matches = pd.DataFrame(all_matches_data)

                viz_col1, viz_col2 = st.columns([1, 1])

                with viz_col1:
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Tổng câu kiểm tra", len(sents_nv))
                    c2.metric("Số câu vi phạm", len(total_plagiarized_sents))
                    c3.metric("Tỷ lệ", f"{rate_total:.1%}")

                    st.download_button(
                        label=" Tải báo cáo (.csv)",
                        data=df_matches.to_csv(index=False).encode('utf-8-sig'),
                        file_name='bao_cao_don.csv',
                        mime='text/csv',
                        width="stretch"
                    )

                with viz_col2:
                    plot_data = pd.DataFrame({
                        "Trạng thái": ["Trùng lặp", "Duy nhất"],
                        "Số lượng": [len(total_plagiarized_sents), len(sents_nv) - len(total_plagiarized_sents)]
                    })
                    fig = px.pie(
                        plot_data, values='Số lượng', names='Trạng thái', color='Trạng thái',
                        color_discrete_map={'Trùng lặp': '#e74c3c', 'Duy nhất': '#2ecc71'},
                        hole=0.4
                    )
                    fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=200)
                    st.plotly_chart(fig, width='stretch')

                st.dataframe(df_matches, width='stretch')
            else:
                st.success(" Không tìm thấy đạo văn!")

# ------------------------------------------
# TAB 2: KIỂM TRA CHÉO (ZIP BATCH)
# ------------------------------------------
with tab2:
    st.subheader("Quét chéo sinh viên trong lớp")
    zip_upload = st.file_uploader("Tải lên file ZIP bài tập", type=["zip"])

    if zip_upload and st.button("Bắt đầu Quét Chéo", type="primary"):
        st.divider()
        files_dict = {}

        with st.status("Đang giải nén và đọc nội dung...", expanded=True) as zip_status:
            with zipfile.ZipFile(zip_upload) as z:
                for file_info in z.infolist():
                    if file_info.is_dir() or file_info.filename.startswith('__MACOSX'): continue
                    ext = os.path.splitext(file_info.filename)[-1].lower()

                    if ext in [".txt", ".docx", ".pdf"]:
                        with z.open(file_info) as f:
                            filename = os.path.basename(file_info.filename)
                            vfile = VirtualFile(f.read(), filename)
                            try:
                                text = load_file(vfile)
                                if text.strip(): files_dict[filename] = text
                            except Exception as e:
                                st.warning(f"Bỏ qua {filename}: Lỗi đọc ({e})")
            zip_status.update(label=f"Đã đọc thành công {len(files_dict)} file!", state="complete")

        if len(files_dict) < 2:
            st.error("Cần ít nhất 2 file hợp lệ trong thư mục Zip để quét chéo!")
        else:
            parsed_data = {}
            encode_bar = st.progress(0, text="Đang mã hóa Vector AI cho các bài tập...")

            items = list(files_dict.items())
            for i, (fname, ftext) in enumerate(items):
                sents = split_sentences(ftext)
                sents_clean = [preprocess_for_vector(s) for s in sents]
                # THÊM BATCH_SIZE=32
                vecs = encode_sentences(sents_clean, model, batch_size=32)
                parsed_data[fname] = {'sents': sents, 'vecs': vecs}
                encode_bar.progress((i + 1) / len(items))
            encode_bar.empty()

            cross_matches = []
            file_names = list(parsed_data.keys())
            pairs = list(itertools.combinations(file_names, 2))

            compare_bar = st.progress(0, text="Đang bắt cặp so sánh chéo...")

            for i, (file_A, file_B) in enumerate(pairs):
                sents_A, vecs_A = parsed_data[file_A]['sents'], parsed_data[file_A]['vecs']
                sents_B, vecs_B = parsed_data[file_B]['sents'], parsed_data[file_B]['vecs']

                if not sents_A or not sents_B: continue

                sim_pairs = find_similar_pairs(vecs_A, vecs_B, threshold=threshold)
                results, _ = detect_plagiarism(sents_A, sents_B, sim_pairs)

                # --- BẮT ĐẦU BỘ LỌC UI CHO TAB 2 ---
                if results:
                    results.sort(key=lambda x: x[2], reverse=True)
                    filtered_results = []
                    seen_s1 = set()
                    
                    for s1, s2, cos in results:
                        if s1 not in seen_s1:
                            filtered_results.append((s1, s2, cos))
                            seen_s1.add(s1)
                            
                    results = filtered_results
                # --- KẾT THÚC BỘ LỌC ---

                if results:
                    for s1, s2, cos in results:
                        cross_matches.append({
                            "Bài A": file_A, "Bài B": file_B,
                            "Câu Bài A": s1, "Câu Bài B": s2,
                            "Vector": round(cos, 3)
                        })
                compare_bar.progress((i + 1) / len(pairs))
            compare_bar.empty()

            st.subheader(f"Kết quả kiểm tra chéo ({len(files_dict)} bài)")

            if cross_matches:
                df_cross = pd.DataFrame(cross_matches)
                summary_df = df_cross.groupby(['Bài A', 'Bài B']).size().reset_index(name='Số câu giống nhau')


                def calc_plagiarism_rate(row, file_col):
                    filename = row[file_col]
                    total_sents = len(parsed_data[filename]['sents'])
                    if total_sents == 0: return 0.0
                    return row['Số câu giống nhau'] / total_sents


                summary_df['Tỷ lệ đạo (Bài A)'] = summary_df.apply(lambda r: calc_plagiarism_rate(r, 'Bài A'), axis=1)
                summary_df['Tỷ lệ đạo (Bài B)'] = summary_df.apply(lambda r: calc_plagiarism_rate(r, 'Bài B'), axis=1)
                summary_df = summary_df.sort_values(by='Số câu giống nhau', ascending=False)

                add_history_record(
                    scan_mode="Kiểm tra chéo lớp (Zip)",
                    file_name=zip_upload.name,
                    plagiarism_rate="N/A",
                    note=f"Phát hiện {len(summary_df)} cặp bài chép của nhau"
                )

                st.write("### Bảng tóm tắt các cặp vi phạm")
                st.dataframe(
                    summary_df, width='stretch',
                    column_config={
                        "Bài A": st.column_config.TextColumn("Sinh viên A", width="medium"),
                        "Bài B": st.column_config.TextColumn("Sinh viên B", width="medium"),
                        "Số câu giống nhau": st.column_config.NumberColumn("Số câu trùng", format="%d"),
                        "Tỷ lệ đạo (Bài A)": st.column_config.ProgressColumn("% Đạo (A)", format="%.2f", min_value=0,
                                                                             max_value=1),
                        "Tỷ lệ đạo (Bài B)": st.column_config.ProgressColumn("% Đạo (B)", format="%.2f", min_value=0,
                                                                             max_value=1)
                    }
                )

                st.write("### Chi tiết đối chiếu từng cặp")

                st.download_button(
                    label="Tải toàn bộ dữ liệu chéo (.csv)",
                    data=df_cross.to_csv(index=False).encode('utf-8-sig'),
                    file_name='bao_cao_cheo_lop.csv',
                    mime='text/csv',
                    width = "stretch"
                )
                st.markdown("<br>", unsafe_allow_html=True)

                for index, row in summary_df.iterrows():
                    file_a, file_b = row['Bài A'], row['Bài B']
                    num_matches, rate_a, rate_b = row['Số câu giống nhau'], row['Tỷ lệ đạo (Bài A)'], row[
                        'Tỷ lệ đạo (Bài B)']

                    expander_title = f"{file_a} (Đạo {rate_a:.1%}) {file_b} (Đạo {rate_b:.1%}) | Trùng {num_matches} câu"
                    with st.expander(expander_title, expanded=False):
                        pair_data = df_cross[(df_cross['Bài A'] == file_a) & (df_cross['Bài B'] == file_b)]

                        for _, match_row in pair_data.iterrows():
                            s1, s2, cos = match_row['Câu Bài A'], match_row['Câu Bài B'], match_row['Vector']

                            st.markdown(f"""
                                                        <div class="report-card">
                                                            <div style="margin-bottom: 4px;"> <b>{file_a}:</b> <span class="suspect-text">{s1}</span></div>
                                                            <div style="margin-bottom: 8px;"> <b>{file_b}:</b> <span class="source-text">{s2}</span></div>
                                                            <div style="display:flex; gap:10px; font-size:0.85em;">
                                                                <span style="background:#e6f7ff; padding:2px 8px; border-radius:4px; color:#0050b3; border:1px solid #91d5ff">
                                                                     Vector: {cos:.2f}
                                                                </span>
                                                            </div>
                                                        </div>
                                                    """, unsafe_allow_html=True)
            else:
                st.success("Tuyệt vời! Không phát hiện sinh viên nào chép bài của nhau.")
                add_history_record(
                    scan_mode="Kiểm tra chéo lớp (Zip)",
                    file_name=zip_upload.name,
                    plagiarism_rate="0%",
                    note="Không phát hiện vi phạm chéo"
                )

# ------------------------------------------
# TAB 3: LỊCH SỬ QUÉT
# ------------------------------------------
with tab3:
    st.subheader("Lịch sử các lần phân tích")
    st.info("Hệ thống tự động lưu lại thông tin tổng quan của các lần quét để bạn tiện theo dõi.")

    col_btn1, col_btn2 = st.columns([1, 8])
    with col_btn1:
        if st.button("Xóa lịch sử", type="secondary"):
            clear_history()
            st.rerun()

    df_history = load_history_df()

    if not df_history.empty:
        st.dataframe(df_history, width='stretch')
        st.download_button(
            label="Tải file Nhật ký (CSV)",
            data=df_history.to_csv(index=False).encode('utf-8-sig'),
            file_name='nhat_ky_quet_dao_van.csv',
            mime='text/csv',
            width = "stretch"
        )
    else:
        st.write("Trống. Bạn chưa thực hiện lần quét nào.")
