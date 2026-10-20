---
name: Propose a new resource
about: Suggest a Drug-centric, Drug-related, or Auxiliary resource for inclusion
title: "[New resource] <resource name>"
labels: new-resource
---

## Resource

**Name:**

**URL:**

**Paper / DOI:**

## Category

- [ ] Drug-centric: focuses directly on drugs, including datasets, benchmarks, text corpora, and tools built specifically around drugs
- [ ] Drug-related: broader biological or clinical information that also includes drugs (for example knowledge graphs, chemical text-mining corpora, clinical trials, medical terminology)
- [ ] Auxiliary: general biomedical information or evaluation material not specific to drugs (for example disease, gene, and pathway resources, clinical datasets, text collections, benchmarks)

## Type

- [ ] Database (DB)
- [ ] Dataset (curated, possibly static)
- [ ] Knowledge Graph (KG)

## Proposed description (best guess)

- **Subcategory:** _(use an existing value from `registry/*.json`; 32 labels are in use)_
- **Knowledge consumption mode** (`paradigm`): LLM-Friendly / Tool-Mediated
- **Knowledge interface** (`pathway`): Direct Prompt / RAG / Graph Query / REST / Computational / Hybrid
- **Main identifier system** (`identifier`): _(DrugBank ID / RxNorm / ChEMBL ID / name only / …)_
- **Access approach** (`access`): Open API / Open Download / Academic API / Academic Download / Web Only
- **Resource update status** (`update_cadence`): Continuous / Periodic Recent / Periodic Moderate / Periodic Stale / Abandoned Static / Static
- **Task tags** (`task_tags`, Drug-centric only): T1 identification, T2 labeling, T3 mechanism, T4 safety, T5 drug–drug interaction, T6 target binding, T7 response, T8 repurposing, T9 combination

## Why include it?

_(1-3 sentences on why this resource is useful for LLM drug agents)_

## Have you used it in an agent system?

_(Optional: link to your agent code or paper if applicable)_
