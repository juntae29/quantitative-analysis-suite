import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import platform, os
import networkx as nx
import math
import seaborn as sns
from scipy.cluster.hierarchy import dendrogram, linkage

def set_korean_font():
    # 폰트 경로는 사용자 환경에 맞게 유지
    font_path = os.path.join(os.path.dirname(__file__), '..', 'fonts', 'malgun.ttf')
    if os.path.exists(font_path):
        fm.fontManager.addfont(font_path)
        plt.rcParams['font.family'] = 'Malgun Gothic'
    else:
        plt.rcParams['font.family'] = 'Malgun Gothic' if platform.system() == "Windows" else 'AppleGothic'
    plt.rcParams['axes.unicode_minus'] = False

set_korean_font()

class Visualizer:
    @staticmethod
    def draw_network(matrix, n_words, ax):
        top_matrix = matrix.iloc[:n_words, :n_words]
        G = nx.from_pandas_adjacency(top_matrix)
        
        # 뭉침 방지를 위해 k값을 1.5로 상향 조정
        pos = nx.spring_layout(G, k=1.5, seed=42)
        node_freqs = {node: int(matrix.loc[node, node]) for node in G.nodes()}
        
        # 1. 엣지 먼저 그리기 (배경 레이어)
        edges = G.edges(data=True)
        weights = [min(data['weight'] * 0.2, 5.0) for u, v, data in edges]
        nx.draw_networkx_edges(G, pos, ax=ax, edge_color='#64B5F6', width=weights, alpha=0.3)
        
        # 2. [핵심] nx.draw_networkx_nodes를 호출하지 않고, plt.Circle을 수동으로 그림
        # 이를 통해 파란색 배경 원이 생성될 여지를 원천 차단함
        for node, (x, y) in pos.items():
            # 노드 크기 계산 (로그 스케일)
            radius = math.log(node_freqs[node] + 2) * 0.02
            
            # 빨간 테두리 원만 생성
            circle = plt.Circle((x, y), radius=radius, color='#FF5252', fill=False, linewidth=1.5)
            ax.add_artist(circle)
            
            # 텍스트 라벨링
            label_text = f"{node}\n({node_freqs[node]})"
            ax.text(x, y, label_text, fontsize=8, ha='center', va='center', 
                    fontweight='bold', color='#1A237E')
        
        ax.set_title("Co-occurrence Network Graph", fontsize=10, fontweight='bold')
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-1.2, 1.2)
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