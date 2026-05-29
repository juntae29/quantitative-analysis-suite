import pandas as pd
import numpy as np
from sklearn.manifold import MDS
from sklearn.cluster import KMeans

class WordAnalyzer:
    @staticmethod
    def get_centrality(matrix):
        degree = matrix.sum(axis=1)
        return pd.DataFrame(degree, columns=['Degree']).sort_values(by='Degree', ascending=False)

    @staticmethod
    def get_top_keywords(matrix, n=10):
        temp_matrix = matrix.copy()
        values = temp_matrix.values.astype(float)
        np.fill_diagonal(values, 0)
        centrality = pd.Series(values.sum(axis=1), index=temp_matrix.index)
        return centrality.nlargest(n).index.tolist()

    @staticmethod
    def get_clustering(matrix, k):
        kmeans = KMeans(n_clusters=k, n_init='auto')
        data_for_cluster = matrix.copy()
        data_for_cluster['cluster'] = kmeans.fit_predict(matrix)
        return data_for_cluster[['cluster']].sort_values(by='cluster')

    @staticmethod
    def get_mds_coords(matrix):
        # MDS 좌표 계산 메서드 복구
        mds = MDS(n_components=2, dissimilarity='precomputed', random_state=42)
        # 거리를 기반으로 MDS 계산 (빈도 행렬을 거리로 변환)
        dist = 1 - (matrix / matrix.max().max())
        coords = mds.fit_transform(dist)
        return coords, matrix.index.tolist()