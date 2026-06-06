import pandas as pd
import pypdf
import io
import re
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter

class DataProcessor:
    def load_file(self, file):
        # 기존 파일 확장자 차단 규칙 정책 100% 보존
        if file.name.lower().endswith(('.ttf', '.py', '.js', '.css', '.yaml', '.txt')):
            return None
        content = file.getvalue()
        try:
            if file.name.lower().endswith('.pdf'):
                reader = pypdf.PdfReader(io.BytesIO(content))
                text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
                df = pd.DataFrame({'combined': [text]})
            elif file.name.lower().endswith(('.xlsx', '.xls')):
                # [초강력 메모리 다이어트: 빈도수 기반 상위 300개 단어 제한 전처리]
                try:
                    all_words_list = []
                    row_contents = []
                    
                    with zipfile.ZipFile(io.BytesIO(content)) as z:
                        if 'xl/sharedStrings.xml' in z.namelist():
                            with z.open('xl/sharedStrings.xml') as f:
                                for event, elem in ET.iterparse(f, events=('end',)):
                                    if elem.tag.endswith('t') and elem.text:
                                        cleaned_words = self.normalize(elem.text)
                                        if cleaned_words:
                                            all_words_list.extend(cleaned_words)
                                            row_contents.append(cleaned_words)
                                    elem.clear()
                    
                    if row_contents:
                        # 1단계: 전체 단어 중 상위 300개 핵심 단어만 추출 (메모리 덤핑 폭발의 주범인 하위 노이즈 단어 제거)
                        word_counts = Counter(all_words_list)
                        top_words = set([word for word, count in word_counts.most_common(300)])
                        
                        # 2단계: 핵심 단어만 필터링하여 순차 청크 데이터프레임 빌드
                        filtered_rows = []
                        current_chunk = []
                        
                        for row in row_contents:
                            meaningful_words = [w for w in row if w in top_words]
                            if meaningful_words:
                                current_chunk.extend(meaningful_words)
                                
                            if len(current_chunk) >= 50:
                                filtered_rows.append(" ".join(current_chunk))
                                current_chunk = []
                                
                        if current_chunk:
                            filtered_rows.append(" ".join(current_chunk))
                            
                        df = pd.DataFrame({'combined': filtered_rows})
                        return df[['combined']]
                    else:
                        df = pd.read_excel(io.BytesIO(content))
                except Exception:
                    df = pd.read_excel(io.BytesIO(content))
            else:
                df = pd.read_csv(io.BytesIO(content), encoding='utf-8-sig')
            
            # 기존 원본 가공 흐름 완벽 유지
            df = df.fillna('').astype(str)
            df['combined'] = df.apply(lambda row: ' '.join(row.values), axis=1)
            return df[['combined']]
        except Exception:
            return None

    def normalize(self, text):
        # 원래 잘 되던 단어 정제 로직 및 불용어 세트 100% 동일 유지
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