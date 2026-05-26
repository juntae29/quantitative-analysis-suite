import pandas as pd
from collections import Counter
from konlpy.tag import Okt
import matplotlib.pyplot as plt

def set_font():
    plt.rc('font', family='NanumGothic')

def run_analysis(df, column_name):
    if df is None or column_name not in df.columns:
        return None, None, None, None
    
    data = df[column_name].dropna().astype(str).tolist()
    text = " ".join(data)
    
    if not text.strip():
        return None, None, None, None
    
    # Okt 객체 생성 후 명사와 형용사 추출
    okt = Okt()
    tokens = [word for word, pos in okt.pos(text) if pos in ['Noun', 'Adjective']]
    
    if not tokens:
        return None, None, None, None
    
    # 직접 빈도 계산
    counts = Counter(tokens)
    result_df = pd.DataFrame(counts.items(), columns=['Word', 'Score'])
    
    return counts, None, result_df, None