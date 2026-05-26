import streamlit as st
import pandas as pd
from analyzer import run_quantitative_analysis, generate_wordcloud

st.set_page_config(layout="wide")
st.title("Professional Content Analyzer (KH Coder Integrated)")

uploaded_file = st.sidebar.file_uploader("Upload Data (CSV)", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    col = st.selectbox("Column to Analyze", df.columns)
    
    if st.button("Run Comprehensive Analysis"):
        freq, corr_df, word_df = run_quantitative_analysis(df, col)
        
        # [Tab 1] 시각화 (워드클라우드)
        t1, t2, t3 = st.tabs(["Dashboard (WordCloud)", "Taxonomy Mapping", "Co-occurrence Network"])
        with t1:
            st.image(generate_wordcloud(freq).to_array())
        
        # [Tab 2] 분류 분석 (매핑)
        with t2:
            targets = st.text_input("Target Keywords (comma separated)", "분석, 데이터")
            target_list = [t.strip() for t in targets.split(",")]
            st.table(word_df[word_df['Word'].isin(target_list)])
            
        # [Tab 3] 관계 분석 (KH Coder 스타일)
        with t3:
            st.write("단어 간 유사도 네트워크 행렬 (Co-occurrence)")
            st.dataframe(corr_df.style.background_gradient(cmap='Greens'))