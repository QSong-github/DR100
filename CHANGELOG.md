# Changelog

All notable changes to the DR100 registry are documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned for v1.1
- Resolve all `data_quality: "needs_review"` records (target: 0 in drug_centric)
- Add `license` field per resource (CC-BY, custom academic, etc.)
- Populate `task_tags` (T1–T9) per resource
- Add 2 supplementary drug-related records currently in paper but missing from registry
  (Hetionet data download, KEGG DRUG / MEDICUS)
- Resolve PharmGKB/ClinPGx categorization (drug-centric vs drug-related)

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
