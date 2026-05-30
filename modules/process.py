import pandas as pd
import pypdf, io, re

class DataProcessor:
    def load_file(self, file):
        if file.name.lower().endswith(('.ttf', '.py', '.js', '.css', '.yaml', '.txt')):
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
        except:
            return None

    def normalize(self, text):
        # 한글을 그대로 보존하면서 토큰화
        text = re.sub(r'[^가-힣a-zA-Z0-9\s]', ' ', str(text)).lower()
        words = text.split()
        noise_words = {'fonts', 'visualizer', 'process', 'engine', 'main', 'py', 'ttf', 'otf', 'csv', 'xlsx', 'pdf', 'modules', 'data', 'git', 'commit', 'push', 'run', 'fix', 'cloud', 'bash', 'filter'}
        return [w for w in words if len(w) > 1 and w not in noise_words]