# DR100

**A review of 177 drug-relevant data resources (105 drug-centric, 29 drug-related, 43 auxiliary) for large language model agents, organized by integration pathway with a Resource Interconnection Graph.**

The registry annotates **177 resources** (105 drug-centric + 29 drug-related + 43
auxiliary) along 10 fields that an LLM-agent engineer actually needs at build time:
integration pathway, identifier vocabulary, access class, update cadence, and more.

---

## What's in here

| Path | What it is |
|---|---|
| `schema/dr100_schema.json` | JSON Schema 7 specification for a single resource record |
| `registry/drug_centric.{json,tsv}` | 105 drug-centric resources, fully annotated |
| `registry/drug_related.{json,tsv}` | 29 indirect drug-related resources |
| `registry/auxiliary.{json,tsv}` | 43 general biomedical resources used by drug agents |
| 🌟 `rig/edges.{csv,tsv}` | **Resource Interconnection Graph: 440 typed edges across 6 relation types** |
| 🌟 `rig/summary.md` + `rig/topology.md` | RIG stats: hubs, clusters, modularity (Q = 0.608) |
| 🌟 `rig/build_rig.py` | Reproducible RIG construction with 326 Tier 1 web-verified evidence URLs |
| 🌟 `rig/networkx.gpickle` | NetworkX MultiDiGraph for downstream analysis |
| 🌟 `figures/figure_8_rig.{pdf,png}` | Static publication-quality RIG visualization |
| 🌟 `figures/rig_interactive.html` | Interactive RIG (Plotly) — pan/zoom/hover/legend toggle |
| 🌟 `index.html` | GitHub Pages landing page (live at https://qsong-github.github.io/DR100/) |
| **`examples/01–68_*.py`** | **68 runnable Python access scripts, one per LLM-Friendly resource** |
| `notebooks/01_quickstart.ipynb` | Load + filter + select resources for an agent |
| `scripts/build_registry.py` | Rebuild JSON/TSV from source files |
| `68DrugResources.xlsx` | Source spreadsheet for the 68 example scripts (curator working copy) |
| `docs/data_quality_report.md` | Discrepancy log between source files (v1.0) |
| `docs/contribution_guide.md` | How to propose new resources |

## 🌐 Live interactive RIG visualization

**[https://qsong-github.github.io/DR100/](https://qsong-github.github.io/DR100/)** — pan/zoom the 177-resource graph, hover for resource details, click legend entries to toggle edge types.

## 🔗 Resource Interconnection Graph (RIG) at a glance

The 177 DR100 resources form a **single fully-connected typed multigraph** with **440 inter-resource edges**:

| Edge type | Count | What it means |
|---|---|---|
| `incorporates` | 162 | A integrates B's data (e.g., DRKG incorporates DrugBank, Hetionet, STRING) |
| `derived_from` | 43 | A's content is extracted from B (e.g., SIDER from FDA SPL labels) |
| `mirrors` | 8 | A and B are alternative interfaces to same data (e.g., openFDA mirrors DailyMed) |
| `bridges` | 83 | A normalizes IDs across B and others (e.g., RxNorm bridges DrugBank, ATC, SNOMED) |
| `complements` | 97 | A and B are used together for full coverage (e.g., DDInter + MecDDI) |
| `feeds_pipeline` | 41 | A's output is B's typical input (e.g., LINCS L1000 → CLUE.io) |

**Top hubs by betweenness centrality:** UMLS (0.28), PubMed Central (0.21), DailyMed (0.19), DrugBank (0.18), LINCS L1000 (0.16), ChEMBL (0.14)
**Top hubs by eigenvector centrality:** DrugBank (0.52), Hetionet (0.24), ChEMBL (0.21), PrimeKG (0.20), DrugCentral (0.20)
**Modularity Q = 0.608** across **11 communities** (chemoinformatics, KG aggregators, FDA labels/PV, biomedical NLP, evidence integration, identifier bridges, drug-target evidence, drug combination, disease ontology, cancer PGx, EHR-NLP)

326 of 440 edges carry directly-fetched (Tier 1) provenance URLs to authoritative integration documentation; the remaining 114 (Tier 2) are panel-curated over primary source publications.

> The 68 example scripts demonstrate the *LLM-Friendly* subset (paradigm = LLM-Friendly,
> 70 of 105 drug-centric resources) with realistic access patterns:
> download URLs, API endpoints, fallback mirrors, and minimal parsing. Use them as
> reference implementations when wiring resources into an agent's tool registry.

---

## Quick start

```bash
pip install jsonschema pandas
```

```python
import json
from pathlib import Path

registry = json.loads(Path("registry/drug_centric.json").read_text())

# All 105 drug-centric resources
print(f"{len(registry)} resources")

# Filter: agent needs Drug-Drug Interaction tools with Open API access,
# updated within the last 2 years
ddi_tools = [
    r for r in registry
    if r["subcategory"] == "Drug-Drug Interaction (DDI)"
    and r["access"] == "Open API"
    and r["update_cadence"] in ("Continuous", "Periodic Recent")
]
for r in ddi_tools:
    print(f"  {r['name']:30s} | {r['pathway']:15s} | {r['identifier']}")
```

Or via pandas:

```python
import pandas as pd
df = pd.read_csv("registry/drug_centric.tsv", sep="\t")
df.query("pathway == 'Hybrid' and access == 'Open API'")[["name", "subcategory", "identifier"]]
```

---

## Schema overview

Each resource record carries:

**Identity** &nbsp;`name`, `aliases`, `link`, `paper_link`

**Categorical** &nbsp;`category` (drug-centric / related / auxiliary), `type` (DB / Dataset / KG), `subcategory` (15 / 9 / 8 controlled values)

**Cognitive paradigm** &nbsp;`paradigm`: **LLM-Friendly** (70 of 105 drug-centric) vs **Tool-Mediated** (35 of 105)

**Operational integration pathway** &nbsp;`pathway`: one of
&nbsp;&nbsp; **Direct Prompt** (6) · **RAG** (21) · **Graph Query** (9) · **REST** (14) · **Computational** (38) · **Hybrid** (17)

**Implementation axes** &nbsp;`identifier`, `access`, `update_cadence`, `license`, `task_tags` (T1-T9)

**Provenance** &nbsp;`aim`, `source`, `description`, `data_quality`, `notes`

See [`schema/dr100_schema.json`](schema/dr100_schema.json) for the formal spec.

---

## Pathway taxonomy at a glance

| Pathway | Definition | When to use |
|---|---|---|
| **Direct Prompt** | < 4K-token curated text, loaded once into context | Small fixed reference (EML, ATC, CPIC tables) |
| **RAG** | Long-form text, chunked + embedded + retrieved | Drug labels, monographs, literature corpora |
| **Graph Query** | Typed entities/relations, LLM generates Cypher/SPARQL | Multi-hop reasoning over KGs |
| **REST** | Documented JSON/XML APIs, wrapped as function calls | Fresh structured records (FAERS, Open Targets) |
| **Computational** | Cheminformatics / ML pipelines, out-of-process tools | SMILES libraries, bioactivity matrices, signatures |
| **Hybrid** | Provides multiple of the above in one resource | DrugBank, ChEMBL, PharmGKB |

Full taxonomy and decision tree: see §3.3 and Figure 6 of the paper.

---

## Contributing

We welcome PRs that:
- Add new drug-centric / drug-related / auxiliary resources
- Correct annotations on existing records
- Improve schema coverage (e.g., richer task tagging)
- Add demo notebooks for additional case studies

See [`docs/contribution_guide.md`](docs/contribution_guide.md). All PRs are validated
against the JSON Schema automatically.

---

## Citing DR100

If you use the registry or the survey, please cite:

```bibtex
@article{wang2026dr100,
  title   = {DR100: A Review of Drug-Centric Data Resources for Large Language Model Agents},
  author  = {Wang, Qing and Tang, Dingyi and Liang, Jialu and Wang, Guangyu and Su, Jing and Song, Qianqian},
  year    = {2026},
  note    = {Registry: \url{https://github.com/QSong-github/DR100}}
}
```

Citation metadata is also provided in [CITATION.cff](CITATION.cff) for tools that
support the Citation File Format.

---

## License

- **Data** (everything under `registry/` and `schema/`): [CC BY 4.0](LICENSE-DATA)
- **Code** (everything under `scripts/`, `notebooks/`): [MIT](LICENSE-CODE)

Individual resources catalogued by DR100 retain their original licenses; the
`access` field per record reflects each resource's own terms.

---

## Contact

Correspondence: **Qianqian Song, PhD** — `qsong1@ufl.edu`
First author: **Qing Wang** — `wang.qing@ufl.edu`
Department of Health Outcomes and Biomedical Informatics, University of Florida
