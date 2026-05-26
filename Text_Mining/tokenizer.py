# Text_Mining/tokenizer.py
import pandas as pd
from collections import Counter
from kiwipiepy import Kiwi

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