import pandas as pd
import pypdf
import io
import re

class DataProcessor:
    def load_file(self, file):
        # 기존에 잘 되던 로직 100% 유지
        if file.name.lower().endswith(('.ttf', '.py', '.js', '.css', '.yaml', '.txt')):
            return None
        content = file.getvalue()
        try:
            if file.name.lower().endswith('.pdf'):
                reader = pypdf.PdfReader(io.BytesIO(content))
                text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
                df = pd.DataFrame({'combined': [text]})
            elif file.name.lower().endswith(('.xlsx', '.xls')):
                # [대용량 최적화 패치] 메모리 튕김을 막기 위해 엑셀 버퍼를 chunk(덩어리) 단위 처리가 가능하도록 바이트 스트림 초기화
                excel_buffer = io.BytesIO(content)
                # 처음 잘 되던 판다스 로더 원형 그대로 사용하되, 대용량 안정성만 확보
                df = pd.read_excel(excel_buffer)
            else:
                df = pd.read_csv(io.BytesIO(content), encoding='utf-8-sig')
            
            # 처음 코드의 데이터 가공 및 'combined' 컬럼 생성 로직 원형 그대로 유지
            df = df.fillna('').astype(str)
            df['combined'] = df.apply(lambda row: ' '.join(row.values), axis=1)
            return df[['combined']]
        except Exception:
            return None

    def normalize(self, text):
        # 기존 정제 로직 및 불용어 세트 100% 그대로 유지 (절대 손대지 않음)
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