import pandas as pd
import pypdf
import io
import re
import zipfile
import xml.etree.ElementTree as ET

class DataProcessor:
    def load_file(self, file):
        # 기존에 잘 되던 로직 유지
        if file.name.lower().endswith(('.ttf', '.py', '.js', '.css', '.yaml', '.txt')):
            return None
        content = file.getvalue()
        try:
            if file.name.lower().endswith('.pdf'):
                reader = pypdf.PdfReader(io.BytesIO(content))
                text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
                df = pd.DataFrame({'combined': [text]})
            elif file.name.lower().endswith(('.xlsx', '.xls')):
                try:
                    # [대용량 무의존성 패치] 외부 라이브러리 없이 순수 내장 XML 스트리밍으로 텍스트만 고속 추출
                    strings = []
                    with zipfile.ZipFile(io.BytesIO(content)) as z:
                        # 엑셀 내부의 실제 데이터 문자열 맵 추출
                        if 'xl/sharedStrings.xml' in z.namelist():
                            with z.open('xl/sharedStrings.xml') as f:
                                for event, elem in ET.iterparse(f, events=('end',)):
                                    if elem.tag.endswith('t'): # 텍스트 태그 검색
                                        if elem.text:
                                            strings.append(elem.text)
                                        elem.clear()
                    
                    if strings:
                        # 원형 데이터 구조와 완벽히 호환되도록 단일 컬럼 프레임 생성
                        df = pd.DataFrame({'combined': [' '.join(strings)]})
                    else:
                        # 텍스트 맵이 비어있을 경우 판다스 기본 로더로 안전하게 대체
                        df = pd.read_excel(io.BytesIO(content))
                except Exception:
                    df = pd.read_excel(io.BytesIO(content))
            else:
                df = pd.read_csv(io.BytesIO(content), encoding='utf-8-sig')
            
            # 기존 원형 데이터 가공 흐름 100% 동일하게 유지
            df = df.fillna('').astype(str)
            df['combined'] = df.apply(lambda row: ' '.join(row.values), axis=1)
            return df[['combined']]
        except Exception:
            return None

    def normalize(self, text):
        # 기존 정제 로직 완벽 유지
        if not isinstance(text, str):
            text = str(text) if text is not None else ""
        
        text = re.sub(r'[^가-힣a-zA-Z0-9\s]', ' ', text).lower()
        words = text.split()
        
        noise_words = {
            'fonts', 'visualizer', 'process', 'engine', 'main', 'py', 'ttf', 'otf', 
            'csv', 'xlsx', 'pdf', 'modules', 'data', 'git', 'commit', 'push', 
            'run', 'fix', 'cloud', 'bash', 'filter', 'rerun', 'loading', 'st', 'streamlit'
        }
        
        # 반환값 규칙 원형 유지
        return [w for w in words if (len(w) > 1 or re.match(r'[가-힣]', w)) and w not in noise_words]