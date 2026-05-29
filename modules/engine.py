import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer

class CoOccurrenceEngine:
    @staticmethod
    def create_matrix(tokens_list):
        sentences = [" ".join(tokens) for tokens in tokens_list]
        vectorizer = CountVectorizer(min_df=1)
        X = vectorizer.fit_transform(sentences)
        word_freqs = np.array(X.sum(axis=0)).flatten()
        Xc = (X.T * X)
        Xc_dense = Xc.toarray().astype(float)
        np.fill_diagonal(Xc_dense, word_freqs)
        return pd.DataFrame(Xc_dense, 
                            columns=vectorizer.get_feature_names_out(), 
                            index=vectorizer.get_feature_names_out())