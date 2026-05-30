import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import platform
import os
import networkx as nx
import seaborn as sns
from scipy.cluster.hierarchy import dendrogram, linkage

# 폰트 설정을 위한 로직을 별도 함수로 분리하여 가장 먼저 실행
def set_korean_font():
    font_path = os.path.join(os.path.dirname(__file__), '..', 'fonts', 'malgun.ttf')
    
    # 폰트 매니저가 폰트 파일을 확실히 인식하도록 등록
    if os.path.exists(font_path):
        fm.fontManager.addfont(font_path)
        plt.rcParams['font.family'] = 'Malgun Gothic'
    else:
        # 폰트 파일이 없을 경우 시스템 환경에 따른 대체 폰트 설정
        if platform.system() == "Windows":
            plt.rcParams['font.family'] = 'Malgun Gothic'
        elif platform.system() == "Darwin":
            plt.rcParams['font.family'] = 'AppleGothic'
        else:
            plt.rcParams['font.family'] = 'sans-serif'
            
    # 마이너스 기호 깨짐 방지
    plt.rcParams['axes.unicode_minus'] = False

# 모듈 로드 시 즉시 실행
set_korean_font()

class Visualizer:
    @staticmethod
    def draw_network(matrix, n_words, ax):
        top_matrix = matrix.iloc[:n_words, :n_words]
        G = nx.from_pandas_adjacency(top_matrix)
        node_freqs = {node: int(matrix.loc[node, node]) for node in G.nodes()}
        node_sizes = [max(node_freqs[n] * 20, 1000) for n in G.nodes()]
        weights = [G[u][v]['weight'] * 0.1 for u, v in G.edges()]
        pos = nx.spring_layout(G, k=0.8, seed=42)
        nx.draw_networkx_nodes(G, pos, ax=ax, node_size=node_sizes, 
                               node_color='#E8EAF6', edgecolors='#FF5252', linewidths=0.5)
        nx.draw_networkx_edges(G, pos, ax=ax, edge_color='#64B5F6', width=weights, alpha=0.5)
        
        # 텍스트 렌더링 시 강제 폰트 설정 유지
        font_props = {'family': plt.rcParams['font.family']}
        for node, (x, y) in pos.items():
            ax.text(x, y, str(node_freqs[node]), fontsize=9, color='#1A237E', 
                    ha='center', va='center', fontweight='bold', fontdict=font_props)
        for node, (x, y) in pos.items():
            ax.text(x, y + 0.08, str(node), fontsize=9, color='black', 
                    ha='center', va='bottom', fontweight='bold', fontdict=font_props)
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