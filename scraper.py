import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time

def run_web_scraper(search_query, num_papers):
    if os.path.exists("scraped_data.csv"): os.remove("scraped_data.csv")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    query = search_query.replace(' ', '+')
    url = f"https://arxiv.org/search/?query={query}&searchtype=all&source=header&size={num_papers}&order=-announced_date_first"
    
    try:
        time.sleep(1)
        response = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, "html.parser")
        articles = soup.find_all("li", class_="arxiv-result")
        
        extracted = []
        for article in articles:
            title = article.find("p", class_="title").text.strip()
            summary = article.find("p", class_="abstract").text.replace("Abstract:", "").strip()
            extracted.append({"title": title, "Abstract": summary})
            
        if not extracted: return False
        pd.DataFrame(extracted).to_csv("scraped_data.csv", index=False, encoding="utf-8-sig")
        return True
    except Exception as e:
        print(f"Scraper Error: {e}")
        return False

def scrape_text_from_url(url):
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.get_text(separator=' ').strip()
    except Exception as e:
        print(f"URL Scraper Error: {e}")
        return None