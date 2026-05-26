import pandas as pd
from collections import Counter
from kiwipiepy import Kiwi
import matplotlib.pyplot as plt
from wordcloud import WordCloud

def set_font():
    plt.rc('font', family='NanumGothic')

def run_analysis(df, column_name):
    if df is None or column_name not in df.columns:
        return None, None
    
    raw_data = df[column_name].dropna().astype(str).tolist()
    combined_text = " ".join(raw_data)
    
    if not combined_text.strip():
        return None, None
    
    kiwi = Kiwi()
    tokens = []
    analysis_results = kiwi.analyze(combined_text)
    
    for result in analysis_results:
        for token in result[0]:
            tokens.append(token.form)
            
    if not tokens:
        return None, None
    
    token_counts = Counter(tokens)
    result_dataframe = pd.DataFrame(token_counts.most_common(20), columns=['Word', 'Frequency'])
    
    return result_dataframe, token_counts

def generate_wordcloud(token_counts):
    wc = WordCloud(
        font_path='/usr/share/fonts/truetype/nanum/NanumGothic.ttf',
        background_color='white',
        width=800, height=400
    ).generate_from_frequencies(dict(token_counts))
    return wc