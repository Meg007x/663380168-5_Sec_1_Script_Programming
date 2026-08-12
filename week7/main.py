import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from scraper import SimpleWebScraper

def main():
    target_url = "https://automatetheboringstuff.com/3e/"
    scraper = SimpleWebScraper(target_url)

    scraped_data = scraper.scrape_main_titles()
    if scraped_data:
        print("--- ข้อมูลที่ Scrape ได้ ---")
        print(f"ชื่อหนังสือ: {scraped_data['book_title']}\n")
        print("ชื่อบทต่างๆ:")
        for i, title in enumerate(scraped_data['chapter_titles']):
            print(f"{i+1}. {title}")
    else:
        print("Failed to scrape data.")

if __name__ == "__main__":
    main()