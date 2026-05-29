import pandas as pd
import pypdf, io, re

class DataProcessor:
    def load_file(self, file):
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
            
            # 결측치를 빈 문자열로 대체 후 전체 문자열 변환
            df = df.fillna('').astype(str)
            df['combined'] = df.apply(lambda row: ' '.join(row.values), axis=1)
            return df[['combined']]
        except Exception:
            return None

    def normalize(self, text):
        return re.sub(r'[^a-zA-Z0-9가-힣\s]', ' ', str(text)).lower().split()