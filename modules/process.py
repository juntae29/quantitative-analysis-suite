import pandas as pd
import pypdf, io, re

class DataProcessor:
    def load_file(self, file):
        if file.name.lower().endswith(('.ttf', '.py', '.js', '.css', '.yaml', '.txt')):
            return None
        content = file.getvalue()
        try:
            # 텍스트 인코딩을 명시적으로 utf-8로 강제 처리
            if file.name.lower().endswith('.pdf'):
                reader = pypdf.PdfReader(io.BytesIO(content))
                text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
                df = pd.DataFrame({'combined': [text]})
            elif file.name.lower().endswith(('.xlsx', '.xls')):
                df = pd.read_excel(io.BytesIO(content))
            else:
                df = pd.read_csv(io.BytesIO(content), encoding='utf-8-sig')
            
            df = df.fillna('').astype(str)
            df['combined'] = df.apply(lambda row: ' '.join(row.values), axis=1)
            return df[['combined']]
        except:
            return None

    def normalize(self, text):
    # 입력값이 문자열이 아닐 경우 빈 문자열로 처리하여 에러 방지
    if not isinstance(text, str):
        text = str(text) if text is not None else ""
        
    # 이후 기존 정제 로직 진행
    text = re.sub(r'[^가-힣a-zA-Z0-9\s]', ' ', text).lower()
        words = text.split()
        
        # 시스템 노이즈 단어 목록def normalize
        noise_words = {
            'fonts', 'visualizer', 'process', 'engine', 'main', 'py', 'ttf', 'otf', 
            'csv', 'xlsx', 'pdf', 'modules', 'data', 'git', 'commit', 'push', 
            'run', 'fix', 'cloud', 'bash', 'filter', 'rerun', 'loading', 'st', 'streamlit'
        }
        
        # 3. 필터링 (한글은 1자여도 의미가 있으므로, '한글이면 통과, 영어는 1자 초과' 조건 적용)
        return [w for w in words if (len(w) > 1 or re.match(r'[가-힣]', w)) and w not in noise_words]