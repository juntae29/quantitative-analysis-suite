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
        
        # [핵심] 로그 스케일 적용하여 노드 크기 폭발 방지 및 시각적 균형 유지
        node_sizes = [max(math.log(node_freqs[n] + 1) * 800, 500) for n in G.nodes()]
        
        edges = G.edges(data=True)
        weights = [min(data['weight'] * 0.5, 5.0) for u, v, data in edges]
        
        # [핵심] k값을 조절하여 노드 간 척력 강화 (뭉침 방지)
        pos = nx.spring_layout(G, k=0.8, seed=42)
        
        # [핵심] 파란색 배경 제거: node_color='none' 설정, 빨간 테두리만 유지
        nx.draw_networkx_nodes(G, pos, ax=ax, node_size=node_sizes, 
                               node_color='none', edgecolors='#FF5252', linewidths=1.5)
        
        nx.draw_networkx_edges(G, pos, ax=ax, edge_color='#64B5F6', width=weights, alpha=0.4)
        
        # 텍스트 라벨링
        font_props = {'family': plt.rcParams['font.family'], 'weight': 'bold'}
        for node, (x, y) in pos.items():
            label_text = f"{node}\n({node_freqs[node]})"
            ax.text(x, y, label_text, fontsize=9, color='#1A237E', 
                    ha='center', va='center', fontdict=font_props)
            
        ax.set_title("Co-occurrence Network Graph", fontdict=font_props)
        ax.axis('off')

    # ... (기타 함수들 draw_mds, draw_dendrogram, draw_heatmap 유지)