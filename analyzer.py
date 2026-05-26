import pandas as pd
import re
import os
import io
import requests
import matplotlib.font_manager as fm
from sklearn.feature_extraction.text import TfidfVectorizer
from wordcloud import WordCloud

def get_font_prop():
    # 폰트를 직접 다운로드하여 메모리에 올림
    url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"
    response = requests.get(url)
    font_file = io.BytesIO(response.content)
    
    # 임시 파일 없이 메모리에서 바로 폰트 매니저에 등록
    return font_file

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
    # 메모리에 로드된 폰트 데이터를 WordCloud에 직접 전달
    # WordCloud는 font_path 인자에 파일 경로만 받으므로, 
    # 해결책으로 임시 파일을 /tmp (쓰기 가능 영역)에 생성
    font_path = "/tmp/NanumGothic.ttf"
    if not os.path.exists(font_path):
        font_data = get_font_prop()
        with open(font_path, "wb") as f:
            f.write(font_data.getvalue())
            
    wc = WordCloud(width=800, height=400, background_color='white', font_path=font_path)
    if not word_dict: return wc
    wc.generate_from_frequencies(word_dict)
    return wc