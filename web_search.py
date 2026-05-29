import time
import random
import requests
from bs4 import BeautifulSoup
import trafilatura
from ddgs import DDGS
from fake_useragent import UserAgent
import urllib.parse
import cloudscraper
try:
    ua = UserAgent()
except:
    ua = None


def get_random_headers():
    user_agent = ua.random if ua else 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    return {
        'User-Agent': user_agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Referer': 'https://www.google.com/',
        'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7'
    }

def search_google_manual(query, max_results=3):
    print(f"   ->  Chuyển sang Google (Manual) cho: [{query}]...")
    urls = set()
    search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&num={max_results + 5}&hl=vi"
    try:
        response = requests.get(search_url, headers=get_random_headers(), timeout=10)
        if response.status_code == 429:
            print("   ->  Google chặn IP (429 Too Many Requests).")
            return []
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            all_links = soup.find_all('a', href=True)
            for a in all_links:
                link = a['href']
                if link.startswith('/url?q='):
                    link = link.split('/url?q=')[1].split('&')[0]
                    link = urllib.parse.unquote(link)
                if any(x in link for x in
                       ['google.com', 'youtube.com', 'blogger.com', 'javascript:', '#', 'facebook.com']):
                    continue
                if link.startswith('http'):
                    urls.add(link)
                    if len(urls) >= max_results: break
    except Exception as e:
        print(f"   -> Lỗi kết nối Google: {e}")
    return list(urls)


def search_internet(queries, max_results_per_query=3):
    urls = set()
    print("--- Bắt đầu tìm kiếm Internet ---")
    try:
        ddgs = DDGS()
    except Exception as e:
        print(f"Lỗi khởi tạo DDGS: {e}")
        ddgs = None

    for raw_query in queries:
        if len(raw_query.split()) < 2:
            continue

        # TẠO 2 PHIÊN BẢN TỪ KHÓA:
        # 1. exact_query: Giữ nguyên ngoặc kép (Ví dụ: '"Hà Nội sẽ ưu tiên"')
        # 2. broad_query: Bỏ ngoặc kép (Ví dụ: 'Hà Nội sẽ ưu tiên')
        exact_query = raw_query
        broad_query = raw_query.replace('"', '')

        # Kịch bản tìm kiếm kép
        search_modes = [
            ("Exact Match", exact_query),
            ("Broad Match", broad_query)
        ]

        found_urls = set()

        for mode_name, query in search_modes:
            print(f" Đang tìm ({mode_name}): [{query}]")

            # --- 1. Gọi DuckDuckGo ---
            if ddgs:
                try:
                    results = list(ddgs.text(query, max_results=max_results_per_query))
                    if results:
                        for r in results:
                            found_urls.add(r['href'])
                except Exception as e:
                    print(f"   ->  DDG lỗi: {e}")

            # --- 2. Gọi Google (nếu DuckDuckGo không có kết quả) ---
            if not found_urls:
                google_links = search_google_manual(query, max_results=max_results_per_query)
                for link in google_links:
                    found_urls.add(link)

            # --- 3. KIỂM TRA ĐIỀU KIỆN DỪNG ---
            if found_urls:
                # Nếu ĐÃ TÌM THẤY URL ở chế độ Exact Match -> BỎ QUA chế độ Broad Match
                break
            else:
                # Nếu Exact Match trả về 0 kết quả, in thông báo và tiếp tục vòng lặp sang Broad Match
                if mode_name == "Exact Match":
                    print("   -> 0 kết quả. Tự động tháo ngoặc kép, chuyển sang Broad Match...")
                    time.sleep(random.uniform(1.0, 2.0))

        # Lưu các URL hợp lệ vào danh sách tổng
        for url in found_urls:
            urls.add(url)

        time.sleep(random.uniform(1.5, 3.0))

    return list(urls)


def get_smart_queries(sentences):
    # 1. Tính toán số lượng truy vấn: Số câu // 3 (Đảm bảo ít nhất là 1)
    num_queries = max(1, len(sentences) // 3)

    queries = []

    # 2. Ưu tiên các câu dài để lấy từ khóa cho chuẩn
    # Sắp xếp danh sách câu theo độ dài (số lượng từ) giảm dần
    sorted_sentences = sorted(sentences, key=lambda s: len(s.split()), reverse=True)

    # 3. Chỉ lấy đúng số lượng câu đã tính toán
    selected_sentences = sorted_sentences[:num_queries]

    for sentence in selected_sentences:
        words = sentence.split()
        total_words = len(words)

        # --- THUẬT TOÁN SLIDING OFFSET (LỌC TỪ NỐI ĐẦU CÂU) ---
        # Nếu câu rất dài (>= 20 từ): Bỏ qua 1/5 số từ ở đầu câu và lấy tối đa 16 từ cốt lõi
        if total_words >= 20:
            start_idx = total_words // 5
            chunk = " ".join(words[start_idx : start_idx + 16])
            
        # Nếu câu dài vừa phải (16-19 từ): Bỏ qua 2 từ đầu, lấy phần cốt lõi phía sau
        elif total_words >= 16:
            start_idx = 2
            # Lấy 15-16 từ tính từ start_idx để tránh query quá dài
            chunk = " ".join(words[start_idx : start_idx + 15])
            
        # Nếu câu ngắn (< 16 từ): Lấy nguyên vẹn cả câu
        else:
            chunk = " ".join(words)
        # -------------------------------------------------------

        # 4. QUAN TRỌNG NHẤT: Bọc trong dấu ngoặc kép để tìm kiếm Exact Match
        exact_query = f'"{chunk}"'
        queries.append(exact_query)

    return queries

def fetch_url_content(url):
    print(f"    Đang tải: {url[:60]}...")

    # Cách 1: Thử nghiệm với trafilatura (nhanh nhất cho các web bình thường)
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            text = trafilatura.extract(downloaded)
            if text and len(text.strip()) > 100:
                return text
    except:
        pass  # Nếu lỗi thì bỏ qua, chuyển sang cách 2

    # Cách 2: Dùng Cloudscraper để vượt rào các trang báo lớn như VnExpress
    try:
        scraper = cloudscraper.create_scraper(browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        })
        response = scraper.get(url, timeout=10)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Bóc tách và dọn rác
            for script in soup(["script", "style", "nav", "footer", "aside"]):
                script.extract()
            text = soup.get_text(separator=' ')
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)

            if len(text) > 100:
                return text
        else:
            print(f"   ->  Bị chặn bởi server (Mã lỗi: {response.status_code})")

    except requests.exceptions.Timeout:
        print(f"   ->  Timeout: Trang web {url[:30]}... tải quá chậm!")
    except Exception as e:
        print(f"   ->  Lỗi khi trích xuất URL: {str(e)[:50]}")

    return ""