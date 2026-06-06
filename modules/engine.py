import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer

class CoOccurrenceEngine:
    @staticmethod
    def create_matrix(tokens_list):
        if not tokens_list:
            return None
            
        # 1차원 데이터가 넘어오든 2차원이 넘어오든 안전하게 문장 배열로 가공
        if isinstance(tokens_list[0], list):
            sentences = [" ".join(tokens) for tokens in tokens_list if tokens]
        else:
            sentences = [" ".join(tokens_list)]
            
        if not sentences or all(not s.strip() for s in sentences):
            return None

        try:
            # 어떤 유니코드 문자든 공백이 아니면 하나의 단어로 인정하는 정규식 패턴 주입
            vectorizer = CountVectorizer(min_df=1, token_pattern=r'\S+')
            X = vectorizer.fit_transform(sentences)
            
            if X.shape[1] == 0:
                return None
                
            word_freqs = np.array(X.sum(axis=0)).flatten()
            Xc = (X.T * X)
            Xc_dense = Xc.toarray().astype(float)
            
            np.fill_diagonal(Xc_dense, word_freqs)
            
            return pd.DataFrame(
                Xc_dense, 
                columns=vectorizer.get_feature_names_out(), 
                index=vectorizer.get_feature_names_out()
            )
            
        except ValueError as e:
            if "empty vocabulary" in str(e):
                return None
            raise e