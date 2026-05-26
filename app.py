import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from pypdf import PdfReader
from analyzer import run_quantitative_analysis, generate_wordcloud, set_matplotlib_font

st.set_page_config(layout="wide")

st.markdown("""
    <style>
    button[data-baseweb="tab"] { font-size: 20px !important; font-weight: bold !important; }
    div[data-baseweb="textarea"] + div { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("Data Mining Analyzer")

# 가이드 문구 노출: 상단에 명확하게 노출
st.info("""
### 📢 User Guide
1. **Select Input:** Choose your data source (CSV, PDF, or Text) from the left sidebar.
2. **Upload/Paste:** Provide the file or text content.
3. **Run:** Click the **'Run Analysis'** button to generate insights.
""")

set_matplotlib_font()

mode = st.sidebar.radio("Input Source", ["CSV Upload", "PDF Document", "Text Input"])
df = None
col = None

if mode == "CSV Upload":
    f = st.file_uploader("Upload CSV", type=["csv"])
    if f: 
        df = pd.read_csv(f)
        col = st.selectbox("Select Column", df.columns)
elif mode == "PDF Document":
    f = st.file_uploader("Upload PDF", type=["pdf"])
    if f:
        reader = PdfReader(f)
        text = " ".join([p.extract_text() for p in reader.pages if p.extract_text()])
        df = pd.DataFrame({"Content": [text]})
        col = "Content"
elif mode == "Text Input":
    t = st.text_area("Paste Text", label_visibility="collapsed")
    if t: 
        df = pd.DataFrame({"Content": [t]})
        col = "Content"

if df is not None:
    if mode != "CSV Upload":
        st.write(f"**Target Column:** '{col}'")
    
    run_btn = st.button("Run Analysis", type="primary")

    if run_btn:
        freq, corr_df, word_df, G = run_quantitative_analysis(df, col)
        
        t1, t2, t3 = st.tabs(["Dashboard (WordCloud)", "Keyword List", "Co-occurrence Network"])
        
        with t1:
            if freq: st.image(generate_wordcloud(freq).to_array())
        with t2:
            st.table(word_df.sort_values('Score', ascending=False).head(20))
        with t3:
            if G and len(G.nodes) > 0:
                fig, ax = plt.subplots(figsize=(10, 8))
                pos = nx.spring_layout(G, k=0.5)
                nx.draw(G, pos, with_labels=True, node_color='skyblue', font_size=12, ax=ax, font_family='NanumGothic')
                st.pyplot(fig)
            else: st.warning("Not enough data for network visualization.")