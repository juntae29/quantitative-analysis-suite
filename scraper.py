import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

def run_web_scraper(search_query="Artificial Intelligence", num_papers=30):
    """
    arXiv 웹사이트에서 논문 정보를 수집하는 함수
    """
    print(f"[System] Starting data scraping for: {search_query}")
    
    extracted_records = []
    start_index = 0
    papers_per_page = 50
    
    headers = {"User-Agent": "Mozilla/5.0"}
    
    while len(extracted_records) < num_papers:
        url = f"https://arxiv.org/search/?query={search_query.replace(' ', '+')}&searchtype=all&size={papers_per_page}&start={start_index}"
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200: break
        except: break
            
        soup = BeautifulSoup(response.text, "html.parser")
        articles = soup.find_all("li", class_="arxiv-result")
        if not articles: break
            
        for article in articles:
            if len(extracted_records) >= num_papers: break
            title_el = article.find("p", class_="title")
            summary_el = article.find("p", class_="abstract")
            
            if title_el and summary_el:
                title = re.sub(r'\s+', ' ', title_el.text.strip())
                summary = re.sub(r'\s+', ' ', summary_el.text.replace("Abstract:", "").strip())
                extracted_records.append({"title": title, "Abstract": summary})
        
        start_index += papers_per_page
        time.sleep(0.5)
        
    if not extracted_records: return False
    pd.DataFrame(extracted_records).to_csv("scraped_data.csv", index=False, encoding="utf-8-sig")
    print(f"[Success] {len(extracted_records)} records saved.")
    return True

def scrape_text_from_url(url):
    """
    사용자가 입력한 URL의 텍스트를 추출하는 함수
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 불필요한 태그 제거 (스크립트, 스타일, 네비게이션 등)
        for element in soup(["script", "style", "nav", "footer", "header", "noscript"]):
            element.extract()
            
        # 텍스트 추출
        text = soup.get_text(separator=' ')
        # 공백 정리
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    except Exception as e:
        print(f"[Error] Failed to scrape {url}: {e}")
        return None