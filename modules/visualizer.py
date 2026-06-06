import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import platform, os
import networkx as nx
import math
from scipy.cluster.hierarchy import dendrogram, linkage
import seaborn as sns

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
        top_matrix = matrix.iloc[:n_words, :n_words]
        G = nx.from_pandas_adjacency(top_matrix)
        
        node_freqs = {node: int(matrix.loc[node, node]) for node in G.nodes()}
        
        # 로그 스케일링으로 노드 크기 폭발 방지
        node_sizes = [max(math.log(node_freqs[n] + 1) * 800, 500) for n in G.nodes()]
        
        edges = G.edges(data=True)
        weights = [min(data['weight'] * 0.5, 5.0) for u, v, data in edges]
        
        # k값을 조절하여 노드 분산 유도
        pos = nx.spring_layout(G, k=0.8, seed=42)
        
        # [중요] node_color='none'은 노드 내부를 투명하게 만듦
        # 만약 여전히 파란색이 보인다면, 이전 그래프가 캐시된 것이니 반드시 '강력 새로고침' 필요
        nx.draw_networkx_nodes(G, pos, ax=ax, node_size=node_sizes, 
                               node_color='none', edgecolors='#FF5252', linewidths=1.5)
        
        nx.draw_networkx_edges(G, pos, ax=ax, edge_color='#64B5F6', width=weights, alpha=0.4)
        
        font_props = {'family': plt.rcParams['font.family'], 'weight': 'bold'}
        for node, (x, y) in pos.items():
            label_text = f"{node}\n({node_freqs[node]})"
            ax.text(x, y, label_text, fontsize=9, color='#1A237E', 
                    ha='center', va='center', fontdict=font_props)
            
        ax.set_title("Co-occurrence Network Graph", fontdict=font_props)
        ax.axis('off')

    # MDS, Dendrogram, Heatmap 관련 메서드들은 이전과 동일하게 유지
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