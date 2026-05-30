import pandas as pd
import pypdf, io, re

class DataProcessor:
    def load_file(self, file):
        # 강력한 필터링: 코드 파일, 폰트 파일, 시스템 파일 무시
        excluded_extensions = ('.ttf', '.py', '.js', '.css', '.yaml', '.txt')
        if file.name.lower().endswith(excluded_extensions):
            return None
            
        content = file.getvalue()
        try:
            if file.name.lower().endswith('.pdf'):
                reader = pypdf.PdfReader(io.BytesIO(content))
                text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
                df = pd.DataFrame({'combined': [text]})
            elif file.name.lower().endswith(('.xlsx', '.xls')):
                df = pd.read_excel(io.BytesIO(content))
            else:
                df = pd.read_csv(io.BytesIO(content))
            
            df = df.fillna('').astype(str)
            df['combined'] = df.apply(lambda row: ' '.join(row.values), axis=1)
            return df[['combined']]
        except Exception:
            return None

    def normalize(self, text):
        # 한글/영어/숫자 이외의 불필요한 특수문자 제거 및 토큰화
        words = re.sub(r'[^a-zA-Z0-9가-힣\s]', ' ', str(text)).lower().split()
        # 추가 필터링: 너무 짧은 단어나 의미 없는 키워드 제거
        return [w for w in words if len(w) > 1]