import pandas as pd
from collections import Counter
from kiwipiepy import Kiwi
import matplotlib.pyplot as plt

def set_font():
    plt.rc('font', family='NanumGothic')

def run_analysis(df, column_name):
    if df is None or column_name not in df.columns:
        return None, None, None, None
    
    # Ensure data is string and join with space
    data = df[column_name].dropna().astype(str).tolist()
    text = " ".join(data)
    
    if not text or len(text.strip()) == 0:
        return None, None, None, None
    
    kiwi = Kiwi()
    # Broaden analysis to include all nouns and adjectives found
    results = kiwi.analyze(text)
    tokens = []
    for result in results:
        for token in result[0]:
            if token.tag in ['NNG', 'NNP', 'VA', 'VV']:
                tokens.append(token.form)
    
    if not tokens:
        return None, None, None, None
    
    counts = Counter(tokens)
    result_df = pd.DataFrame(counts.most_common(20), columns=['Word', 'Score'])
    
    return counts, None, result_df, None