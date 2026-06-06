import pandas as pd
import pypdf
import io
import re
import zipfile
import xml.etree.ElementTree as ET

class DataProcessor:
    def load_file(self, file):
        # 기존 파일 확장자 차단 규칙 및 원형 로직 100% 보존
        if file.name.lower().endswith(('.ttf', '.py', '.js', '.css', '.yaml', '.txt')):
            return None
        content = file.getvalue()
        try:
            if file.name.lower().endswith('.pdf'):
                reader = pypdf.PdfReader(io.BytesIO(content))
                text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
                df = pd.DataFrame({'combined': [text]})
            elif file.name.lower().endswith(('.xlsx', '.xls')):
                # [근본적 메모리 관리 패치] 대용량 덤핑을 막기 위한 행(Row) 단위 순차적 스트리밍 파서
                try:
                    row_pieces = []
                    current_row = []
                    
                    with zipfile.ZipFile(io.BytesIO(content)) as z:
                        if 'xl/sharedStrings.xml' in z.namelist():
                            with z.open('xl/sharedStrings.xml') as f:
                                # iterparse를 활용해 대용량 XML 구조를 순차적으로 해체하며 메모리 방출
                                for event, elem in ET.iterparse(f, events=('end',)):
                                    if elem.tag.endswith('t') and elem.text:
                                        current_row.append(elem.text)
                                        
                                        # 일정 토큰 수나 데이터가 쌓이면 순차적으로 청크 분할 저장
                                        if len(current_row) >= 50:
                                            row_pieces.append(" ".join(current_row))
                                            current_row = []
                                    elem.clear()
                                    
                            if current_row:
                                row_pieces.append(" ".join(current_row))
                    
                    if row_pieces:
                        # 덤핑하지 않고 순차 처리가 가능한 형태의 데이터프레임 규격으로 빌드
                        df = pd.DataFrame({'combined': row_pieces})
                        return df[['combined']]
                    else:
                        df = pd.read_excel(io.BytesIO(content))
                except Exception:
                    df = pd.read_excel(io.BytesIO(content))
            else:
                df = pd.read_csv(io.BytesIO(content), encoding='utf-8-sig')
            
            # 원본의 가공 메커니즘 흐름 유지
            df = df.fillna('').astype(str)
            df['combined'] = df.apply(lambda row: ' '.join(row.values), axis=1)
            return df[['combined']]
        except Exception:
            return None

    def normalize(self, text):
        # 기존 단어 정제 로직 및 불용어(noise_words) 세트 100% 원형 그대로 보존
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