import pandas as pd
import re
import os
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from wordcloud import WordCloud

def tokenize(text):
    return re.findall(r'[가-힣a-zA-Z]+', str(text))

def process_advanced_mining(df, column_name):
    data = df[column_name].dropna().astype(str)
    if data.empty: return pd.DataFrame(), {}
    
    vectorizer = TfidfVectorizer(tokenizer=tokenize, token_pattern=None, ngram_range=(1, 2), max_features=50)
    tfidf_matrix = vectorizer.fit_transform(data)
    
    feature_names = vectorizer.get_feature_names_out()
    scores = tfidf_matrix.sum(axis=0).A1
    return pd.DataFrame({'Word': feature_names, 'Count': scores}).sort_values(by='Count', ascending=False), dict(zip(feature_names, scores))

def generate_wordcloud_obj(word_dict):
    font_path = "/tmp/NanumGothic.ttf"
    if not os.path.exists(font_path):
        try:
            url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"
            response = requests.get(url, timeout=10)
            with open(font_path, "wb") as f:
                f.write(response.content)
        except:
            font_path = None
            
    wc = WordCloud(width=800, height=400, background_color='white', font_path=font_path)
    if not word_dict: return wc
    wc.generate_from_frequencies(word_dict)
    return wc

def map_taxonomy(word_list, taxonomy_dict):
    results = {}
    for category, keywords in taxonomy_dict.items():
        targets = [k.strip() for k in keywords.split(",")]
        results[category] = [word for word in word_list if word in targets]
    return results