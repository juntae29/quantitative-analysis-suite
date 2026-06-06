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
                # [제안 반영: 상위 100개 핵심 텍스트 단어 선별 알고리즘]
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
                                            # 숫자로만 이루어진 단어는 그래프 왜곡 방지를 위해 원천 제외
                                            text_only_words = [w for w in cleaned_words if not w.isdigit()]
                                            if text_only_words:
                                                all_words_list.extend(text_only_words)
                                                row_contents.append(text_only_words)
                                    elem.clear()
                    
                    if row_contents:
                        # 전체 순수 텍스트 중 정확히 상위 100개 단어만 컷오프(Cut-off)하여 사전 구축
                        word_counts = Counter(all_words_list)
                        top_100_words = set([word for word, count in word_counts.most_common(100)])
                        
                        filtered_rows = []
                        current_chunk = []
                        
                        for row in row_contents:
                            # 제안하신 대로 상위 100개 단어 리스트에 포함된 단어들만 추출하여 재조립
                            meaningful_words = [w for w in row if w in top_100_words]
                            if meaningful_words:
                                current_chunk.extend(meaningful_words)
                                
                            if len(current_chunk) >= 40:
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
            
            # 기존 원본 파일 가공 흐름 완벽 유지
            df = df.fillna('').astype(str)
            df['combined'] = df.apply(lambda row: ' '.join(row.values), axis=1)
            return df[['combined']]
        except Exception:
            return None

    def normalize(self, text):
        # 기존 사용자 단어 정제 알고리즘 및 노이즈 필터링 완전 유지 (동일성 보장)
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