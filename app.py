import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from pypdf import PdfReader
from analyzer import run_quantitative_analysis, generate_wordcloud, set_matplotlib_font

st.set_page_config(layout="wide")

# 1. 고정된 헤더 영역
st.title("Data Mining Analyzer")
st.markdown("---")

# 2. 고정된 안내 문구 영역 (절대 위치 고정)
guide_col, input_col = st.columns([1, 2])

with guide_col:
    st.subheader("💡 User Guide")
    st.markdown("1. Select source from the sidebar.")
    st.markdown("2. Input data in the center panel.")
    st.markdown("3. Click 'Run Analysis'.")

# 3. 사이드바 입력 모드 설정
input_mode = st.sidebar.radio("Input Source", ["CSV Upload", "PDF Document", "Text Input"])

# 4. 입력/분석 영역
with input_col:
    data_frame = None
    target_column = None

    if input_mode == "Text Input":
        user_text = st.text_area("Paste your text here:", height=150)
        if user_text: 
            data_frame = pd.DataFrame({"Content": [user_text]})
            target_column = "Content"
    elif input_mode == "CSV Upload":
        uploaded_file = st.file_uploader("Upload CSV:", type=["csv"])
        if uploaded_file: 
            data_frame = pd.read_csv(uploaded_file)
            target_column = st.selectbox("Select Column:", data_frame.columns)
    elif input_mode == "PDF Document":
        uploaded_file = st.file_uploader("Upload PDF:", type=["pdf"])
        if uploaded_file:
            reader = PdfReader(uploaded_file)
            text_content = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])
            data_frame = pd.DataFrame({"Content": [text_content]})
            target_column = "Content"

    # 분석 실행 버튼
    if data_frame is not None:
        if st.button("Run Analysis", type="primary"):
            set_matplotlib_font()
            frequency, correlation_df, word_score_df, graph = run_quantitative_analysis(data_frame, target_column)
            
            tabs = st.tabs(["Dashboard", "Keyword List", "Network"])
            with tabs[0]:
                if frequency: st.image(generate_wordcloud(frequency).to_array())
            with tabs[1]:
                st.table(word_score_df.sort_values('Score', ascending=False).head(20))
            with tabs[2]:
                if graph and len(graph.nodes) > 0:
                    fig, ax = plt.subplots(figsize=(8, 6))
                    pos = nx.spring_layout(graph, k=0.5)
                    nx.draw(graph, pos, with_labels=True, node_color='skyblue', ax=ax, font_family='NanumGothic')
                    st.pyplot(fig)
                else: st.warning("Insufficient data.")