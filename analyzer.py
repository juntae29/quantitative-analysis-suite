import re
import pandas as pd
import os
import platform
from collections import Counter
from kiwipiepy import Kiwi
from wordcloud import WordCloud

# Global instance for Kiwi
_kiwi_instance = None

def get_kiwi():
    global _kiwi_instance
    if _kiwi_instance is None:
        _kiwi_instance = Kiwi()
    return _kiwi_instance

def process_text_data(text):
    if not text or not isinstance(text, str):
        return []
    kiwi = get_kiwi()
    clean_text = re.sub(r'[^가-힣a-zA-Z\s]', '', text)
    tokens = kiwi.tokenize(clean_text)
    allowed_tags = ['NNG', 'NNP', 'SL']
    raw_words = [t.form.lower() if t.tag == 'SL' else t.form for t in tokens if t.tag in allowed_tags]
    stop_words = ['그것', '이것', '저것', '때문', '위해', '대한', '통해', '관한', '다함께', '우리', '우리의', '무리를', '함께', '모든', '통하여', '대하여', '있습니다', '아래', '이상', '이하', '내용', '구분', 'the', 'and', 'of', 'to', 'in', 'is', 'for', 'that', 'with', 'on', 'as', 'by', 'an', 'this', 'we']
    return [w for w in raw_words if len(w) > 1 and w not in stop_words]

def process_dataframe_mining(df):
    all_text = " ".join(df['Abstract'].fillna("").astype(str).tolist()) if 'Abstract' in df.columns else ""
    if not all_text and 'title' in df.columns:
        all_text = " ".join(df['title'].fillna("").astype(str).tolist())
    filtered_words = process_text_data(all_text)
    word_df = pd.DataFrame(Counter(filtered_words).most_common(10), columns=["Word", "Count"]) if filtered_words else pd.DataFrame(columns=["Word", "Count"])
    return word_df, filtered_words

def generate_wordcloud_obj(text_list, font_path=None):
    if not font_path:
        linux_fonts = ["/usr/share/fonts/truetype/nanum/NanumGothic.ttf", "/usr/share/fonts/fonts-nanum/NanumGothic.ttf"]
        for path in linux_fonts:
            if os.path.exists(path):
                font_path = path
                break
    wc = WordCloud(font_path=font_path, width=800, height=500, background_color="white", colormap="plasma", prefer_horizontal=0.9)
    return wc.generate(" ".join(text_list))