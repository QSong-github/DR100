# Changelog

All notable changes to the DR100 repository are documented in this file. Entries before 1.5.0
describe earlier drafts; their counts, names, and terms may differ from the Review.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

No changes yet.

## [1.5.1] — 2026-10-20

### Changed
- Text aligned with the current Review: primary-category definitions (README, schema, issue template, contribution
  guide), knowledge-interface names, evidence-reference counts for both relationship files, and the note that
  23 weak log entries correspond to 22 distinct relationships.
- RIG overview figure and interactive views: Review terminology and values (440 relationships, 392 resource pairs,
  one connected component when direction is ignored, Tier 1 326 / Tier 2 114, Q = 0.608), distinct-neighbor degree,
  betweenness on unweighted paths, communities numbered 1-11 as in `rig/topology.md`, neutral community names, and
  the six coordination patterns described as in the Review.
- `rig/make_figure.py` reads the data files in this repository, uses the stored layout
  (`figures/rig_layout.json`, spring layout with seed 42), and writes the Plotly view without the
  Python plotly package. `figures/figure_8_rig.{pdf,png}` and `figures/rig_interactive.html` regenerated.
- Notebook and example headers: no references to sections of earlier drafts; corrected the category of
  PharmGKB/ClinPGx and the type of OREGANO.

### Unchanged
- Data files are byte-identical to commit 2a144fd.

## [1.5.0] — 2026-10-19

### Changed
- Documentation aligned with the Review "Mapping the drug knowledge ecosystem for AI agents
  through resources, interfaces, and interconnections". README, CITATION.cff, index.html, and the
  figure and notebook text now use its title, authors, and terminology (primary category,
  knowledge consumption mode, knowledge interface, resource update status, status labels).
- README counts corrected to the data (relationship types 163 / 100 / 83 / 43 / 43 / 8;
  17 Drug-centric subcategories).
- `rig/topology.py` rewritten with the Review's definitions (distinct-neighbor degree, normalized
  betweenness on unweighted paths, greedy modularity with multiplicity weights and resolution 1,
  plus equal-weight and Tier 1 sensitivity analyses). `rig/topology.md` regenerated.
- `schema/dr100_schema.json`: task-tag values now match the data (T1–T9), `Static` added to the
  update status values, `task_tags_verified` allowed, descriptions updated. All 177 records
  validate, so the CI check passes again.

### Removed
- `supplementary_data/SupplementaryData_DR100.xlsx`, the tables of an earlier draft's
  supplementary material. The Review's Supplementary Data is distributed with the article.

### Unchanged
- Data files (`registry/*.json`, `registry/*.tsv`, `rig/edges.csv`, `rig/edges.tsv`,
  `rig/rig_edges_v1.csv`) are byte-identical to commit 2a144fd, which the Review cites.

## [1.4.0] — 2026-05-24

### Added
- 🌟 **Resource Interconnection Graph (RIG) v1.4** with 440 typed edges across 6 relation types
  - 326 edges Tier 1 web-verified against authoritative source documentation (URLs included)
  - 114 edges Tier 2 panel-curated over primary publications
  - Single fully-connected graph spanning all 177 resources
  - Modularity Q = 0.608 across 11 communities (greedy modularity decomposition)
- `rig/edges.{csv,tsv}` — machine-readable typed edge list with source URLs
- `rig/summary.md` + `rig/topology.md` — hubs, clusters, centralities, communities
- `rig/build_rig.py` + `rig/topology.py` — reproducible build and analysis scripts
- `rig/networkx.gpickle` — NetworkX MultiDiGraph for downstream use
- `figures/figure_8_rig.{pdf,png}` — static publication-quality Figure 8
- `figures/rig_interactive.html` — interactive Plotly visualization
- `index.html` — GitHub Pages landing page

### Methodology
- Phase A-M Chrome-based verification across 30+ hub resources
- Typed edges: `incorporates` (162), `complements` (97), `bridges` (83),
  `derived_from` (43), `feeds_pipeline` (41), `mirrors` (8)

## [1.0.0] — 2026-05-23

### Added
- Initial release of the DR100 machine-readable registry.
- 105 drug-centric resources with full annotation across 6 integration pathways.
- 29 drug-related (indirect) resources with base annotation.
- 43 auxiliary biomedical resources with base annotation.
- JSON Schema 7 specification (`schema/dr100_schema.json`).
- Quickstart Jupyter notebook (`notebooks/01_quickstart.ipynb`).
- Build script (`scripts/build_registry.py`) for reproducible registry assembly.
- Data-quality discrepancy report (`docs/data_quality_report.md`).
- **68 runnable Python access example scripts** (`examples/01–68_*.py`), one per
  LLM-Friendly drug-centric resource, demonstrating realistic download / API
  access patterns with fallbacks. Curator source spreadsheet preserved at
  `68DrugResources.xlsx`.

### Known issues
- 14 source-level discrepancies detected during v1.0 build (see data quality report);
  all carry `data_quality: "needs_review"` and will be resolved in v1.1.
- Pathway / identifier / access / update annotations are authoritative only for
  drug-centric resources; drug-related and auxiliary resources carry conservative
  default values pending fuller annotation in v1.1.
