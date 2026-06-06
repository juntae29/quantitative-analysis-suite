import pandas as pd
import pypdf
import io
import re
import zipfile
import xml.etree.ElementTree as ET

class DataProcessor:
    def load_file(self, file):
        # 기존 파일 차단 규칙 및 원형 로직 100% 보존
        if file.name.lower().endswith(('.ttf', '.py', '.js', '.css', '.yaml', '.txt')):
            return None
        content = file.getvalue()
        try:
            if file.name.lower().endswith('.pdf'):
                reader = pypdf.PdfReader(io.BytesIO(content))
                text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
                df = pd.DataFrame({'combined': [text]})
            elif file.name.lower().endswith(('.xlsx', '.xls')):
                # [초경량 저메모리 스트리밍 패치] 메모리 OOM 방지를 위해 판다스를 거치지 않고 내장 XML 파서로 텍스트 직접 추출
                try:
                    text_pieces = []
                    with zipfile.ZipFile(io.BytesIO(content)) as z:
                        if 'xl/sharedStrings.xml' in z.namelist():
                            with z.open('xl/sharedStrings.xml') as f:
                                for event, elem in ET.iterparse(f, events=('end',)):
                                    if elem.tag.endswith('t') and elem.text:
                                        text_pieces.append(elem.text)
                                    elem.clear()
                    if text_pieces:
                        df = pd.DataFrame({'combined': [' '.join(text_pieces)]})
                    else:
                        df = pd.read_excel(io.BytesIO(content))
                except Exception:
                    df = pd.read_excel(io.BytesIO(content))
            else:
                df = pd.read_csv(io.BytesIO(content), encoding='utf-8-sig')
            
            # 기존 원본 코드의 'combined' 결합 가공 흐름 완벽 일치
            df = df.fillna('').astype(str)
            df['combined'] = df.apply(lambda row: ' '.join(row.values), axis=1)
            return df[['combined']]
        except Exception:
            return None

    def normalize(self, text):
        # 원래 잘 되던 단어 정제 로직 및 불용어 세트 100% 동일 유지 (절대 건드리지 않음)
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