import streamlit as st
import pandas as pd
from analyzer import process_advanced_mining, generate_wordcloud_obj, map_taxonomy

st.title("Advanced Data Mining Analyzer")

# 1. 입력 모드 선택
mode = st.sidebar.selectbox("Select Mode", ["CSV Upload", "Custom Text Input"])

df = None

# 2. 데이터 입력 로직
if mode == "CSV Upload":
    f = st.sidebar.file_uploader("Upload CSV", type=["csv"])
    if f: df = pd.read_csv(f)

elif mode == "Custom Text Input":
    user_text = st.text_area("분석할 문장을 입력하세요:", height=200)
    if st.button("분석 실행"):
        if user_text:
            # 입력된 텍스트를 데이터프레임 형식으로 즉시 변환
            df = pd.DataFrame({"User_Input": [user_text]})
            st.write("입력된 텍스트가 데이터셋으로 등록되었습니다.")
        else:
            st.warning("분석할 내용을 입력해 주세요.")

# 3. 데이터가 존재할 때 분석 실행
if df is not None and not df.empty:
    selected_col = st.selectbox("분석할 컬럼을 선택하세요:", df.columns)
    
    # 텍스트 분석 실행
    word_df, word_dict = process_advanced_mining(df, selected_col)
    
    if not word_df.empty:
        col1, col2 = st.columns(2)
        with col1: st.image(generate_wordcloud_obj(word_dict).to_array())
        with col2: st.bar_chart(word_df.set_index("Word"))
        
        # Taxonomy 설정 및 매핑
        cat_name = st.text_input("Category Name", "Methodology")
        cat_words = st.text_input("Keywords", "regression, analysis, model")
        
        if st.button("Taxonomy 매핑 결과 보기"):
            tax_dict = {cat_name: [w.strip().lower() for w in cat_words.split(",")]}
            mapping = map_taxonomy(word_dict.keys(), tax_dict)
            st.write(f"**{cat_name}** 분류 결과:", mapping[cat_name])
    else:
        st.error("텍스트 분석 결과가 없습니다. 입력 내용을 확인하세요.")