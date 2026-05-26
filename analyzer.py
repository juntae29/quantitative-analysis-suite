import pandas as pd
import re
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from wordcloud import WordCloud

def tokenize(text):
    # 한글 및 영문 단어 추출 (정규식 기반)
    return re.findall(r'[가-힣a-zA-Z]+', str(text))

def process_advanced_mining(df, column_name):
    data = df[column_name].dropna().astype(str)
    if data.empty: return pd.DataFrame(), {}
    
    # TF-IDF 분석 엔진
    vectorizer = TfidfVectorizer(tokenizer=tokenize, token_pattern=None, ngram_range=(1, 2), max_features=50)
    tfidf_matrix = vectorizer.fit_transform(data)
    
    feature_names = vectorizer.get_feature_names_out()
    scores = tfidf_matrix.sum(axis=0).A1
    word_df = pd.DataFrame({'Word': feature_names, 'Count': scores}).sort_values(by='Count', ascending=False)
    return word_df, dict(zip(word_df['Word'], word_df['Count']))

def generate_wordcloud_obj(word_dict):
    # 폰트 우선순위: 로컬 NanumGothic.ttf -> 없으면 시스템 기본 폰트
    font_path = "NanumGothic.ttf" if os.path.exists("NanumGothic.ttf") else None
    wc = WordCloud(width=800, height=400, background_color='white', font_path=font_path)
    
    if not word_dict: return wc
    wc.generate_from_frequencies(word_dict)
    return wc

def map_taxonomy(word_list, taxonomy_dict):
    results = {}
    for category, keywords in taxonomy_dict.items():
        results[category] = [word for word in word_list if word in [k.strip() for k in keywords.split(",")]]
    return results