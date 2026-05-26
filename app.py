import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from pypdf import PdfReader
from analyzer import run_quantitative_analysis, generate_wordcloud, set_matplotlib_font

st.set_page_config(layout="wide")

# 1. Top Section: Title and Guide (Fixed at the top)
header_container = st.container()
with header_container:
    st.title("Data Mining Analyzer")
    st.markdown("---")
    st.markdown("### 💡 User Guide")
    st.markdown("1. Select the input method from the left sidebar.")
    st.markdown("2. Input your data or text in the section below.")
    st.markdown("3. Click 'Run Analysis' to generate insights.")
    st.markdown("---")

# 2. Bottom Section: Input and Analysis (Separate container)
input_analysis_container = st.container()
with input_analysis_container:
    set_matplotlib_font()
    input_mode = st.sidebar.radio("Input Source", ["CSV Upload", "PDF Document", "Text Input"])
    
    data_frame = None
    target_column = None

    # Input Logic inside the bottom container
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

    # Execution Logic inside the bottom container
    if data_frame is not None:
        if input_mode != "CSV Upload":
            st.write(f"**Target Column:** '{target_column}'")
        
        if st.button("Run Analysis", type="primary"):
            frequency, correlation_df, word_score_df, graph = run_quantitative_analysis(data_frame, target_column)
            
            tab1, tab2, tab3 = st.tabs(["Dashboard (WordCloud)", "Keyword List", "Co-occurrence Network"])
            
            with tab1:
                if frequency: 
                    st.image(generate_wordcloud(frequency).to_array())
            with tab2:
                st.table(word_score_df.sort_values('Score', ascending=False).head(20))
            with tab3:
                if graph and len(graph.nodes) > 0:
                    figure, axis = plt.subplots(figsize=(10, 8))
                    positions = nx.spring_layout(graph, k=0.5)
                    nx.draw(graph, positions, with_labels=True, node_color='skyblue', font_size=12, ax=axis, font_family='NanumGothic')
                    st.pyplot(figure)
                else: 
                    st.warning("Insufficient data for network visualization.")