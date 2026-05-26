import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

def run_web_scraper(search_query="Artificial Intelligence", num_papers=30):
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