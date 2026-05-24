# DR100

**An integration-pathway atlas of 100 drug-centric knowledge resources for LLM-driven agent systems.**

DR100 is the companion machine-readable registry for the survey
*Wang Q., Liu T., Zhou M., Wang G., Su J., Song Q.* — **DR100: a systematic atlas
of drug-centric knowledge resources for LLM-driven agent systems** (under review,
*Briefings in Bioinformatics*).

The registry annotates **174 resources** (100 drug-centric + 30 drug-related + 44
auxiliary) along 10 fields that an LLM-agent engineer actually needs at build time:
integration pathway, identifier vocabulary, access class, update cadence, and more.

---

## What's in here

| Path | What it is |
|---|---|
| `schema/dr100_schema.json` | JSON Schema 7 specification for a single resource record |
| `registry/drug_centric.{json,tsv}` | 100 drug-centric resources, fully annotated |
| `registry/drug_related.{json,tsv}` | 30 indirect drug-related resources |
| `registry/auxiliary.{json,tsv}` | 44 general biomedical resources used by drug agents |
| **`examples/01–68_*.py`** | **68 runnable Python access scripts, one per LLM-Friendly resource** |
| `notebooks/01_quickstart.ipynb` | Load + filter + select resources for an agent |
| `scripts/build_registry.py` | Rebuild JSON/TSV from source files |
| `68DrugResources.xlsx` | Source spreadsheet for the 68 example scripts (curator working copy) |
| `docs/data_quality_report.md` | Discrepancy log between source files (v1.0) |
| `docs/contribution_guide.md` | How to propose new resources |

> The 68 example scripts demonstrate the *LLM-Friendly* subset (paradigm = LLM-Friendly,
> 68 of 100 drug-centric resources) with realistic access patterns:
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

# All 100 drug-centric resources
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

**Cognitive paradigm** &nbsp;`paradigm`: **LLM-Friendly** (68 of 100 drug-centric) vs **Tool-Mediated** (32 of 100)

**Operational integration pathway** &nbsp;`pathway`: one of
&nbsp;&nbsp; **Direct Prompt** (5) · **RAG** (20) · **Graph Query** (9) · **REST** (14) · **Computational** (35) · **Hybrid** (17)

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

## Versioning & roadmap

| Version | Scope |
|---|---|
| **v1.0 (this release)** | 100 drug-centric + 30 drug-related + 44 auxiliary; pathway/identifier/access/update authoritative for drug-centric |
| v1.1 (planned) | Resolve `needs_review` records; add `license` per resource; add `task_tags` |
| v1.x (quarterly) | Community-contributed additions via pull requests |
| v2.0 | Expanded catalog beyond the inaugural 100; DR-Bench integration |

Update cadence: **quarterly** releases tagged with semantic versioning.

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
  title   = {DR100: a systematic atlas of drug-centric knowledge resources for LLM-driven agent systems},
  author  = {Wang, Qing and Liu, Tianshi and Zhou, Minghao and Wang, Guangyu and Su, Jing and Song, Qianqian},
  journal = {Briefings in Bioinformatics},
  year    = {2026},
  note    = {Registry: \url{https://github.com/wq2581/DR100}}
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
