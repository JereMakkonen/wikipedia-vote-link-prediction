import networkx as nx
import math
import random


def filter_nodes(G, k, m=20):
    """
    Filters nodes that can not possibly be in a k-plex of size m.
    """
    # 1. K-core filtering: Remove nodes that are not >= (m - k)-core
    H = nx.k_core(G, k=m-k)
    
    # 2. Cliqueness filtering: Keep only nodes that belong to a clique of size >= ceiling(m/k)
    cliqueness = {u: 0 for u in H.nodes()}
    for clique in nx.find_cliques(H):
        for u in clique:
            cliqueness[u] = max(cliqueness[u], len(clique))
            
    valid_nodes = [u for u in H.nodes() if cliqueness[u] >= math.ceil(m / k)]
    return H.subgraph(valid_nodes)


def is_k_plex(G, nodes, k):
    """
    Check if node set forms a k-plex in G.
    """
    n = len(nodes)
    for v in nodes:
        deg = sum(1 for u in G.neighbors(v) if u in nodes)
        if deg < n - k:
            return False
    return True


def expand_k_plex(G, plex, k):
    """
    Greedy k-plex expansion statring from a set of nodes.
    """
    S = list(G.nodes() - plex)
    random.shuffle(S)

    while S:
        # score nodes in S: score(v) = deg_in_plex(v)
        scores = {v: sum(1 for u in G.neighbors(v) if u in plex) for v in S}

        # best candidate
        v = max(scores, key=scores.get)
        if is_k_plex(G, plex | {v}, k):
            plex.add(v)

        S.remove(v)

    return plex


if __name__ == "__main__":
    
    G = nx.read_edgelist("Wiki-Vote.txt", comments="#", nodetype=int)
    
    # First we filter nodes that can not be in the k-plex. (Here we are looking for 3-plexes with sizes >= 20)
    # However, this does not guarantee that a k-plex with size m exists
    H = filter_nodes(G, 3, 20)
    
    # Generate good seeds for k-plex. Here we just select 10 random large cliques
    max_clique = max(list(nx.find_cliques(H)), key=len)
    cliques = [c for c in list(nx.find_cliques(H)) if len(c) >= len(max_clique) - 1]
    seeds = random.sample(cliques, 10)
 
    # Expand seeds and try to find the largest k-plex
    for seed in seeds:
        plex = expand_k_plex(H, set(seed), 3)
        print(len(plex), plex)
