"""
Generate the RIG overview in two formats from the repository's data files:

  (a) static PDF + PNG via matplotlib + NetworkX
      Output: figures/figure_8_rig.pdf + .png
  (b) interactive standalone HTML (plotly.js from the CDN; no Python plotly package needed)
      Output: figures/rig_interactive.html
      Hover for resource details; pan/zoom; click the legend to toggle relationship types.

This is an overview of the same graph that the Review analyses; the Review's Figure 5 is published
with the article. Definitions follow the Review and rig/topology.py: undirected projection with
relationship multiplicity as pair weight, communities by greedy modularity (resolution 1) numbered
1-11 as in rig/topology.md, degree = distinct neighbors, normalized betweenness on unweighted paths.

Layout: positions are read from figures/rig_layout.json (spring layout, seed 42) so that the figure
is reproducible across NetworkX versions; if the file is missing it is computed and written.
Node size encodes distinct neighbors, node color the community, edge color the relationship type.
The 12 resources with the highest betweenness are labeled.

Run from the repository root:  python rig/make_figure.py
"""

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

import networkx as nx
from networkx.algorithms.community import greedy_modularity_communities, modularity
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

CATS = ("drug_centric", "drug_related", "auxiliary")
records = [r for c in CATS for r in json.loads((ROOT / "registry" / f"{c}.json").read_text(encoding="utf-8"))]
names = [r["name"] for r in records]
CAT_LABEL = {"Drug-centric": "Drug-centric", "Drug-related (indirect)": "Drug-related", "auxiliary": "Auxiliary"}
cat_of = {r["name"]: CAT_LABEL[r["category"]] for r in records}

with open(ROOT / "rig" / "edges.csv", newline="", encoding="utf-8") as fh:
    edges = list(csv.DictReader(fh))
tier = {}
with open(ROOT / "rig" / "rig_edges_v1.csv", newline="", encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        tier[(r["source"], r["edge_type"], r["target"])] = r["provenance_tier"]

# ---- Directed multigraph and its undirected projection (as in rig/topology.py)
G = nx.MultiDiGraph()
G.add_nodes_from(names)
for r in edges:
    G.add_edge(r["source"], r["target"], edge_type=r["edge_type"])
UG = nx.Graph()
UG.add_nodes_from(names)
for r in edges:
    u, v = r["source"], r["target"]
    if UG.has_edge(u, v):
        UG[u][v]["weight"] += 1
    else:
        UG.add_edge(u, v, weight=1)

comms = list(greedy_modularity_communities(UG, weight="weight", resolution=1))
q = modularity(UG, comms, weight="weight", resolution=1)
node_to_comm = {n: i + 1 for i, c in enumerate(comms) for n in c}          # 1-11, as in rig/topology.md
bet = nx.betweenness_centrality(UG, normalized=True, weight=None)
deg = dict(UG.degree())                                                   # distinct neighbors
n_tier1 = sum(1 for k in tier.values() if k == "1")
assert (UG.number_of_nodes(), G.number_of_edges(), UG.number_of_edges()) == (177, 440, 392)
assert nx.number_connected_components(UG) == 1 and len(comms) == 11

top_label = sorted(bet.items(), key=lambda x: -x[1])[:12]
label_set = {n for n, _ in top_label}

# ---- Layout
layout_file = OUT_DIR / "rig_layout.json"
if layout_file.exists():
    pos = {n: tuple(xy) for n, xy in json.loads(layout_file.read_text()).items()}
else:
    pos = nx.spring_layout(UG, seed=42, k=0.55, iterations=200, weight="weight")
    layout_file.write_text(json.dumps({n: [round(float(x), 6), round(float(y), 6)] for n, (x, y) in pos.items()}, indent=0))

edge_counts = Counter(r["edge_type"] for r in edges)
TYPE_ORDER = ["incorporates", "complements", "bridges", "derived_from", "feeds_pipeline", "mirrors"]
TYPE_LABEL = {"incorporates": "Incorporates", "complements": "Complements", "bridges": "Bridges",
              "derived_from": "Derived from", "feeds_pipeline": "Feeds pipeline", "mirrors": "Mirrors"}
SUBTITLE = (f"177 resources · 440 relationships · 392 resource pairs · one connected component when direction is ignored"
            f" · Q = {q:.3f} · 11 communities")

# ============================================================================
# (a) MATPLOTLIB STATIC PDF + PNG
# ============================================================================

EDGE_COLORS = {
    "incorporates":    "#E66100",  # orange
    "derived_from":    "#D81B60",  # red/magenta
    "mirrors":         "#999999",  # grey
    "bridges":         "#1E88E5",  # blue
    "complements":     "#43A047",  # green
    "feeds_pipeline":  "#8E44AD",  # purple
}

# 11 community colors (ColorBrewer Set3-ish, distinguishable)
COMM_COLORS = [
    "#8DD3C7", "#FFD92F", "#BEBADA", "#FB8072", "#80B1D3",
    "#FDB462", "#B3DE69", "#FCCDE5", "#BC80BD", "#CCEBC5",
    "#FFED6F", "#A6CEE3", "#1F78B4", "#33A02C", "#FB9A99",
]

fig, ax = plt.subplots(figsize=(20, 16))

# Edges - draw by type, semi-transparent
seen = set()
for r in edges:
    u, v, et = r["source"], r["target"], r["edge_type"]
    if (u, v, et) in seen or (v, u, et) in seen:
        continue
    seen.add((u, v, et))
    ax.annotate(
        "", xy=pos[v], xytext=pos[u],
        arrowprops=dict(arrowstyle="-", color=EDGE_COLORS.get(et, "#bbbbbb"), alpha=0.32, lw=0.7),
        zorder=1,
    )

# Nodes
node_sizes = [80 + 30 * deg[n] for n in UG.nodes()]
node_colors = [COMM_COLORS[(node_to_comm[n] - 1) % len(COMM_COLORS)] for n in UG.nodes()]
nx.draw_networkx_nodes(
    UG, pos, ax=ax,
    node_size=node_sizes,
    node_color=node_colors,
    edgecolors="black",
    linewidths=0.6,
    alpha=0.95,
)

SHORT = {
    "PubMed Central Open Access Subset": "PMC OA",
    "UMLS (Unified Medical Language System)": "UMLS",
    "TDC (Therapeutics Data Commons)": "TDC",
}
LABEL_OFFSET = {"ROBOKOP": (0.0, -0.05)}          # keeps the ROBOKOP label clear of DRKG
for n in label_set:
    x, y = pos[n]
    dx, dy = LABEL_OFFSET.get(n, (0.0, 0.0))
    ax.text(x + dx, y + 0.025 + dy, SHORT.get(n, n), fontsize=9, ha="center",
            fontweight="bold", color="black",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                      edgecolor="black", alpha=0.85))

# Relationship-type legend, in the Review's order
edge_legend = [Line2D([0], [0], color=EDGE_COLORS[t], lw=2.5, label=f"{TYPE_LABEL[t]} ({edge_counts[t]})")
               for t in TYPE_ORDER]
ax.legend(handles=edge_legend, loc="lower left", fontsize=11,
          title="Relationship type", title_fontsize=12, frameon=True, framealpha=0.92)

ax.set_title(
    "Resource Interconnection Graph (RIG)\n" + SUBTITLE + "\n"
    "Node color: community (1–11). Node size: distinct neighbors. Labels: 12 highest betweenness values.",
    fontsize=15, fontweight="bold", pad=18,
)

# Cosmetics
ax.set_xticks([]); ax.set_yticks([])
for spine in ax.spines.values():
    spine.set_visible(False)
ax.margins(0.07)

plt.tight_layout()
pdf_path = OUT_DIR / "figure_8_rig.pdf"
png_path = OUT_DIR / "figure_8_rig.png"
plt.savefig(pdf_path, dpi=300, bbox_inches="tight")
plt.savefig(png_path, dpi=200, bbox_inches="tight")
plt.close(fig)
print(f"Wrote: {pdf_path}")
print(f"Wrote: {png_path}")

# ============================================================================
# (b) INTERACTIVE HTML (plotly.js 2.12.1 from the CDN)
# ============================================================================

EDGE_COLORS_RGB = {
    "incorporates":    "rgba(230, 97, 0, 0.4)",
    "derived_from":    "rgba(216, 27, 96, 0.4)",
    "mirrors":         "rgba(120, 120, 120, 0.4)",
    "bridges":         "rgba(30, 136, 229, 0.4)",
    "complements":     "rgba(67, 160, 71, 0.4)",
    "feeds_pipeline":  "rgba(142, 68, 173, 0.4)",
}

edges_by_type = defaultdict(list)
for r in edges:
    edges_by_type[r["edge_type"]].append((r["source"], r["target"]))
traces = []
for et in TYPE_ORDER:
    xs, ys = [], []
    for u, v in edges_by_type[et]:
        (x0, y0), (x1, y1) = pos[u], pos[v]
        xs += [x0, x1, None]
        ys += [y0, y1, None]
    traces.append(dict(type="scatter", x=xs, y=ys, mode="lines",
                       line=dict(width=0.8, color=EDGE_COLORS_RGB[et]),
                       name=f"{TYPE_LABEL[et]} ({len(edges_by_type[et])})", hoverinfo="skip", showlegend=True))


def listed(ns):
    ns = sorted(set(ns))
    return ", ".join(ns[:8]) + (" ..." if len(ns) > 8 else "")


node = dict(x=[], y=[], size=[], color=[], text=[], hover=[])
for n in UG.nodes():
    x, y = pos[n]
    out_n = [v for _, v in G.out_edges(n)]
    in_n = [u for u, _ in G.in_edges(n)]
    node["x"].append(x); node["y"].append(y)
    node["size"].append(8 + 2.0 * deg[n])
    node["color"].append(COMM_COLORS[(node_to_comm[n] - 1) % len(COMM_COLORS)])
    node["text"].append(SHORT.get(n, n) if n in label_set else "")
    node["hover"].append(
        f"<b>{n}</b><br>primary category: {cat_of[n]}<br>community: {node_to_comm[n]}<br>"
        f"distinct neighbors: {deg[n]}<br>betweenness (unweighted paths): {bet[n]:.3f}<br>"
        f"outgoing relationships ({len(out_n)}): {listed(out_n)}<br>"
        f"incoming relationships ({len(in_n)}): {listed(in_n)}")
traces.append(dict(type="scatter", x=node["x"], y=node["y"], mode="markers+text",
                   marker=dict(size=node["size"], color=node["color"], line=dict(color="black", width=0.6), opacity=0.92),
                   text=node["text"], textposition="top center",
                   textfont=dict(size=9, color="black", family="Helvetica"),
                   hovertext=node["hover"], hoverinfo="text", name="Resources (177)", showlegend=False))
layout = dict(
    title=dict(text="<b>Resource Interconnection Graph (RIG)</b><br>"
                    f"<span style='font-size:14px'>{SUBTITLE}</span><br>"
                    "<span style='font-size:11px;color:#555'>Hover for resource details · click the legend to toggle "
                    "relationship types · node color: community · node size: distinct neighbors</span>",
               x=0.02, xanchor="left"),
    showlegend=True,
    legend=dict(title=dict(text="Relationship type"), x=0.02, y=0.02,
                bgcolor="rgba(255,255,255,0.85)", bordercolor="black", borderwidth=1),
    hovermode="closest", xaxis=dict(visible=False), yaxis=dict(visible=False),
    plot_bgcolor="white", width=1500, height=1000, margin=dict(l=20, r=20, t=110, b=20),
)
html_path = OUT_DIR / "rig_interactive.html"
html_path.write_text(
    "<html>\n<head><meta charset=\"utf-8\" /><title>Resource Interconnection Graph (RIG)</title></head>\n<body>\n"
    "<script src=\"https://cdn.plot.ly/plotly-2.12.1.min.js\"></script>\n"
    "<div id=\"rig\" style=\"height:1000px; width:1500px;\"></div>\n<script>\n"
    f"Plotly.newPlot(\"rig\", {json.dumps(traces)}, {json.dumps(layout)}, {{\"responsive\": true}});\n"
    "</script>\n</body>\n</html>\n", encoding="utf-8")
print(f"Wrote: {html_path}")
print(f"communities {len(comms)}, Q = {q:.7f}, Tier 1 = {n_tier1}, labeled: {sorted(SHORT.get(n, n) for n in label_set)}")
