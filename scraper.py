import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import os
from urllib.parse import quote

def run_web_scraper(search_query, num_papers):
    extracted_records = []
    start_index = 0
    if os.path.exists("scraped_data.csv"): os.remove("scraped_data.csv")
    
    headers = {"User-Agent": "Mozilla/5.0"}
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
                title = article.find("p", class_="title").text.strip()
                summary = article.find("p", class_="abstract").text.replace("Abstract:", "").strip()
                extracted_records.append({"title": title, "Abstract": summary})
            start_index += 50
            time.sleep(2.0)
        except: break
    
    if not extracted_records: return False
    pd.DataFrame(extracted_records).to_csv("scraped_data.csv", index=False, encoding="utf-8-sig")
    return True

def scrape_text_from_url(url):
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if response.status_code != 200: return None
        soup = BeautifulSoup(response.text, 'html.parser')
        for e in soup(["script", "style", "nav", "footer", "header"]): e.extract()
        text = re.sub(r'\s+', ' ', soup.get_text(separator=' ')).strip()
        return text if len(text) > 50 else None
    except: return None