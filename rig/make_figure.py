"""
Generate the RIG visualization in two formats:

  (a) High-quality static PDF + PNG via matplotlib + NetworkX
      Output: main/figures/figure_8_rig.pdf  +  .png

  (b) Interactive standalone HTML (Plotly) for GitHub Pages
      Output: main/figures/rig_interactive.html
      Hover for node info + edge type; pan/zoom; community color-coded

Layout: spring_layout with seed=42 for reproducibility.
Node size encodes total degree (multigraph). Node color encodes
greedy-modularity community. Edges colored by type. Top-12 hubs labeled.
"""

import pickle
import json
from pathlib import Path
from collections import Counter, defaultdict

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D

ROOT = Path.home() / "Desktop" / "DrugResource100" / "main"
GPK = ROOT / "rig_outputs/rig_networkx.gpickle"
OUT_DIR = ROOT / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

with open(GPK, "rb") as f:
    G = pickle.load(f)

with open(ROOT / "rig_outputs/resource_names.json") as f:
    NAMES = json.load(f)
cat_of = {n["name"]: cat for cat, items in NAMES.items() for n in items}

# ---- Undirected projection for layout + community
UG = nx.Graph()
for n, d in G.nodes(data=True):
    UG.add_node(n, **d)
for u, v, k, d in G.edges(keys=True, data=True):
    if UG.has_edge(u, v):
        UG[u][v]["weight"] = UG[u][v].get("weight", 0) + 1
    else:
        UG.add_edge(u, v, weight=1, edge_type=d.get("edge_type", "?"))

# Communities via greedy modularity
from networkx.algorithms.community import greedy_modularity_communities
comms = list(greedy_modularity_communities(UG, weight="weight"))
node_to_comm = {n: i for i, c in enumerate(comms) for n in c}

# Centralities
bet = nx.betweenness_centrality(UG, weight="weight")
deg = {n: G.in_degree(n) + G.out_degree(n) for n in G.nodes()}

# Top-12 hubs by betweenness for labels
top_label = sorted(bet.items(), key=lambda x: -x[1])[:12]
label_set = {n for n, _ in top_label}

# Layout (cache to figures/_layout.pkl for reproducibility)
layout_cache = OUT_DIR / "_layout.pkl"
if layout_cache.exists():
    with open(layout_cache, "rb") as f:
        pos = pickle.load(f)
else:
    pos = nx.spring_layout(UG, seed=42, k=0.55, iterations=200, weight="weight")
    with open(layout_cache, "wb") as f:
        pickle.dump(pos, f)

# Edge counts by type for dynamic legend
edge_counts = Counter(d.get("edge_type", "?") for _, _, _, d in G.edges(keys=True, data=True))

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
for u, v, k, d in G.edges(keys=True, data=True):
    et = d.get("edge_type", "?")
    color = EDGE_COLORS.get(et, "#bbbbbb")
    if (u, v, et) in seen or (v, u, et) in seen:
        continue
    seen.add((u, v, et))
    ax.annotate(
        "", xy=pos[v], xytext=pos[u],
        arrowprops=dict(arrowstyle="-", color=color, alpha=0.32, lw=0.7),
        zorder=1,
    )

# Nodes
node_sizes = [80 + 30 * deg[n] for n in UG.nodes()]
node_colors = [COMM_COLORS[node_to_comm[n] % len(COMM_COLORS)] for n in UG.nodes()]
nx.draw_networkx_nodes(
    UG, pos, ax=ax,
    node_size=node_sizes,
    node_color=node_colors,
    edgecolors="black",
    linewidths=0.6,
    alpha=0.95,
)

# Top-15 hub labels with better positioning
label_dict = {n: n.replace(" (Unified Medical Language System)", "")
                   .replace(" (Therapeutics Data Commons)", "")
                   .replace(" Drug Pharmacological Actions", "")
                   .replace(" (Comparative Toxicogenomics DB)", "")
                   .replace(" (National Drug File)", "")
                   .replace(" (Cancer Cell Line Encyclopedia)", "")
                   .replace(" (Cancer Therapeutics Response Portal)", "")
                   .replace(" (Genomics-Drug Knowledge DB)", "")
                   .replace(" (Drug Target Commons) 2.0", "")
                   .replace(" Open Access Subset", " OA")
                   .replace(" (Multiscale Interactome)", "")
                   .replace(" (Online Mendelian Inheritance in Man)", "")
                   .replace(" (Human Metabolome Database)", "")
                   .replace(" (Genotype-Tissue Expression)", "")
                   .replace(" (The Cancer Genome Atlas)", "")
                   .replace(" (Human Phenotype Ontology)", "")
                   .replace(" (Clinical Knowledge Graph)", "")
                   .replace(" (Protein Data Bank)", "")
                   .replace(" (NCIt)", "")
                   .replace(" (PKG)", "")
                   .replace("/ClinPGx", "")
              for n in label_set}
for n, lbl in label_dict.items():
    x, y = pos[n]
    ax.text(x, y + 0.025, lbl, fontsize=9, ha="center",
            fontweight="bold", color="black",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                     edgecolor="black", alpha=0.85))

# Edge-type legend
edge_legend = [
    Line2D([0], [0], color=EDGE_COLORS["incorporates"],   lw=2.5, label=f"incorporates ({edge_counts['incorporates']})"),
    Line2D([0], [0], color=EDGE_COLORS["derived_from"],   lw=2.5, label=f"derived_from ({edge_counts['derived_from']})"),
    Line2D([0], [0], color=EDGE_COLORS["mirrors"],        lw=2.5, label=f"mirrors ({edge_counts['mirrors']})"),
    Line2D([0], [0], color=EDGE_COLORS["bridges"],        lw=2.5, label=f"bridges ({edge_counts['bridges']})"),
    Line2D([0], [0], color=EDGE_COLORS["complements"],    lw=2.5, label=f"complements ({edge_counts['complements']})"),
    Line2D([0], [0], color=EDGE_COLORS["feeds_pipeline"], lw=2.5, label=f"feeds_pipeline ({edge_counts['feeds_pipeline']})"),
]
ax.legend(handles=edge_legend, loc="lower left", fontsize=11,
          title="Edge type", title_fontsize=12, frameon=True, framealpha=0.92)

# Title + subtitle
ax.set_title(
    "DR100 Resource Interconnection Graph (RIG)\n"
    "177 resources · 440 typed edges · single fully-connected component · Q = 0.608 · 11 communities",
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
# (b) PLOTLY INTERACTIVE HTML (for GitHub Pages)
# ============================================================================
import plotly.graph_objects as go

EDGE_COLORS_RGB = {
    "incorporates":    "rgba(230, 97, 0, 0.4)",
    "derived_from":    "rgba(216, 27, 96, 0.4)",
    "mirrors":         "rgba(120, 120, 120, 0.4)",
    "bridges":         "rgba(30, 136, 229, 0.4)",
    "complements":     "rgba(67, 160, 71, 0.4)",
    "feeds_pipeline":  "rgba(142, 68, 173, 0.4)",
}

# Edges by type (one trace per type for legend interactivity)
edge_traces = []
edges_by_type = defaultdict(list)
for u, v, k, d in G.edges(keys=True, data=True):
    edges_by_type[d.get("edge_type", "?")].append((u, v, d))

for et, edges in edges_by_type.items():
    xs, ys, hovers = [], [], []
    for u, v, d in edges:
        x0, y0 = pos[u]; x1, y1 = pos[v]
        xs += [x0, x1, None]
        ys += [y0, y1, None]
    edge_traces.append(go.Scatter(
        x=xs, y=ys, mode="lines",
        line=dict(width=0.8, color=EDGE_COLORS_RGB.get(et, "#999")),
        name=f"{et} ({len(edges)})",
        hoverinfo="skip", showlegend=True,
    ))

# Nodes
node_x, node_y, node_text, node_size, node_color, node_label = [], [], [], [], [], []
for n in UG.nodes():
    x, y = pos[n]
    node_x.append(x); node_y.append(y)
    sz = 8 + 2.0 * deg[n]
    node_size.append(sz)
    cat = cat_of.get(n, "?")
    comm = node_to_comm[n]
    color = COMM_COLORS[comm % len(COMM_COLORS)]
    node_color.append(color)
    # Build hover text
    nbrs_out = [v for _, v, k in G.out_edges(n, keys=True)]
    nbrs_in  = [u for u, _, k in G.in_edges(n, keys=True)]
    hover = (
        f"<b>{n}</b><br>"
        f"category: {cat}<br>"
        f"community: {comm}<br>"
        f"in/out degree: {G.in_degree(n)}/{G.out_degree(n)}<br>"
        f"betweenness: {bet.get(n, 0):.3f}<br>"
        f"out-neighbors ({len(nbrs_out)}): {', '.join(sorted(set(nbrs_out))[:8])}{' ...' if len(set(nbrs_out)) > 8 else ''}<br>"
        f"in-neighbors ({len(nbrs_in)}): {', '.join(sorted(set(nbrs_in))[:8])}{' ...' if len(set(nbrs_in)) > 8 else ''}"
    )
    node_text.append(hover)
    node_label.append(n if n in label_set else "")

node_trace = go.Scatter(
    x=node_x, y=node_y, mode="markers+text",
    marker=dict(size=node_size, color=node_color,
                line=dict(color="black", width=0.6),
                opacity=0.92),
    text=node_label,
    textposition="top center",
    textfont=dict(size=9, color="black", family="Helvetica"),
    hovertext=node_text,
    hoverinfo="text",
    name="Resources (177)",
    showlegend=False,
)

fig_int = go.Figure(data=edge_traces + [node_trace])
fig_int.update_layout(
    title=dict(
        text="<b>DR100 Resource Interconnection Graph (RIG)</b><br>"
             "<span style='font-size:14px'>177 resources · 440 typed edges · single fully-connected component · Q = 0.608 · 11 communities</span><br>"
             "<span style='font-size:11px;color:#555'>Hover for resource details · click legend to toggle edge types</span>",
        x=0.02, xanchor="left",
    ),
    showlegend=True,
    legend=dict(title="Edge type", x=0.02, y=0.02,
                bgcolor="rgba(255,255,255,0.85)",
                bordercolor="black", borderwidth=1),
    hovermode="closest",
    xaxis=dict(visible=False),
    yaxis=dict(visible=False),
    plot_bgcolor="white",
    width=1500, height=1000,
    margin=dict(l=20, r=20, t=110, b=20),
)
html_path = OUT_DIR / "rig_interactive.html"
fig_int.write_html(str(html_path), include_plotlyjs="cdn", full_html=True)
print(f"Wrote: {html_path}")

# A stripped index.html for GitHub Pages that just iframes the figure
gh_pages = OUT_DIR / "index.html"
gh_pages.write_text(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>DR100 Resource Interconnection Graph</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 0; background: #fafafa; }}
  header {{ padding: 1.2em 2em; background: white; border-bottom: 1px solid #ddd; }}
  h1 {{ margin: 0 0 0.2em 0; font-size: 1.4em; color: #222; }}
  .sub {{ color: #666; font-size: 0.95em; }}
  .stats {{ color: #444; font-size: 0.9em; margin-top: 0.6em; }}
  iframe {{ width: 100%; height: calc(100vh - 130px); border: none; background: white; }}
  a {{ color: #1E88E5; }}
</style>
</head>
<body>
<header>
  <h1>DR100 — Resource Interconnection Graph</h1>
  <div class="sub">Companion to <em>Wang Q. et al.</em> · Mapping the drug knowledge ecosystem for AI agents through resources, interfaces, and interconnections</div>
  <div class="stats">
    177 resources · 440 typed edges · single fully-connected component · modularity Q = 0.608 · 11 communities ·
    <a href="https://github.com/QSong-github/DR100">GitHub repo</a>
  </div>
</header>
<iframe src="rig_interactive.html" title="DR100 RIG"></iframe>
</body>
</html>
""")
print(f"Wrote: {gh_pages}")

print()
print("== DONE ==")
print(f"  static PDF: {pdf_path}")
print(f"  static PNG: {png_path}")
print(f"  interactive HTML: {html_path}")
print(f"  GitHub Pages index: {gh_pages}")
