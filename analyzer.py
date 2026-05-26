import pandas as pd
import re
import os
import requests
import networkx as nx
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from wordcloud import WordCloud

def get_font():
    font_path = "/tmp/NanumGothic.ttf"
    if not os.path.exists(font_path):
        url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"
        try:
            res = requests.get(url, timeout=10)
            with open(font_path, "wb") as f: f.write(res.content)
        except: return None
    return font_path

def tokenize(text):
    return re.findall(r'[가-힣a-zA-Z]+', str(text))

def run_quantitative_analysis(df, column_name):
    data = df[column_name].dropna().astype(str)
    if data.empty: return {}, pd.DataFrame(), pd.DataFrame(), None
    
    # 동적 min_df 설정: 데이터가 적으면 1, 많으면 2
    min_df = 1 if len(data) < 2 else 2
    
    vec = TfidfVectorizer(tokenizer=tokenize, token_pattern=None, min_df=min_df)
    tfidf = vec.fit_transform(data)
    words = vec.get_feature_names_out()
    
    if len(words) == 0: return {}, pd.DataFrame(), pd.DataFrame(), None
    
    freq = dict(zip(words, tfidf.sum(axis=0).A1))
    sim = cosine_similarity(tfidf.T)
    corr_df = pd.DataFrame(sim, index=words, columns=words)
    word_df = pd.DataFrame({'Word': words, 'Score': tfidf.sum(axis=0).A1})
    
    G = nx.Graph()
    for i in range(len(words)):
        for j in range(i + 1, len(words)):
            if sim[i, j] > 0.1: # 임계치를 낮추어 연결 확보
                G.add_edge(words[i], words[j], weight=sim[i, j])
                
    return freq, corr_df, word_df, G

def generate_wordcloud(freq):
    wc = WordCloud(width=800, height=400, background_color='white', font_path=get_font())
    return wc.generate_from_frequencies(freq) if freq else wc