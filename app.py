import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt  # 이 부분이 누락되면 NameError가 발생한다
from pypdf import PdfReader
import openpyxl
from analyzer import run_analysis, set_font, generate_wordcloud

st.set_page_config(layout="wide")

# Sidebar 설정
with st.sidebar:
    st.title("User Guide")
    input_mode = st.radio("Input Source", ["CSV/Excel Upload", "PDF Document", "Text Input"])
    
    if "data" not in st.session_state:
        st.session_state.data = None
        st.session_state.column = None

    if input_mode == "CSV/Excel Upload":
        uploaded = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx", "xls"])
        if uploaded:
            try:
                if uploaded.name.lower().endswith('.csv'):
                    st.session_state.data = pd.read_csv(uploaded)
                else:
                    st.session_state.data = pd.read_excel(uploaded)
                
                cols = st.session_state.data.select_dtypes(include=['object']).columns.tolist()
                if cols:
                    st.session_state.column = st.selectbox("Select Text Column", cols)
            except Exception as e:
                st.error(f"Error: {e}")
            
    elif input_mode == "PDF Document":
        uploaded = st.file_uploader("Upload PDF", type=["pdf"])
        if uploaded:
            reader = PdfReader(uploaded)
            text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])
            st.session_state.data = pd.DataFrame({"Content": [text]})
            st.session_state.column = "Content"
            
    elif input_mode == "Text Input":
        text = st.text_area("Input text", height=150)
        if text:
            st.session_state.data = pd.DataFrame({"Content": [text]})
            st.session_state.column = "Content"

# 메인 화면
st.title("Data Mining Analyzer")

if st.session_state.data is not None and st.session_state.column:
    if st.button("Run Analysis", type="primary"):
        set_font()
        result_df, token_counts = run_analysis(st.session_state.data, st.session_state.column)
        
        if result_df is not None:
            st.table(result_df)
            st.subheader("Frequency Visualization")
            
            # Matplotlib 객체 생성
            fig, ax = plt.subplots()
            wc = generate_wordcloud(token_counts)
            ax.imshow(wc, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig)
        else:
            st.error("No meaningful tokens detected. Check the column selection.")