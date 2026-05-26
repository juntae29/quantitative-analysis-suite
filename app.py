import streamlit as st
import pandas as pd
from pypdf import PdfReader
from analyzer import run_analysis, set_font

st.set_page_config(layout="wide")

with st.sidebar:
    st.title("User Guide")
    st.markdown("1. Select source.\n2. Upload file.\n3. Run analysis.")
    st.markdown("---")
    
    input_mode = st.radio("Input Source", ["CSV/Excel Upload", "PDF Document", "Text Input"])
    
    if "data_frame" not in st.session_state:
        st.session_state.data_frame = None
    
    if input_mode == "CSV/Excel Upload":
        uploaded_file = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx", "xls"])
        if uploaded_file:
            if uploaded_file.name.endswith('.csv'):
                try:
                    st.session_state.data_frame = pd.read_csv(uploaded_file, encoding='utf-8')
                except:
                    st.session_state.data_frame = pd.read_csv(uploaded_file, encoding='cp949')
            else:
                # Excel: Load all sheets and let user select
                excel_file = pd.ExcelFile(uploaded_file)
                sheet_name = st.selectbox("Select Sheet", excel_file.sheet_names)
                st.session_state.data_frame = pd.read_excel(uploaded_file, sheet_name=sheet_name)
            
            if st.session_state.data_frame is not None:
                st.session_state.target_column = st.selectbox("Select Column", st.session_state.data_frame.columns)
            
    elif input_mode == "PDF Document":
        uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
        if uploaded_file:
            reader = PdfReader(uploaded_file)
            full_text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])
            st.session_state.data_frame = pd.DataFrame({"Content": [full_text]})
            st.session_state.target_column = "Content"
            
    elif input_mode == "Text Input":
        user_input = st.text_area("Input text", height=150)
        if user_input:
            st.session_state.data_frame = pd.DataFrame({"Content": [user_input]})
            st.session_state.target_column = "Content"

    st.markdown("---")
    st.text("여호와를 찬양하라!")

st.title("Data Mining Analyzer")

if st.session_state.data_frame is not None and "target_column" in st.session_state:
    if st.button("Run Analysis", type="primary"):
        set_font()
        result_table = run_analysis(st.session_state.data_frame, st.session_state.target_column)
        
        if result_table is not None:
            st.table(result_table)
        else:
            st.error("Analysis failed. Please check the input data.")
else:
    st.info("Please provide input in the sidebar.")