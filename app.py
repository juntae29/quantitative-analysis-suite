import streamlit as st
import pandas as pd
from pypdf import PdfReader
from analyzer import run_quantitative_analysis, generate_wordcloud

st.set_page_config(layout="wide")
st.title("Data Mining Analyzer")

# 1. 사이드바 입력 설정
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
    t = st.text_area("Paste Text")
    if t: df = pd.DataFrame({"Content": [t]})

# 2. 분석 실행 및 결과 대시보드
if df is not None:
    col = st.selectbox("Select Column", df.columns)
    if st.button("Run Analysis"):
        freq, corr_df, word_df = run_quantitative_analysis(df, col)
        
        # 탭 변수 정의
        tab1_title = '<span style="font-size: 20px; font-weight: bold;">Dashboard (WordCloud)</span>'
        tab2_title = '<span style="font-size: 20px; font-weight: bold;">Keyword List</span>'
        tab3_title = '<span style="font-size: 20px; font-weight: bold;">Co-occurrence Network</span>'
        
        t1, t2, t3 = st.tabs([tab1_title, tab2_title, tab3_title])
        
        with t1:
            st.image(generate_wordcloud(freq).to_array())
        with t2:
            st.markdown("### <span style='font-size: 24px;'>Top 20 Keywords</span>", unsafe_allow_html=True)
            st.table(word_df.sort_values('Score', ascending=False).head(20))
        with t3:
            st.markdown("### <span style='font-size: 24px;'>Word Co-occurrence Correlation Matrix</span>", unsafe_allow_html=True)
            st.dataframe(corr_df.style.background_gradient(cmap='Blues'))