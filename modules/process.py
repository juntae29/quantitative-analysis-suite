import pandas as pd
import pypdf
import io
import re

class DataProcessor:
    def load_file(self, file):
        if file.name.lower().endswith(('.ttf', '.py', '.js', '.css', '.yaml', '.txt')):
            return None
            
        content = file.getvalue()
        try:
            # 1. PDF 파일 처리
            if file.name.lower().endswith('.pdf'):
                reader = pypdf.PdfReader(io.BytesIO(content))
                text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
                df = pd.DataFrame({'combined': [text]})
                return df[['combined']]
                
            # 2. Excel (XLSX, XLS) 파일 처리 (판다스 내부 엔진 우회 방식)
            elif file.name.lower().endswith(('.xlsx', '.xls')):
                # 최신 파이썬 스트림 호환성을 위해 판다스 메서드에 엔진을 명시적으로 주입
                df = pd.read_excel(io.BytesIO(content), engine='openpyxl')
                
            # 3. CSV 파일 처리
            else:
                df = pd.read_csv(io.BytesIO(content), encoding='utf-8-sig')
            
            # 공통 데이터 정제 및 병합
            df = df.fillna('').astype(str)
            if not df.empty:
                df['combined'] = df.apply(lambda row: ' '.join(row.values), axis=1)
                return df[['combined']]
            else:
                return None
                
        except Exception:
            return None

    def normalize(self, text):
        if not isinstance(text, str):
            text = str(text) if text is not None else ""
        
        text = re.sub(r'[^가-힣a-zA-Z0-9\s]', ' ', text).lower()
        words = text.split()
        
        noise_words = {
            'fonts', 'visualizer', 'process', 'engine', 'main', 'py', 'ttf', 'otf', 
            'csv', 'xlsx', 'pdf', 'modules', 'data', 'git', 'commit', 'push', 
            'run', 'fix', 'cloud', 'bash', 'filter', 'rerun', 'loading', 'st', 'streamlit'
        }
        
        return [w for w in words if (len(w) > 1 or re.match(r'[가-힣]', w)) and w not in noise_words]