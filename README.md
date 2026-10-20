# DR100

Companion data and code for the Review **"Mapping the drug knowledge ecosystem for AI agents through resources, interfaces, and interconnections"** by Qing Wang, Sipei Gu, Dingyi Tang, Qizhen Lan, Xiaoqian Jiang, Jing Su, Baijian Yang, and Qianqian Song.

The Review examines **177 resources** that can support drug-related tasks of AI agents. This repository holds the two data products it analyses:

- the **resource table**, which describes one resource at a time (primary category, subcategory, knowledge consumption mode, knowledge interface, identifiers, access, update status, and task tags), and
- the **Resource Interconnection Graph (RIG)**, in which each of the 177 resources is a node and 440 directed relationships of six types describe how pairs of resources are connected.

DR100 is the repository name. It is not another name for the RIG, and the Review covers 177 resources, not 100.

---

## Version used in the Review

All quantitative results in the Review were computed from commit
[`2a144fd6d129af0273d6145fd21498aaa7ac0bb7`](https://github.com/QSong-github/DR100/commit/2a144fd6d129af0273d6145fd21498aaa7ac0bb7).
Later commits change documentation, the schema, the RIG overview figure and interactive views, and analysis scripts. The data files below are byte-identical to that commit.

| Data file | Content |
|---|---|
| `registry/drug_centric.json` (+ `.tsv`) | 105 Drug-centric resources |
| `registry/drug_related.json` (+ `.tsv`) | 29 Drug-related resources |
| `registry/auxiliary.json` (+ `.tsv`) | 43 Auxiliary resources |
| `rig/edges.csv` (+ `.tsv`) | 440 RIG relationships with evidence reference, confidence label, and note |
| `rig/rig_edges_v1.csv` | The same 440 source-type-target rows with their provenance tier. Its evidence references, confidence labels, and notes come from a later checking pass and differ from `rig/edges.csv`; the Review's confidence counts use `rig/edges.csv` |

## Repository contents

| Path | What it is |
|---|---|
| `schema/dr100_schema.json` | JSON Schema for one resource record (checked by CI on every push) |
| `rig/topology.py`, `rig/topology.md` | Graph analysis with the definitions used in the Review |
| `rig/make_figure.py` | Draws the RIG overview figure and the Plotly view from the data files (layout stored in `figures/rig_layout.json`) |
| `rig/summary.md` | Relationship-type counts and a typed-edge degree table |
| `rig/build_rig.py`, `rig/verification_plan.json`, `rig/verify_logs/` | Original RIG construction script and checking logs |
| `scripts/build_registry.py`, `scripts/apply_provenance_tier.py`, `scripts/apply_verifications.py` | Original scripts used to build the resource table and assign provenance tiers |
| `rig/networkx.gpickle` | The RIG as a NetworkX MultiDiGraph |
| `figures/`, `index.html` | RIG overview figure and interactive views drawn from the same data (open `index.html` in a browser). The Review's Figure 5 is published with the article |
| `examples/01–68_*.py`, `68DrugResources.xlsx` | Access scripts for 68 resources and their source spreadsheet |
| `notebooks/01_quickstart.ipynb` | Loading and filtering the resource table |
| `docs/` | Contribution guide and the construction log of the resource table |

---

## Resource table

Each resource has one primary category and one main value per field. The field names predate the Review's terminology. The mapping is:

| Review term | Field | Values (counts over all 177 resources unless noted) |
|---|---|---|
| Primary category | `category` | `Drug-centric` 105, `Drug-related (indirect)` 29, `auxiliary` 43 |
| Subcategory | `subcategory` | 32 distinct labels (17 within Drug-centric, 9 within Drug-related, 8 within Auxiliary) |
| Knowledge consumption mode | `paradigm` | `LLM-Friendly` 134, `Tool-Mediated` 43 |
| Knowledge interface | `pathway` | `Direct Prompt` (Direct Prompting) 6, `RAG` (Retrieval-Augmented Generation) 91, `Graph Query` (Graph Queries) 9, `REST` (Structured REST APIs) 14, `Computational` (Computational Tool Invocation) 38, `Hybrid` (Hybrid Interfaces) 18, missing 1 |
| Main identifier system | `identifier` | `name only` 91, `DrugBank ID` 29, `InChIKey` 9, `SMILES` 7, `RxNorm` 7, `ChEMBL ID` 6, `ATC` 4, `PubChem CID` 3, 17 other systems 20, missing 1 |
| Access approach | `access` | `Open Download` 124, `Open API` 33, `Academic Download` 12, `Academic API` 3, `Web Only` 4, missing 1 |
| Resource update status | `update_cadence` | `Continuous` 11, `Periodic Recent` 38, `Periodic Moderate` 94, `Periodic Stale` 10, `Abandoned Static` 21, `Static` 2, missing 1 |
| Task tags (Drug-centric only) | `task_tags` | T1 identification 39, T2 labeling 36, T3 mechanism 20, T4 safety 31, T5 drug–drug interaction 8, T6 target binding 41, T7 response 23, T8 repurposing 25, T9 combination 9 (232 assignments) |
| Status label | `data_quality` | `authoritative` 99, `needs_review` 78 (7 Drug-centric, 28 Drug-related, 43 Auxiliary) |
| License | `license` | Populated for 3 resources |

Other fields are `name`, `type` (KG, DB, or Dataset), `aim`, `source`, `description`, `link`, `paper_link`, `notes`, and, for 11 broad knowledge bases whose task tags were checked individually, `task_tags_verified`.

Notes on interpretation:

- **Primary categories** group resources by how directly they concern drugs. Drug-centric resources focus directly on drugs (chemical properties, pharmacology, pharmacogenomics, toxicity, drug interactions, and therapeutic applications), including datasets, benchmarks, text corpora, and tools built specifically around drugs. Drug-related resources focus on broader biological or clinical information that also includes drugs, such as biomedical knowledge graphs, chemical text-mining corpora, clinical trials, and medical terminology. Auxiliary resources provide general biomedical information or evaluation material that is not specific to drugs, including disease, gene, and pathway resources, clinical datasets, biomedical text collections, and benchmarks.
- **Status labels** come from the construction script (`scripts/build_registry.py`). A record is `authoritative` when its name matched the source spreadsheets exactly and its field values were accepted. It is `needs_review` when the name matched only approximately (similarity threshold 0.88) or not at all, or when a Drug-related or Auxiliary record carried default-looking values (RAG with name-only identifiers). The labels describe the construction process, not an independent validation of each field.
- **Update status** follows the original classification (Recent about one year, Moderate one to two years, Stale two to five years since the last update). The files do not store update dates.
- **Task tags** were first assigned from subcategories and keyword matches in `aim` and `description`, then checked for selected broad knowledge bases. A tag marks a possible use, not a task an agent has completed with that resource.
- The record `i2b2/VA 2010 Concepts/Assertions/Relations` has no interface, identifier, access, or update value.

---

## Resource Interconnection Graph

| Type | Count | Meaning |
|---|---|---|
| `incorporates` | 163 | The source integrates content supplied by the target (for example, DRKG incorporates DrugBank, Hetionet, and STRING) |
| `complements` | 100 | The two resources provide information that may be useful together; no fixed order of operations |
| `bridges` | 83 | A mapping that can help connect resources using different identifiers or terminology |
| `derived_from` | 43 | The source was created by selecting, transforming, or reorganizing the target's content (for example, PLINDER from the Protein Data Bank) |
| `feeds_pipeline` | 43 | The source's output can serve as the target's input (for example, Open TG-GATEs feeds TOXRIC) |
| `mirrors` | 8 | One resource redistributes the other's content with minimal change (for example, openFDA and DailyMed serve the same structured product labels) |

As in the Review, direction carries a specific meaning for `incorporates`, `derived_from`, and `feeds_pipeline`. `complements` implies no fixed order, and the recorded direction of `bridges` and `mirrors` is not interpreted.

**Labels on relationships.** Confidence (`confidence` in `rig/edges.csv`) is high for 211, medium for 226, and low for 3 relationships. The provenance tier (`provenance_tier` in `rig/rig_edges_v1.csv`) is Tier 1 for 326 relationships (supported by retrieved external evidence) and Tier 2 for 114 (curator-interpreted). These are the project's recorded classifications, not probabilities of correctness. In `rig/edges.csv`, 225 evidence references cite section numbers of an earlier draft of the Review (`DR100-§…`) and 14 cite `Convention`, rather than external documentation; 30 such section references remain in `rig/rig_edges_v1.csv`. The checking logs in `rig/verify_logs/` do not cover all 440 relationships, and 23 entries labeled weak in `rig/verify_logs/audit_v2.json` (22 distinct relationships, one logged twice) are Tier 1 in `rig/rig_edges_v1.csv`.

**Structure** (as reported in the Review). The Review's values were computed with the self-contained scripts distributed as its Supplementary Code; `python rig/topology.py` applies the same definitions to the same files, gives the same values, and writes `rig/topology.md`:

- The directed multigraph has no duplicate source-type-target rows and no self-links. Ignoring direction, the 440 relationships connect 392 distinct resource pairs, and all 177 resources form one connected component.
- Degree (distinct neighbors): DrugBank 34, PubMed Central Open Access Subset 20, UMLS 18, ChEMBL 17, ROBOKOP 16.
- Normalized betweenness on unweighted paths is highest for DrugBank, the PubMed Central Open Access Subset, UMLS, DailyMed, and LINCS L1000.
- Greedy modularity with relationship multiplicity as pair weight and resolution 1 gives 11 communities, Q = 0.608 (sizes 36, 28, 21, 20, 14, 12, 12, 11, 10, 8, 5). Equal pair weights also give 11 communities, Q = 0.588, with different membership.
- Keeping only the 326 Tier 1 relationships leaves 294 resource pairs and 42 connected components (one of 134 resources, two of two resources, and 39 isolated resources).

An undirected path between two resources does not mean an agent can follow it as a sequence of available operations.

---

## Quick start

```python
import json
from pathlib import Path

tables = {f: json.loads(Path(f"registry/{f}.json").read_text())
          for f in ("drug_centric", "drug_related", "auxiliary")}
print(sum(len(t) for t in tables.values()))  # 177

# Drug-centric drug-drug interaction resources with an open API and a recent update status
ddi = [r for r in tables["drug_centric"]
       if r["subcategory"] == "Drug-Drug Interaction (DDI)"
       and r["access"] == "Open API"
       and r["update_cadence"] in ("Continuous", "Periodic Recent")]
for r in ddi:
    print(r["name"], r["pathway"], r["identifier"], sep=" | ")
```

Or with pandas:

```python
import pandas as pd
df = pd.read_csv("registry/drug_centric.tsv", sep="\t")
df.query("pathway == 'Hybrid' and access == 'Open API'")[["name", "subcategory", "identifier"]]
```

---

## Citation

```bibtex
@article{wang2026mapping,
  title  = {Mapping the drug knowledge ecosystem for AI agents through resources, interfaces, and interconnections},
  author = {Wang, Qing and Gu, Sipei and Tang, Dingyi and Lan, Qizhen and Jiang, Xiaoqian and Su, Jing and Yang, Baijian and Song, Qianqian},
  year   = {2026},
  note   = {Data and code: \url{https://github.com/QSong-github/DR100}}
}
```

Citation metadata is also provided in [CITATION.cff](CITATION.cff).

---

## License

- Resource-table data and schema (`registry/`, `schema/`): [CC BY 4.0](LICENSE-DATA)
- Code (`scripts/`, `notebooks/`): [MIT](LICENSE-CODE)

Each catalogued resource keeps its own license and terms of use.

## Contact

Correspondence: Qianqian Song (song1081@purdue.edu)
