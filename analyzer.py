import pandas as pd
import re
import os
import requests
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from wordcloud import WordCloud

# [1] 데이터 로드 및 폰트 설정
def get_font():
    font_path = "/tmp/NanumGothic.ttf"
    if not os.path.exists(font_path):
        url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"
        try:
            res = requests.get(url, timeout=10)
            with open(font_path, "wb") as f: f.write(res.content)
        except: return None
    return font_path

# [2] 형태소 분석 (기존 복구)
def tokenize(text):
    return re.findall(r'[가-힣a-zA-Z]+', str(text))

# [3] KH Coder 스타일의 정량적 분석 통합
def run_quantitative_analysis(df, column_name):
    data = df[column_name].dropna().astype(str)
    if data.empty: return None, None, None
    
    # TF-IDF 기반 단어 벡터화
    vec = TfidfVectorizer(tokenizer=tokenize, token_pattern=None, min_df=2)
    tfidf = vec.fit_transform(data)
    words = vec.get_feature_names_out()
    
    # [A] 단어 빈도
    freq = dict(zip(words, tfidf.sum(axis=0).A1))
    
    # [B] 단어 간 관계(유사도 행렬) - Co-occurrence Matrix
    sim = cosine_similarity(tfidf.T)
    corr_df = pd.DataFrame(sim, index=words, columns=words)
    
    return freq, corr_df, pd.DataFrame({'Word': words, 'Score': tfidf.sum(axis=0).A1})

# [4] 워드클라우드 및 매핑 유지
def generate_wordcloud(freq):
    wc = WordCloud(width=800, height=400, background_color='white', font_path=get_font())
    return wc.generate_from_frequencies(freq) if freq else wc