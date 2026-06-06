import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import platform
import os
import networkx as nx
import seaborn as sns
import math
from scipy.cluster.hierarchy import dendrogram, linkage

# 폰트 설정을 위한 로직을 별도 함수로 분리하여 가장 먼저 실행
def set_korean_font():
    font_path = os.path.join(os.path.dirname(__file__), '..', 'fonts', 'malgun.ttf')
    
    if os.path.exists(font_path):
        fm.fontManager.addfont(font_path)
        plt.rcParams['font.family'] = 'Malgun Gothic'
    else:
        if platform.system() == "Windows":
            plt.rcParams['font.family'] = 'Malgun Gothic'
        elif platform.system() == "Darwin":
            plt.rcParams['font.family'] = 'AppleGothic'
        else:
            plt.rcParams['font.family'] = 'sans-serif'
            
    plt.rcParams['axes.unicode_minus'] = False

# 모듈 로드 시 즉시 실행
set_korean_font()

class Visualizer:
    @staticmethod
    def draw_network(matrix, n_words, ax):
        top_matrix = matrix.iloc[:n_words, :n_words]
        G = nx.from_pandas_adjacency(top_matrix)
        
        # 빈도수 데이터 추출 (대각 행렬 요소)
        node_freqs = {node: int(matrix.loc[node, node]) for node in G.nodes()}
        
        # 노드 크기 스케일링: 빈도수 로그 스케일 적용 (최대 크기 제한)
        node_sizes = [max(math.log(node_freqs[n] + 1) * 800, 500) for n in G.nodes()]
        
        # 엣지 가중치 강화: 연계 횟수(weight)에 비례하여 굵기 변화
        edges = G.edges(data=True)
        weights = [data['weight'] * 0.5 for u, v, data in edges]
        
        pos = nx.spring_layout(G, k=0.5, seed=42)
        
        # 노드와 엣지 그리기
        nx.draw_networkx_nodes(G, pos, ax=ax, node_size=node_sizes, 
                               node_color='#E8EAF6', edgecolors='#FF5252', linewidths=1.0)
        nx.draw_networkx_edges(G, pos, ax=ax, edge_color='#64B5F6', width=weights, alpha=0.6)
        
        # 라벨링: 단어와 빈도수를 결합하여 명확히 표출
        font_props = {'family': plt.rcParams['font.family'], 'weight': 'bold'}
        for node, (x, y) in pos.items():
            label_text = f"{node}\n({node_freqs[node]})"
            ax.text(x, y, label_text, fontsize=8, color='#1A237E', 
                    ha='center', va='center', fontdict=font_props)
            
        ax.set_title("Co-occurrence Network Graph", fontdict=font_props)
        ax.axis('off')

    @staticmethod
    def draw_mds(coords, labels, ax):
        ax.scatter(coords[:, 0], coords[:, 1], c='#E8EAF6', s=80, edgecolors='#FF5252', linewidths=0.5, alpha=0.8)
        font_props = {'family': plt.rcParams['font.family']}
        for i, label in enumerate(labels):
            ax.text(coords[i, 0], coords[i, 1], str(label), fontsize=9, fontdict=font_props)
        ax.grid(True, linestyle='--', alpha=0.3)
        ax.set_title("MDS Mapping", fontdict=font_props)

    @staticmethod
    def draw_dendrogram(matrix, n_words, ax):
        top_matrix = matrix.iloc[:n_words, :n_words]
        linked = linkage(top_matrix, method='ward')
        dendrogram(linked, labels=[str(l) for l in top_matrix.index.tolist()], ax=ax, leaf_rotation=90)
        ax.set_title(f"Hierarchical Clustering Dendrogram (Top {n_words})", fontdict={'family': plt.rcParams['font.family']})

    @staticmethod
    def draw_heatmap(matrix, ax):
        corr = matrix.corr()
        sns.heatmap(corr, ax=ax, cmap='Blues', annot=False, cbar=True)
        ax.set_title("Word Similarity Heatmap", fontdict={'family': plt.rcParams['font.family']})