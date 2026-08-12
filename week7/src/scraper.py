import requests
from bs4 import BeautifulSoup

class SimpleWebScraper:
    def __init__(self, target_url):
        self.target_url = target_url

    def _get_html_content(self):
        print(f"กำลังดาวน์โหลด เนื้อหาจาก: {self.target_url}")
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(self.target_url, headers=headers, timeout=10)
            response.raise_for_status()
            print("ดาวน์โหลด เนื้อหาสำเร็จ\n")
            return response.text
        except Exception as e:
            print(f"Error: {e}")
            return None

    def scrape_main_titles(self):
        html_content = self._get_html_content()
        if not html_content:
            return None

        soup = BeautifulSoup(html_content, 'html.parser')

        # ดึงชื่อหนังสือ
        header_tag = soup.find('header')
        book_title = "Not Found"
        if header_tag:
            h1_tag = header_tag.find('h1')
            if h1_tag:
                book_title = h1_tag.get_text(strip=True)

        # ดึงรายชื่อบทเรียน
        chapter_titles = []
        # ค้นหาลิงก์บทเรียนจากโครงสร้างหน้าเว็บ
        for a_tag in soup.find_all('a'):
            text = a_tag.get_text(strip=True)
            if text.startswith("Chapter") or text.startswith("Introduction") or text.startswith("Appendix"):
                if text not in chapter_titles:
                    chapter_titles.append(text)

        return {
            "book_title": book_title,
            "chapter_titles": chapter_titles
        }