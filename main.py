import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import io
from modules.process import DataProcessor
from modules.engine import CoOccurrenceEngine
from modules.visualizer import Visualizer
from modules.analysis import WordAnalyzer
from modules.kwic import KwicEngine

st.set_page_config(layout="wide")
st.markdown("### Quantitative Analysis & Text Mining Suite")

with st.sidebar:
    n_words = st.slider("Top N Words", 5, 50, 20)
    chart_size = st.slider("Chart Size", 5, 15, 10)
    st.markdown("### Data Input")
    file = st.file_uploader("Upload CSV, XLSX, or PDF", type=['csv', 'xlsx', 'pdf'])
    manual_text = st.text_area("Or Enter Text Directly")
    
    if st.button("Run Analysis"):
        processor = DataProcessor()
        if file:
            df = processor.load_file(file)
            
            # 클라우드 배포 환경에서의 파일 로드 실패 및 빈 파일 예외 처리
            if df is None or (isinstance(df, pd.DataFrame) and df.empty):
                st.error("파일을 읽어오지 못했거나 빈 파일이다. 파일 포맷을 확인하라.")
                st.stop()
                
            if 'combined' not in df.columns:
                if len(df.columns) > 0:
                    df = df.rename(columns={df.columns[0]: 'combined'})
                else:
                    st.error("업로드된 파일에 데이터가 존재하지 않는다.")
                    st.stop()
        elif manual_text:
            df = pd.DataFrame({'combined': [manual_text]})
        else:
            st.error("Please upload a file or enter text.")
            st.stop()
        
        st.session_state.df = df
        
        # [기존 기능 유지 + 히트맵 데이터 보강]
        tokens_list = [processor.normalize(str(t)) for t in df['combined'].fillna('') if str(t).strip() != '']
        flat_tokens = [t for sublist in tokens_list for t in sublist if len(t) > 1]
        
        if flat_tokens:
            # engine.py에서 예외가 발생하거나 단어가 부족하면 None을 반환함
            matrix = CoOccurrenceEngine.create_matrix(flat_tokens)
            if matrix is not None and not matrix.empty:
                st.session_state.matrix = matrix
            else:
                st.error("유효한 분석 단어를 추출하지 못했다. 입력 텍스트나 불용어 설정을 확인하라.")
                st.session_state.matrix = None
                st.stop()
        else:
            st.error("분석할 단어가 부족합니다.")
            st.session_state.matrix = None
            st.stop()

if 'matrix' in st.session_state and st.session_state.matrix is not None:
    tab1, tab2, tab3 = st.tabs(["Network Graph", "Statistics & Clustering", "KWIC Analysis"])
    with tab1:
        fig, ax = plt.subplots(figsize=(chart_size, chart_size))
        Visualizer.draw_network(st.session_state.matrix, n_words, ax)
        st.pyplot(fig)
        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        st.download_button("Download Network Graph (PNG)", buf.getvalue(), "network_graph.png", "image/png")
    with tab2:
        tool = st.radio("Select Tool", ["Centrality", "Clustering", "MDS Map", "Dendrogram", "Heatmap"], horizontal=True, key="a_tool")
        st.divider()
        subset = st.session_state.matrix.iloc[:n_words, :n_words]
        if tool == "Centrality":
            df_res = WordAnalyzer.get_centrality(subset)
            st.dataframe(df_res, use_container_width=True)
            csv = df_res.to_csv().encode('utf-8-sig')
            st.download_button("Download Centrality Data (CSV)", csv, "centrality.csv", "text/csv")
        elif tool == "Clustering":
            k_val = st.slider("Clusters (K)", 2, 6, 3, key="k_slider")
            df_res = WordAnalyzer.get_clustering(subset, k_val)
            st.dataframe(df_res, use_container_width=True)
            csv = df_res.to_csv().encode('utf-8-sig')
            st.download_button("Download Clustering Data (CSV)", csv, "clustering.csv", "text/csv")
        elif tool == "MDS Map":
            fig, ax = plt.subplots(figsize=(chart_size, chart_size * 0.7))
            coords, labels = WordAnalyzer.get_mds_coords(subset)
            Visualizer.draw_mds(coords, labels, ax)
            st.pyplot(fig)
            buf = io.BytesIO()
            fig.savefig(buf, format="png")
            st.download_button("Download MDS Map (PNG)", buf.getvalue(), "mds_map.png", "image/png")
        elif tool == "Dendrogram":
            fig, ax = plt.subplots(figsize=(chart_size, chart_size * 0.5))
            Visualizer.draw_dendrogram(subset, n_words, ax)
            st.pyplot(fig)
            buf = io.BytesIO()
            fig.savefig(buf, format="png")
            st.download_button("Download Dendrogram (PNG)", buf.getvalue(), "dendrogram.png", "image/png")
        elif tool == "Heatmap":
            fig, ax = plt.subplots(figsize=(chart_size, chart_size * 0.8))
            Visualizer.draw_heatmap(subset, ax)
            st.pyplot(fig)
            buf = io.BytesIO()
            fig.savefig(buf, format="png")
            st.download_button("Download Heatmap (PNG)", buf.getvalue(), "heatmap.png", "image/png")
    with tab3:
        st.subheader("KWIC Discovery & Search")
        top_keywords = WordAnalyzer.get_top_keywords(st.session_state.matrix, n=10)
        cols = st.columns(10)
        for i, word in enumerate(top_keywords):
            if cols[i].button(word, key=f"btn_{word}"):
                st.session_state.search_kw = word
        keyword = st.text_input("Enter keyword to search:", value=st.session_state.get('search_kw', ''))
        if keyword and 'df' in st.session_state:
            # 안전하게 st.session_state.df를 직접 참조하여 텍스트 결합을 수행함
            full_text = " ".join(st.session_state.df['combined'].astype(str))
            contexts = KwicEngine.get_context(full_text, keyword)
            if contexts:
                df_kwic = pd.DataFrame(contexts)
                st.dataframe(df_kwic, use_container_width=True)
                csv = df_kwic.to_csv(index=False).encode('utf-8-sig')
                st.download_button("Download KWIC Results (CSV)", csv, "kwic_results.csv", "text/csv")
            else:
                st.warning("Keyword not found.")