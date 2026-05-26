import streamlit as st
import pandas as pd
from pypdf import PdfReader
from analyzer import run_analysis, set_font

st.set_page_config(layout="wide")

with st.sidebar:
    st.title("User Guide")
    st.markdown("1. Select source.\n2. Upload file.\n3. Run analysis.")
    st.markdown("---")
    
    input_mode = st.radio("Input Source", ["CSV Upload", "PDF Document", "Text Input"])
    
    if "df" not in st.session_state:
        st.session_state.df = None
    
    if input_mode == "CSV Upload":
        uploaded = st.file_uploader("Upload CSV", type=["csv"])
        if uploaded:
            # Handle encoding issues
            try:
                st.session_state.df = pd.read_csv(uploaded, encoding='utf-8')
            except:
                st.session_state.df = pd.read_csv(uploaded, encoding='cp949')
            
            text_cols = st.session_state.df.select_dtypes(include=['object']).columns.tolist()
            if text_cols:
                st.session_state.selected_col = st.selectbox("Select Text Column", text_cols)
            
    elif input_mode == "PDF Document":
        uploaded = st.file_uploader("Upload PDF", type=["pdf"])
        if uploaded:
            reader = PdfReader(uploaded)
            text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])
            st.session_state.df = pd.DataFrame({"Content": [text]})
            st.session_state.selected_col = "Content"
            
    elif input_mode == "Text Input":
        text = st.text_area("Input text", height=150)
        if text:
            st.session_state.df = pd.DataFrame({"Content": [text]})
            st.session_state.selected_col = "Content"

    st.markdown("---")
    st.text("여호와를 찬양하라!")

st.title("Data Mining Analyzer")

if st.session_state.df is not None and "selected_col" in st.session_state:
    if st.button("Run Analysis", type="primary"):
        set_font()
        _, _, result_df, _ = run_analysis(st.session_state.df, st.session_state.selected_col)
        
        if result_df is not None and not result_df.empty:
            st.table(result_df)
        else:
            st.error("No valid tokens found. Please check if the data contains Korean text.")
else:
    st.info("Please provide input in the sidebar.")