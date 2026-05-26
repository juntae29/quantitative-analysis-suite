import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from pypdf import PdfReader
from analyzer import run_quantitative_analysis, generate_wordcloud, set_matplotlib_font

st.set_page_config(layout="wide")

# CSS: 레이아웃 간섭 최소화
st.markdown("""
    <style>
    .guide-box {
        background-color: #e8f4fd;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #2196f3;
        margin-bottom: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("Data Mining Analyzer")

# 강제 안내 영역: 제목 바로 아래에 명확하게 배치
with st.container():
    st.markdown("""
    <div class="guide-box">
        <h3>💡 이용 안내</h3>
        <p>1. 왼쪽 사이드바에서 <b>데이터 입력 방식</b>(CSV, PDF, Text)을 선택하시오.</p>
        <p>2. 해당 방식에 맞춰 데이터를 <b>업로드하거나 문장을 붙여넣으시오.</b></p>
        <p>3. 상자에 데이터를 넣은 후 나타나는 <b>'Run Analysis'</b> 버튼을 클릭하시오.</p>
    </div>
    """, unsafe_allow_html=True)

set_matplotlib_font()

mode = st.sidebar.radio("Input Source", ["CSV Upload", "PDF Document", "Text Input"])
df = None
col = None

# 모드별 입력창
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
    t = st.text_area("분석할 문장을 입력하시오.", placeholder="분석할 문장을 이곳에 붙여넣으시오.", height=150)
    if t: 
        df = pd.DataFrame({"Content": [t]})
        col = "Content"

# 분석 실행부
if df is not None:
    if mode != "CSV Upload":
        st.write(f"**Target Column:** '{col}'")
    
    if st.button("Run Analysis", type="primary"):
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