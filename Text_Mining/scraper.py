import requests
from bs4 import BeautifulSoup

def scrape_text_from_url(url, query=None):
    try:
        search_url = f"{url}?q={query}" if query else url
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.get_text(separator=' ').strip()
    except:
        return None