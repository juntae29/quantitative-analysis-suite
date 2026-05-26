import pandas as pd
from collections import Counter
from kiwipiepy import Kiwi # Java 의존성이 없는 분석기
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
    
    # Kiwi 분석기 초기화 및 명사/형용사 추출
    kiwi = Kiwi()
    tokens = [token.form for token in kiwi.analyze(text)[0][0] if token.tag in ['NNG', 'NNP', 'VA']]
    
    if not tokens:
        return None, None, None, None
    
    # 빈도 계산
    counts = Counter(tokens)
    result_df = pd.DataFrame(counts.items(), columns=['Word', 'Score'])
    
    return counts, None, result_df, None