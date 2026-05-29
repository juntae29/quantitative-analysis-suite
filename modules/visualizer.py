import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import platform
import networkx as nx
import seaborn as sns
from scipy.cluster.hierarchy import dendrogram, linkage

# 운영체제에 따른 폰트 자동 설정
system_name = platform.system()
if system_name == "Windows":
    font_path = "C:/Windows/Fonts/malgun.ttf"
elif system_name == "Darwin": # Mac
    font_path = "/Library/Fonts/AppleGothic.ttf"
else: # Linux (Streamlit Cloud 환경)
    font_path = None

if font_path and fm.findfont(fm.FontProperties(fname=font_path), rebuild_if_missing=False) != fm.findfont(fm.FontProperties(family='sans-serif')):
    try:
        font_name = fm.FontProperties(fname=font_path).get_name()
        plt.rc('font', family=font_name)
    except:
        plt.rc('font', family='sans-serif')
else:
    plt.rc('font', family='sans-serif')

plt.rcParams['axes.unicode_minus'] = False

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
        for node, (x, y) in pos.items():
            ax.text(x, y, str(node_freqs[node]), fontsize=9, color='#1A237E', 
                    ha='center', va='center', fontweight='bold')
        for node, (x, y) in pos.items():
            ax.text(x, y + 0.08, node, fontsize=9, color='black', 
                    ha='center', va='bottom', fontweight='bold')
        ax.set_title("Co-occurrence Network Graph")
        ax.axis('off')

    @staticmethod
    def draw_mds(coords, labels, ax):
        ax.scatter(coords[:, 0], coords[:, 1], c='#E8EAF6', s=80, edgecolors='#FF5252', linewidths=0.5, alpha=0.8)
        for i, label in enumerate(labels):
            ax.text(coords[i, 0], coords[i, 1], label, fontsize=9)
        ax.grid(True, linestyle='--', alpha=0.3)
        ax.set_title("MDS Mapping")

    @staticmethod
    def draw_dendrogram(matrix, n_words, ax):
        top_matrix = matrix.iloc[:n_words, :n_words]
        linked = linkage(top_matrix, method='ward')
        dendrogram(linked, labels=top_matrix.index.tolist(), ax=ax, leaf_rotation=90)
        ax.set_title(f"Hierarchical Clustering Dendrogram (Top {n_words})")

    @staticmethod
    def draw_heatmap(matrix, ax):
        corr = matrix.corr()
        sns.heatmap(corr, ax=ax, cmap='Blues', annot=False, cbar=True)
        ax.set_title("Word Similarity Heatmap")