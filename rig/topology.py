"""
Topology analysis on the DR100 RIG (v1.0).

Computes:
  - degree / weighted degree centrality
  - betweenness centrality (bridges)
  - community detection (Louvain modularity) on undirected projection
  - connected component analysis
  - per-cluster characterization

Output: main/rig_outputs/rig_topology.md
"""

import pickle
import json
from pathlib import Path
from collections import Counter, defaultdict

import networkx as nx

ROOT = Path.home() / "Desktop/DrugResource100/main/rig_outputs"
GPICKLE = ROOT / "rig_networkx.gpickle"
OUT = ROOT / "rig_topology.md"

with open(GPICKLE, "rb") as f:
    G = pickle.load(f)

# Undirected projection for community detection (treat edges as bi-directional links)
UG = nx.Graph()
for n, d in G.nodes(data=True):
    UG.add_node(n, **d)
for u, v, k, d in G.edges(keys=True, data=True):
    if UG.has_edge(u, v):
        UG[u][v]["weight"] = UG[u][v].get("weight", 0) + 1
    else:
        UG.add_edge(u, v, weight=1, edge_type=d["edge_type"])

# Drop isolated nodes for component analysis
nz_nodes = [n for n in UG.nodes() if UG.degree(n) > 0]
H = UG.subgraph(nz_nodes).copy()

# Connected components
comps = sorted(nx.connected_components(H), key=len, reverse=True)
giant = H.subgraph(comps[0]).copy()

# Centrality on giant component
deg_cent = nx.degree_centrality(giant)
bet_cent = nx.betweenness_centrality(giant, weight="weight")
eig_cent = nx.eigenvector_centrality(giant, weight="weight", max_iter=500)

# Community detection - greedy modularity (no extra deps needed)
from networkx.algorithms.community import greedy_modularity_communities
communities = list(greedy_modularity_communities(giant, weight="weight"))
mod_score = nx.algorithms.community.modularity(giant, communities, weight="weight")

# Per-cluster summary: dominant category + theme
def cluster_theme(nodes):
    cats = Counter(G.nodes[n].get("category", "?") for n in nodes)
    # Look at outgoing edge_types from members
    return dict(cats)

# ---- WRITE REPORT ----
with open(OUT, "w") as f:
    f.write("# DR100 RIG Topology Analysis (v1.0)\n\n")
    f.write(f"**Graph**: directed multigraph, **{G.number_of_nodes()}** nodes, **{G.number_of_edges()}** edges\n")
    f.write(f"**Undirected projection** (for community detection): {UG.number_of_nodes()} nodes, {UG.number_of_edges()} unique edges\n")
    f.write(f"**Nodes with ≥1 connection**: {len(nz_nodes)} ({len(nz_nodes)/G.number_of_nodes()*100:.0f}%)\n")
    f.write(f"**Connected components**: {len(comps)}; giant component covers **{len(comps[0])}** nodes ({len(comps[0])/G.number_of_nodes()*100:.0f}% of all DR100 resources)\n\n")

    f.write("## Connectivity by component (Top 8)\n\n")
    f.write("| Component | Size | Sample members |\n|---|---|---|\n")
    for i, c in enumerate(comps[:8], 1):
        sample = sorted(c)[:6]
        f.write(f"| {i} | {len(c)} | {', '.join(sample)} |\n")
    f.write("\n")

    f.write("## Top 15 by betweenness centrality (bridge resources)\n\n")
    f.write("Betweenness = fraction of shortest paths in the giant component that pass through this node.\n")
    f.write("High-betweenness nodes are **structural bridges** — agents whose query crosses many resource boundaries must route through them.\n\n")
    f.write("| Rank | Resource | Betweenness | Category |\n|---|---|---|---|\n")
    for i, (n, c) in enumerate(sorted(bet_cent.items(), key=lambda x: -x[1])[:15], 1):
        f.write(f"| {i} | {n} | {c:.3f} | {G.nodes[n].get('category')} |\n")
    f.write("\n")

    f.write("## Top 15 by eigenvector centrality (importance hubs)\n\n")
    f.write("Eigenvector centrality favors nodes connected to other well-connected nodes — the 'central elite' of the registry.\n\n")
    f.write("| Rank | Resource | Eigenvector | Category |\n|---|---|---|---|\n")
    for i, (n, c) in enumerate(sorted(eig_cent.items(), key=lambda x: -x[1])[:15], 1):
        f.write(f"| {i} | {n} | {c:.3f} | {G.nodes[n].get('category')} |\n")
    f.write("\n")

    f.write(f"## Community structure (greedy modularity, Q = {mod_score:.3f})\n\n")
    f.write(f"Detected **{len(communities)}** communities in the giant component.\n\n")
    for i, c in enumerate(sorted(communities, key=len, reverse=True), 1):
        cats = cluster_theme(c)
        f.write(f"### Cluster {i}: {len(c)} resources | category mix: {cats}\n\n")
        # Order members within cluster by their internal degree
        internal = sorted(c, key=lambda n: -giant.degree(n))
        for n in internal[:20]:
            f.write(f"- {n} (deg {giant.degree(n)})\n")
        if len(c) > 20:
            f.write(f"- ... ({len(c)-20} more)\n")
        f.write("\n")

print(f"Wrote: {OUT}")
print(f"Modularity Q: {mod_score:.3f}")
print(f"Giant component covers {len(comps[0])}/{G.number_of_nodes()} ({len(comps[0])/G.number_of_nodes()*100:.0f}%) resources")
print(f"Detected {len(communities)} communities")
