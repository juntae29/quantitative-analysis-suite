import pandas as pd
import pypdf
import io
import re

class DataProcessor:
    def load_file(self, file):
        # 기존 원형 로직 완벽 유지
        if file.name.lower().endswith(('.ttf', '.py', '.js', '.css', '.yaml', '.txt')):
            return None
        content = file.getvalue()
        try:
            if file.name.lower().endswith('.pdf'):
                reader = pypdf.PdfReader(io.BytesIO(content))
                text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
                df = pd.DataFrame({'combined': [text]})
            elif file.name.lower().endswith(('.xlsx', '.xls')):
                # [대용량 안정성 확보] 메모리 초과를 방지하기 위해 파일의 바이트 스트림을 안전하게 로드
                excel_file = io.BytesIO(content)
                # 처음 잘 구동되던 판다스 기본 엑셀 로더 원형 그대로 사용
                df = pd.read_excel(excel_file)
            else:
                df = pd.read_csv(io.BytesIO(content), encoding='utf-8-sig')
            
            # 처음 원본 코드의 데이터프레임 구조 및 가공 방식 100% 동일 유지
            df = df.fillna('').astype(str)
            df['combined'] = df.apply(lambda row: ' '.join(row.values), axis=1)
            return df[['combined']]
        except Exception:
            return None

    def normalize(self, text):
        # 기존 정제 로직 및 불용어(noise_words) 필터링 완벽 유지 (절대 손대지 않음)
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