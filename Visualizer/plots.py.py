# Visualizer/plots.py
import matplotlib.pyplot as plt
from wordcloud import WordCloud

def set_font():
    # Setting font for Korean characters
    plt.rc('font', family='NanumGothic')

def generate_wordcloud(token_counts):
    # WordCloud generation logic
    wc = WordCloud(
        font_path='/usr/share/fonts/truetype/nanum/NanumGothic.ttf',
        background_color='white',
        width=800, height=400
    ).generate_from_frequencies(dict(token_counts))
    return wc