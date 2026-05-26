import pandas as pd
from collections import Counter
import re
from wordcloud import WordCloud

def process_dataframe_mining(df):
    text_data = " ".join(df['Abstract'].astype(str)).lower()
    words = re.findall(r'\w+', text_data)
    word_counts = Counter(words)
    word_df = pd.DataFrame(word_counts.items(), columns=['Word', 'Count'])
    word_df = word_df.sort_values(by='Count', ascending=False).head(50)
    return word_df, word_counts

def generate_wordcloud_obj(words):
    wc = WordCloud(width=800, height=400, background_color='white')
    wc.generate_from_frequencies(words)
    return wc

def map_taxonomy(word_list, taxonomy_dict):
    results = {}
    for category, keywords in taxonomy_dict.items():
        results[category] = [word for word in word_list if word in keywords]
    return results