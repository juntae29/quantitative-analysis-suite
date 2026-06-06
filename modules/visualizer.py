import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import platform, os
import networkx as nx
import seaborn as sns
from scipy.cluster.hierarchy import dendrogram, linkage

def set_korean_font():
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
        ax.clear()
        top_matrix = matrix.iloc[:n_words, :n_words]
        G = nx.from_pandas_adjacency(top_matrix)
        pos = nx.spring_layout(G, k=1.2, seed=42)
        node_freqs = {node: int(matrix.loc[node, node]) for node in G.nodes()}
        
        # 1. 엣지 그리기
        edges = G.edges(data=True)
        weights = [min(data['weight'] * 0.2, 5.0) for u, v, data in edges]
        nx.draw_networkx_edges(G, pos, ax=ax, edge_color='#EF9A9A', width=weights, alpha=0.3)
        
        # 2. 노드 그리기 (연한 붉은 색상 적용)
        nx.draw_networkx_nodes(
            G, pos, ax=ax, 
            node_size=800, 
            node_color='#FFEBEE',    # 연한 붉은색 내부
            edgecolors='#EF9A9A',    # 연한 붉은색 테두리
            linewidths=2
        )
        
        # 3. 텍스트 라벨 출력
        for node, (x, y) in pos.items():
            ax.text(x, y, f"{node}\n({node_freqs[node]})", fontsize=8, 
                    ha='center', va='center', fontweight='bold', color='#B71C1C')
        
        ax.set_title("Co-occurrence Network Graph", fontsize=10, fontweight='bold')
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-1.2, 1.2)
        ax.axis('off')

    @staticmethod
    def draw_mds(coords, labels, ax):
        ax.clear()
        ax.scatter(coords[:, 0], coords[:, 1], c='#FFEBEE', s=80, edgecolors='#EF9A9A', alpha=0.8)
        for i, label in enumerate(labels):
            ax.text(coords[i, 0], coords[i, 1], str(label), fontsize=9)
        ax.grid(True, linestyle='--', alpha=0.3)
        ax.set_title("MDS Mapping")

    @staticmethod
    def draw_dendrogram(matrix, n_words, ax):
        ax.clear()
        top_matrix = matrix.iloc[:n_words, :n_words]
        linked = linkage(top_matrix, method='ward')
        dendrogram(linked, labels=[str(l) for l in top_matrix.index.tolist()], ax=ax, leaf_rotation=90)
        ax.set_title(f"Hierarchical Clustering Dendrogram (Top {n_words})")

    @staticmethod
    def draw_heatmap(matrix, ax):
        ax.clear()
        corr = matrix.corr()
        # 붉은색 계열 히트맵
        sns.heatmap(corr, ax=ax, cmap='Reds', annot=False, cbar=True)
        ax.set_title("Word Similarity Heatmap")