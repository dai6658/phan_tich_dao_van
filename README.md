#  HỆ THỐNG PHÁT HIỆN ĐẠO VĂN TIẾNG VIỆT

Một ứng dụng **phát hiện đạo văn** ngôn ngữ Tiếng Việt sử dụng mô hình **Sentence-BERT** (`bkai-foundation-models/vietnamese-bi-encoder`), kết hợp các kỹ thuật:

* Tiền xử lý văn bản
* Vector hóa ngữ nghĩa
* So sánh Cosine Similarity
* Phát hiện câu trùng lặp, đạo văn

Giao diện chạy trên **Streamlit**, cho phép người dùng tải lên:

* **1 file nghi vấn**
* **1 hoặc nhiều file tham chiếu**
* **1 file zip chứa các tệp văn bản**
---

##  Cấu trúc hệ thống

```
project/
├── streamlits.py                # Giao diện Streamlit chính
├── file_loader.py               # Đọc file txt, docx, pdf
├── sentence_splitter.py         # Tách câu Tiếng Việt (underthesea)
├── preprocessing.py             # Tiền xử lý câu
├── embedding.py                 # Vector hóa với Sentence-BERT
├── similarity.py                # Tính cosine similarity
├── plagiarism_detector.py       # Phát hiện đạo văn
├── requirements.txt             # Danh sách thư viện Python cần cài
├── web_search.py                # Web search cho tính năng so sánh online
├── scan_history.db              # lịch sử các lần scan
└── README.md                    # Tài liệu hướng dẫn
```

---

##  Cài đặt

 Clone source về:

```bash
git clone <repository_url>
cd project
```

 Tạo environment (khuyên dùng):

```bash
python -m venv venv
source venv/bin/activate  # (Linux, Mac)
venv\Scripts\activate     # (Windows)
```

3️ Cài đặt thư viện:

```bash
pip install -r requirements.txt
```

---

##  Chạy ứng dụng

```bash
streamlit run streamlits.py
```

Giao diện web sẽ mở ở:

```
http://localhost:8501
```

---

##  Hướng dẫn sử dụng
 **Chọn chế độ** 
 **Chọn file nghi vấn**
 **Chọn các file tham chiếu /chế độ search**
 **Điều chỉnh ngưỡng cosine similarity**
 **Nhấn "Phát hiện đạo văn"**
 Kết quả:

* Hiển thị tỷ lệ đạo văn
* Danh sách câu nghi vấn và câu nguồn trùng
* Cảnh báo nếu có dấu hiệu đạo văn toàn phần

---

##  Công nghệ sử dụng

* **Python 3.13**
* [Streamlit](https://streamlit.io/)
* [SentenceTransformers](https://www.sbert.net/)
* [Underthesea](https://github.com/undertheseanlp/underthesea)
* PyPDF2, python-docx, scikit-learn

---

##  Bản quyền

Dành cho mục đích **giáo dục, nghiên cứu**, không khuyến khích sử dụng thương mại mà chưa có sự đồng ý.
