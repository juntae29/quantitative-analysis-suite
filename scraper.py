import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
from urllib.parse import quote # URL 인코딩을 위한 라이브러리 추가

def run_web_scraper(search_query, num_papers):
    extracted_records = []
    start_index = 0
    # 파일 잔류 문제 방지
    if os.path.exists("scraped_data.csv"): os.remove("scraped_data.csv")
    
    headers = {"User-Agent": "Mozilla/5.0"}
    
    # search_query를 안전하게 URL 형식으로 인코딩
    encoded_query = quote(search_query)
    
    while len(extracted_records) < num_papers:
        url = f"https://arxiv.org/search/?query={encoded_query}&size=50&start={start_index}"
        try:
            response = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(response.text, "html.parser")
            articles = soup.find_all("li", class_="arxiv-result")
            
            if not articles: break
            
            for article in articles:
                if len(extracted_records) >= num_papers: break
                title_el = article.find("p", class_="title")
                abstract_el = article.find("p", class_="abstract")
                
                if title_el and abstract_el:
                    title = title_el.text.strip()
                    summary = abstract_el.text.replace("Abstract:", "").strip()
                    extracted_records.append({"title": title, "Abstract": summary})
            
            start_index += 50
            time.sleep(2.0) # 더 안정적인 스크래핑을 위해 대기 시간 증가
        except Exception as e:
            print(f"Error: {e}")
            break
    
    if not extracted_records: return False
    pd.DataFrame(extracted_records).to_csv("scraped_data.csv", index=False, encoding="utf-8-sig")
    return True