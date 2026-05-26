import streamlit as st
import pandas as pd
from analyzer import process_dataframe_mining, generate_wordcloud_obj

st.set_page_config(layout="wide")
st.title("Semantic Taxonomy Analyzer")

with st.sidebar:
    # Taxonomy 설정 기능 추가
    st.header("Taxonomy Settings")
    category = st.multiselect("Define Categories", ["Methodology", "Theory", "Result", "Discussion"])
    
    # 기존 파일 업로드
    uploaded_file = st.file_uploader("Upload Text Data (CSV)", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    word_df, words = process_dataframe_mining(df)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Word Frequency Analysis")
        st.bar_chart(word_df.set_index("Word"))
    
    with col2:
        st.subheader("Taxonomy Mapping")
        # 여기서 Taxonomy 기반 분류 로직을 구현할 수 있다.
        st.write("Selected Categories:", category)
        st.dataframe(word_df)