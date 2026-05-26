import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from pypdf import PdfReader
from analyzer import run_quantitative_analysis, generate_wordcloud, set_matplotlib_font

st.set_page_config(layout="wide")

st.title("Data Mining Analyzer")

# CSS나 복잡한 태그 없이, 가장 직관적인 마크다운 텍스트로 고정
st.markdown("---")
st.markdown("### 💡 이용 안내")
st.markdown("1. 왼쪽 사이드바에서 데이터 입력 방식을 선택하십시오.")
st.markdown("2. 데이터를 업로드하거나 분석할 문장을 상자에 입력하십시오.")
st.markdown("3. 'Run Analysis' 버튼을 클릭하면 분석 결과가 나타납니다.")
st.markdown("---")

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
    t = st.text_area("분석할 문장 입력", placeholder="여기에 분석할 문장을 붙여넣으십시오.", height=150)
    if t: 
        df = pd.DataFrame({"Content": [t]})
        col = "Content"

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
            else: st.warning("분석할 데이터가 부족하여 네트워크 시각화가 불가능하다.")