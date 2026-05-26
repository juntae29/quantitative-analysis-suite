import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from pypdf import PdfReader
from analyzer import run_quantitative_analysis, generate_wordcloud, set_matplotlib_font

st.set_page_config(layout="wide")

# 1. 사이드바: 입력 제어 및 안내
with st.sidebar:
    st.title("💡 User Guide")
    st.markdown("1. Select source. 2. Input/Upload. 3. Analyze.")
    st.markdown("---")
    input_mode = st.radio("Input Source", ["CSV Upload", "PDF Document", "Text Input"])

# 2. 메인 영역 분리 (제목 전용 영역과 입력 전용 영역)
# 제목 고정
st.title("Data Mining Analyzer")
st.markdown("---")

# 입력창이 제목을 밀어내지 않도록 공간 점유 방식 변경
# 빈 공간(Empty)을 사용해 영역을 미리 확보함
input_area = st.empty()
analysis_area = st.container()

with input_area:
    data_frame = None
    target_column = None

    if input_mode == "Text Input":
        user_text = st.text_area("Input text for analysis", placeholder="Paste your text here.", height=150)
        if user_text: 
            data_frame = pd.DataFrame({"Content": [user_text]})
            target_column = "Content"
    elif input_mode == "CSV Upload":
        uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
        if uploaded_file: 
            data_frame = pd.read_csv(uploaded_file)
            target_column = st.selectbox("Select Column", data_frame.columns)
    elif input_mode == "PDF Document":
        uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
        if uploaded_file:
            reader = PdfReader(uploaded_file)
            text_content = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])
            data_frame = pd.DataFrame({"Content": [text_content]})
            target_column = "Content"

# 3. 분석 결과 영역
with analysis_area:
    set_matplotlib_font()
    if data_frame is not None:
        st.markdown("---")
        if input_mode != "CSV Upload":
            st.write(f"**Target Column:** '{target_column}'")
        
        if st.button("Run Analysis", type="primary"):
            frequency, correlation_df, word_score_df, graph = run_quantitative_analysis(data_frame, target_column)
            
            tabs = st.tabs(["Dashboard (WordCloud)", "Keyword List", "Co-occurrence Network"])
            
            with tabs[0]:
                if frequency: st.image(generate_wordcloud(frequency).to_array())
            with tabs[1]:
                st.table(word_score_df.sort_values('Score', ascending=False).head(20))
            with tabs[2]:
                if graph and len(graph.nodes) > 0:
                    fig, ax = plt.subplots(figsize=(10, 8))
                    pos = nx.spring_layout(graph, k=0.5)
                    nx.draw(graph, pos, with_labels=True, node_color='skyblue', font_size=12, ax=ax, font_family='NanumGothic')
                    st.pyplot(fig)
                else: st.warning("Insufficient data.")