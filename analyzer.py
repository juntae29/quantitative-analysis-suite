import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from wordcloud import WordCloud

def process_advanced_mining(df, column_name):
    target_col = column_name if column_name in df.columns else df.select_dtypes(include=['object']).columns[0]
    
    # 텍스트 데이터 정제: 결측치 제거 및 문자열 변환
    data = df[target_col].dropna().astype(str)
    if data.empty:
        return pd.DataFrame(), {}
        
    corpus = data.tolist()
    
    # TF-IDF 적용 (데이터가 적을 경우 오류 방지)
    try:
        vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words='english', max_features=50)
        tfidf_matrix = vectorizer.fit_transform(corpus)
        
        feature_names = vectorizer.get_feature_names_out()
        scores = tfidf_matrix.sum(axis=0).A1
        word_df = pd.DataFrame({'Word': feature_names, 'Count': scores})
        word_df = word_df.sort_values(by='Count', ascending=False)
        return word_df, dict(zip(word_df['Word'], word_df['Count']))
    except:
        return pd.DataFrame(), {}

def generate_wordcloud_obj(word_dict):
    wc = WordCloud(width=800, height=400, background_color='white')
    if not word_dict: return wc
    wc.generate_from_frequencies(word_dict)
    return wc

def map_taxonomy(word_list, taxonomy_dict):
    results = {}
    for category, keywords in taxonomy_dict.items():
        results[category] = [word for word in word_list if word in keywords]
    return results