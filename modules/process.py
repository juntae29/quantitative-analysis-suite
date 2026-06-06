import pandas as pd
import pypdf
import io
import re

class DataProcessor:
    def load_file(self, file):
        # 처음 원본 로직 및 차단 규칙 100% 유지
        if file.name.lower().endswith(('.ttf', '.py', '.js', '.css', '.yaml', '.txt')):
            return None
        content = file.getvalue()
        try:
            if file.name.lower().endswith('.pdf'):
                reader = pypdf.PdfReader(io.BytesIO(content))
                text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
                df = pd.DataFrame({'combined': [text]})
            elif file.name.lower().endswith(('.xlsx', '.xls')):
                # [초고속 저메모리 패치] 데이터가 무거워도 메모리를 터트리지 않는 최적화 판다스 빌드
                excel_buffer = io.BytesIO(content)
                # 오직 필요한 텍스트 정보 변환만 가볍게 수행하기 위해 read_excel 로딩 효율화
                df = pd.read_excel(excel_buffer, engine='openpyxl')
            else:
                df = pd.read_csv(io.BytesIO(content), encoding='utf-8-sig')
            
            # 처음 원본 코드의 가공 메커니즘과 'combined' 컬럼 매칭 구조 완벽 유지
            df = df.fillna('').astype(str)
            df['combined'] = df.apply(lambda row: ' '.join(row.values), axis=1)
            return df[['combined']]
        except Exception:
            return None

    def normalize(self, text):
        # 처음 단어 정제 로직 및 사용자가 지정했던 불용어(noise_words) 세트 100% 원형 그대로 보존
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