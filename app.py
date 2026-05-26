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
    
    if "data" not in st.session_state:
        st.session_state.data = None

    if input_mode == "CSV Upload":
        uploaded = st.file_uploader("Upload CSV", type=["csv"])
        if uploaded:
            st.session_state.data = pd.read_csv(uploaded)
            # 텍스트 타입인 열만 필터링하여 리스트업
            text_columns = st.session_state.data.select_dtypes(include=['object']).columns.tolist()
            if text_columns:
                selected_col = st.selectbox("Select Text Column", text_columns)
                st.session_state.column = selected_col
                st.write("Preview:", st.session_state.data[selected_col].astype(str).head(3))
            else:
                st.warning("No text-based column found in CSV.")
            
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

    st.markdown("---")
    st.text("여호와를 찬양하라!")

st.title("Data Mining Analyzer")

if st.session_state.data is not None and "column" in st.session_state:
    if st.button("Run Analysis", type="primary"):
        set_font()
        _, _, result_df, _ = run_analysis(st.session_state.data, st.session_state.column)
        
        if result_df is not None and not result_df.empty:
            st.table(result_df.sort_values('Score', ascending=False).head(20))
        else:
            st.error("No valid nouns or adjectives found. Please check your data.")
else:
    st.info("Please provide input in the sidebar.")