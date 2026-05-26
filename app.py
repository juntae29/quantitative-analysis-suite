import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from pypdf import PdfReader
from analyzer import run_quantitative_analysis, generate_wordcloud, set_matplotlib_font

st.set_page_config(layout="wide")

# 사이드바 설정
with st.sidebar:
    st.title("Settings")
    input_mode = st.radio("Input Source", ["CSV Upload", "PDF Document", "Text Input"])

# 메인 화면 레이아웃 강제 고정
# 상단 (제목 + 안내) / 하단 (입력창)을 명확히 구분
st.title("Data Mining Analyzer")
st.markdown("---")

# 안내 문구를 제목 바로 아래 고정하기 위해 명시적 텍스트 블록 생성
st.markdown("""
### 💡 User Guide
1. Select the input method from the left sidebar.
2. The input field will appear below this guide.
3. Click 'Run Analysis' to see the results.
""")
st.markdown("---")

# 입력창을 위한 고정 컨테이너
input_container = st.container()

with input_container:
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

# 결과 영역
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