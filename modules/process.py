import pandas as pd
import pypdf
import io
import re

class DataProcessor:
    def load_file(self, file):
        # 기존에 잘 되던 확장자 필터링 로직 유지
        if file.name.lower().endswith(('.ttf', '.py', '.js', '.css', '.yaml', '.txt')):
            return None
            
        content = file.getvalue()
        try:
            if file.name.lower().endswith('.pdf'):
                reader = pypdf.PdfReader(io.BytesIO(content))
                text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
                # PDF는 이미 텍스트 추출이 끝났으므로 바로 정형화하여 반환함
                df = pd.DataFrame({'combined': [text]})
                return df[['combined']]
                
            elif file.name.lower().endswith(('.xlsx', '.xls')):
                # 클라우드 배포 환경(Linux)을 위해 engine='openpyxl'을 명시적으로 지정함
                df = pd.read_excel(io.BytesIO(content), engine='openpyxl')
            else:
                df = pd.read_csv(io.BytesIO(content), encoding='utf-8-sig')
            
            # CSV 및 Excel 파일 데이터 정제 및 결합
            df = df.fillna('').astype(str)
            if not df.empty:
                df['combined'] = df.apply(lambda row: ' '.join(row.values), axis=1)
                return df[['combined']]
            else:
                return None
                
        except Exception:
            return None

    def normalize(self, text):
        # 기존 정제 로직 유지
        if not isinstance(text, str):
            text = str(text) if text is not None else ""
        
        text = re.sub(r'[^가-힣a-zA-Z0-9\s]', ' ', text).lower()
        words = text.split()
        
        noise_words = {
            'fonts', 'visualizer', 'process', 'engine', 'main', 'py', 'ttf', 'otf', 
            'csv', 'xlsx', 'pdf', 'modules', 'data', 'git', 'commit', 'push', 
            'run', 'fix', 'cloud', 'bash', 'filter', 'rerun', 'loading', 'st', 'streamlit'
        }
        
        # 반환값 유지
        return [w for w in words if (len(w) > 1 or re.match(r'[가-힣]', w)) and w not in noise_words]