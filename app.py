import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from pypdf import PdfReader
from analyzer import run_quantitative_analysis, generate_wordcloud

st.set_page_config(layout="wide")

st.markdown("""
    <style>
    button[data-baseweb="tab"] { font-size: 20px !important; font-weight: bold !important; }
    div[data-baseweb="textarea"] + div { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("Data Mining Analyzer")

mode = st.sidebar.radio("Input Source", ["CSV Upload", "PDF Document", "Text Input"])
df = None

if mode == "CSV Upload":
    f = st.file_uploader("Upload CSV", type=["csv"])
    if f: df = pd.read_csv(f)
elif mode == "PDF Document":
    f = st.file_uploader("Upload PDF", type=["pdf"])
    if f:
        reader = PdfReader(f)
        text = " ".join([p.extract_text() for p in reader.pages if p.extract_text()])
        df = pd.DataFrame({"Content": [text]})
elif mode == "Text Input":
    t = st.text_area("Paste Text", label_visibility="collapsed")
    if t: df = pd.DataFrame({"Content": [t]})

if df is not None:
    if mode == "CSV Upload": col = st.selectbox("Select Column", df.columns)
    else: 
        col = "Content"
        st.info(f"Analysis will be performed on the '{col}' column.")

    if st.button("Run Analysis"):
        freq, corr_df, word_df, G = run_quantitative_analysis(df, col)
        
        t1, t2, t3 = st.tabs(["Dashboard (WordCloud)", "Keyword List", "Co-occurrence Network"])
        
        with t1:
            if freq: st.image(generate_wordcloud(freq).to_array())
        with t2:
            st.table(word_df.sort_values('Score', ascending=False).head(20))
        with t3:
            if G and len(G.nodes) > 0:
                fig, ax = plt.subplots(figsize=(10, 8))
                nx.draw(G, with_labels=True, node_color='skyblue', font_family='sans-serif', ax=ax)
                st.pyplot(fig)
            else: st.warning("Not enough data for network visualization.")