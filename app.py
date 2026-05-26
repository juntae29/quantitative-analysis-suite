import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from pypdf import PdfReader
from analyzer import run_quantitative_analysis, generate_wordcloud, set_matplotlib_font

st.set_page_config(layout="wide")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem; }
    button[data-baseweb="tab"] { font-size: 20px !important; font-weight: bold !important; }
    div[data-baseweb="textarea"] + div { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("Data Mining Analyzer")

# 상단 안내 문구 (모든 모드에서 항상 표시)
st.warning("### 💡 이용 안내\n1. 왼쪽 사이드바에서 데이터 입력 방식을 선택한다.\n2. 데이터를 업로드하거나 문장을 붙여넣는다.\n3. **'Run Analysis'** 버튼을 누르면 분석이 시작된다.")

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
    # placeholder 추가로 빈 상자 느낌 제거
    t = st.text_area(
        "Paste Text", 
        placeholder="여기에 분석할 텍스트를 붙여넣으시오.", 
        label_visibility="collapsed"
    )
    if t: 
        df = pd.DataFrame({"Content": [t]})
        col = "Content"
    else:
        st.info("왼쪽에서 'Text Input'을 선택했으므로, 이 상자에 텍스트를 입력해야 분석이 가능하다.")

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