import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from konlpy.tag import Okt
import matplotlib.pyplot as plt

def set_font():
    plt.rc('font', family='NanumGothic')

def tokenizer(text):
    okt = Okt()
    # 명사뿐만 아니라 형용사 등도 포함하여 분석 범위 확대
    return [word for word, pos in okt.pos(text) if pos in ['Noun', 'Adjective']]

def run_analysis(df, column_name):
    if df is None or column_name not in df.columns:
        return None, None, None, None
    
    data = df[column_name].dropna().astype(str).tolist()
    
    if not data or all(len(d.strip()) == 0 for d in data):
        return None, None, None, None
    
    # min_df=1로 설정하여 아주 짧은 텍스트도 분석 가능하게 함
    vectorizer = TfidfVectorizer(tokenizer=tokenizer, token_pattern=None, min_df=1)
    
    try:
        tfidf = vectorizer.fit_transform(data)
    except Exception:
        return None, None, None, None
    
    feature_names = vectorizer.get_feature_names_out()
    word_freq = pd.Series(tfidf.sum(axis=0).A1, index=feature_names)
    result_df = word_freq.reset_index().rename(columns={'index': 'Word', 0: 'Score'})
    
    return word_freq.to_dict(), None, result_df, None