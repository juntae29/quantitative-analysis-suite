import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from wordcloud import WordCloud
from konlpy.tag import Okt
import os

okt = Okt()

def tokenize(text):
    return [word for word, pos in okt.pos(text) if pos in ['Noun', 'Verb', 'Adjective']]

def process_advanced_mining(df, column_name):
    data = df[column_name].dropna().astype(str)
    if data.empty: return pd.DataFrame(), {}
    
    vectorizer = TfidfVectorizer(tokenizer=tokenize, ngram_range=(1, 2), max_features=50)
    tfidf_matrix = vectorizer.fit_transform(data)
    
    feature_names = vectorizer.get_feature_names_out()
    scores = tfidf_matrix.sum(axis=0).A1
    word_df = pd.DataFrame({'Word': feature_names, 'Count': scores}).sort_values(by='Count', ascending=False)
    return word_df, dict(zip(word_df['Word'], word_df['Count']))

def generate_wordcloud_obj(word_dict):
    # 시스템에 설치된 나눔고딕 혹은 프로젝트 내 파일을 우선 탐색
    font_paths = [
        "NanumGothic.ttf", 
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        "/usr/share/fonts/nanum/NanumGothic.ttf"
    ]
    
    selected_font = None
    for path in font_paths:
        if os.path.exists(path):
            selected_font = path
            break
            
    wc = WordCloud(
        width=800, height=400, 
        background_color='white', 
        font_path=selected_font
    )
    if not word_dict: return wc
    wc.generate_from_frequencies(word_dict)
    return wc

def map_taxonomy(word_list, taxonomy_dict):
    results = {}
    for category, keywords in taxonomy_dict.items():
        results[category] = [word for word in word_list if word in keywords]
    return results