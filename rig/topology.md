# DR100 RIG Topology Analysis (v1.0)

**Graph**: directed multigraph, **177** nodes, **440** edges
**Undirected projection** (for community detection): 177 nodes, 392 unique edges
**Nodes with ≥1 connection**: 177 (100%)
**Connected components**: 1; giant component covers **177** nodes (100% of all DR100 resources)

## Connectivity by component (Top 8)

| Component | Size | Sample members |
|---|---|---|
| 1 | 177 | ADE Corpus, ADReCS, ALMANAC, ATC/DDD, BC5CDR, BIOSSES |

## Top 15 by betweenness centrality (bridge resources)

Betweenness = fraction of shortest paths in the giant component that pass through this node.
High-betweenness nodes are **structural bridges** — agents whose query crosses many resource boundaries must route through them.

| Rank | Resource | Betweenness | Category |
|---|---|---|---|
| 1 | UMLS (Unified Medical Language System) | 0.224 | drug_related |
| 2 | PubMed Central Open Access Subset | 0.203 | auxiliary |
| 3 | DrugBank | 0.178 | drug_centric |
| 4 | ROBOKOP | 0.143 | drug_related |
| 5 | LINCS L1000 | 0.135 | drug_centric |
| 6 | DailyMed | 0.127 | drug_centric |
| 7 | ChEMBL | 0.116 | drug_centric |
| 8 | MIMIC IV | 0.082 | auxiliary |
| 9 | TDC (Therapeutics Data Commons) | 0.082 | drug_centric |
| 10 | DRKG | 0.075 | drug_centric |
| 11 | DGIdb | 0.075 | drug_centric |
| 12 | Hetionet | 0.071 | drug_related |
| 13 | Open Targets Platform | 0.071 | drug_centric |
| 14 | MIMIC III | 0.071 | auxiliary |
| 15 | RxNorm | 0.065 | drug_centric |

## Top 15 by eigenvector centrality (importance hubs)

Eigenvector centrality favors nodes connected to other well-connected nodes — the 'central elite' of the registry.

| Rank | Resource | Eigenvector | Category |
|---|---|---|---|
| 1 | DrugBank | 0.523 | drug_centric |
| 2 | Hetionet | 0.224 | drug_related |
| 3 | ChEMBL | 0.207 | drug_centric |
| 4 | PrimeKG | 0.192 | drug_related |
| 5 | DrugCentral | 0.191 | drug_centric |
| 6 | PubChem | 0.191 | drug_centric |
| 7 | RxNorm | 0.185 | drug_centric |
| 8 | UMLS (Unified Medical Language System) | 0.184 | drug_related |
| 9 | OREGANO | 0.178 | drug_centric |
| 10 | KEGG Drug | 0.176 | drug_centric |
| 11 | DRKG | 0.167 | drug_centric |
| 12 | ChEBI | 0.158 | drug_centric |
| 13 | STITCH | 0.157 | drug_centric |
| 14 | ROBOKOP | 0.156 | drug_related |
| 15 | TDC (Therapeutics Data Commons) | 0.153 | drug_centric |

## Community structure (greedy modularity, Q = 0.608)

Detected **11** communities in the giant component.

### Cluster 1: 36 resources | category mix: {'drug_centric': 17, 'auxiliary': 11, 'drug_related': 8}

- DrugBank (deg 34)
- UMLS (Unified Medical Language System) (deg 18)
- ROBOKOP (deg 16)
- RxNorm (deg 13)
- PrimeKG (deg 12)
- OREGANO (deg 12)
- Hetionet (deg 12)
- ATC/DDD (deg 9)
- Reactome (deg 9)
- DRKG (deg 8)
- DrugCentral (deg 8)
- Disease Ontology (DO) (deg 7)
- DrugMAP (deg 7)
- BioKG (deg 7)
- MeSH Drug Pharmacological Actions (deg 7)
- HPO (Human Phenotype Ontology) (deg 6)
- TarKG (deg 6)
- Orphanet (deg 5)
- OMIM (Online Mendelian Inheritance in Man) (deg 5)
- Monarch Initiative (deg 5)
- ... (16 more)

### Cluster 2: 28 resources | category mix: {'auxiliary': 13, 'drug_related': 8, 'drug_centric': 7}

- PubMed Central Open Access Subset (deg 20)
- BLUE Benchmark (deg 8)
- BLURB Benchmark (deg 7)
- BC5CDR (deg 7)
- PubTator3 (deg 5)
- ADE Corpus (deg 5)
- ChemProt (deg 4)
- DDI Corpus 2013 (deg 4)
- MedQA (deg 3)
- SemMedDB (deg 3)
- CORD-19 (deg 3)
- DrugProt (deg 3)
- BioKDE (deg 3)
- CHEMDNER (deg 3)
- PubMedQA (deg 3)
- NLM-Chem-BC7 (deg 3)
- BioASQ (deg 3)
- PubMed Knowledge Graph (PKG) (deg 3)
- iKraph (deg 3)
- MedMCQA (deg 2)
- ... (8 more)

### Cluster 3: 21 resources | category mix: {'drug_centric': 17, 'auxiliary': 2, 'drug_related': 2}

- ChEMBL (deg 17)
- PubChem (deg 13)
- KEGG Drug (deg 10)
- TDC (Therapeutics Data Commons) (deg 8)
- STITCH (deg 8)
- ChEBI (deg 7)
- BindingDB (deg 6)
- MoleculeNet (deg 6)
- STRING (deg 6)
- HMDB (Human Metabolome Database) (deg 5)
- PDB (Protein Data Bank) (deg 4)
- e-Drug3D (deg 3)
- ZINC (deg 3)
- KIBA (deg 3)
- M3-20M (deg 2)
- PDBbind (deg 2)
- DrugOOD (deg 2)
- Polaris (deg 2)
- UniD3 (deg 2)
- DTC (Drug Target Commons) 2.0 (deg 2)
- ... (1 more)

### Cluster 4: 20 resources | category mix: {'drug_related': 3, 'drug_centric': 17}

- LINCS L1000 (deg 10)
- Drug Repurposing Hub (deg 7)
- ClinicalTrials (deg 5)
- NCATS Pharmaceutical Collection (NPC) (deg 4)
- JUMP-Cell Painting (deg 4)
- DrugRepoBank (deg 4)
- RepoDB (deg 4)
- Cochrane Library (deg 2)
- GEO Drug Perturbation Signatures (deg 2)
- DrugSig (deg 2)
- Tahoe (deg 2)
- TrialPanorama (deg 2)
- DrugRepurposing Online (deg 2)
- RepurposeDrugs (deg 2)
- Clue (deg 2)
- TRANSCRIPT DRUG REPURPOSING DATASET (deg 2)
- RxRx3 (deg 1)
- ReframeDB (deg 1)
- EK-DRD (deg 1)
- Cell Painting Gallery (deg 1)

### Cluster 5: 14 resources | category mix: {'drug_centric': 12, 'auxiliary': 2}

- DailyMed (deg 12)
- DILIrank 2.0 (deg 4)
- TOXRIC (deg 4)
- Drugs.com (deg 4)
- Open TG-GATEs (deg 3)
- LiverTox (deg 3)
- UniTox (deg 2)
- TAC 2017 ADR (deg 2)
- DrugMatrix (deg 2)
- ToxCast (deg 2)
- MedlinePlus Drug Info (deg 2)
- MedQuAD (deg 2)
- ChatDoctor Dataset (deg 2)
- RxList Drug Descriptions (deg 1)

### Cluster 6: 12 resources | category mix: {'auxiliary': 4, 'drug_related': 2, 'drug_centric': 6}

- CCLE (Cancer Cell Line Encyclopedia) (deg 7)
- GDSC/GDSC2 (deg 7)
- PharmacoDB (deg 6)
- TCGA (The Cancer Genome Atlas) (deg 5)
- DRMref (deg 4)
- PRISM DepMap (deg 4)
- GenomicKB (deg 4)
- GTEx (Genotype-Tissue Expression) (deg 3)
- NCI-60 (deg 3)
- CTRP (Cancer Therapeutics Response Portal) (deg 3)
- ClinVar (deg 2)
- CancerDR (deg 2)

### Cluster 7: 12 resources | category mix: {'drug_centric': 8, 'drug_related': 2, 'auxiliary': 2}

- Open Targets Platform (deg 12)
- SIDER (deg 10)
- MedDRA (deg 8)
- FAERS (deg 6)
- SPOKE (deg 5)
- openFDA Human Drug (deg 5)
- GWAS Catalog (deg 4)
- VigiAccess (deg 3)
- nSIDES (deg 2)
- PROMISCUOUS 2.0 (deg 2)
- ADReCS (deg 2)
- Europe PMC (deg 1)

### Cluster 8: 11 resources | category mix: {'drug_centric': 7, 'drug_related': 4}

- DGIdb (deg 10)
- PharmGKB/ClinPGx (deg 6)
- TTD (deg 4)
- OncoKB (deg 3)
- CIViC (deg 3)
- IUPHAR/BPS Guide to Pharmacology (deg 3)
- CPIC (deg 3)
- NCI Thesaurus (NCIt) (deg 2)
- Molecular Targets Platform (deg 2)
- GDKD (Genomics-Drug Knowledge DB) (deg 1)
- PharmVar (deg 1)

### Cluster 9: 10 resources | category mix: {'drug_centric': 1, 'auxiliary': 9}

- MIMIC III (deg 7)
- MIMIC IV (deg 4)
- MedNLI (deg 3)
- DrugEHRQA (deg 2)
- MIMIC II (deg 2)
- i2b2/VA 2010 Concepts/Assertions/Relations (deg 2)
- Medical Information Mart (MIMIC-CXR) (deg 1)
- emrQA (deg 1)
- eICU Collaborative Research DB (deg 1)
- MIMIC I (deg 1)

### Cluster 10: 8 resources | category mix: {'drug_centric': 8}

- DrugComb (deg 6)
- FDA Orange Book (deg 4)
- DrugCombDB (deg 4)
- DCDB (Drug Combination DB) (deg 2)
- CDCDB (deg 2)
- SYNERGxDB (deg 2)
- ALMANAC (deg 2)
- SynergyFinder (deg 1)

### Cluster 11: 5 resources | category mix: {'drug_centric': 5}

- askapatient (deg 3)
- CADEC (deg 3)
- Drug Reviews (Druglib.com) (deg 2)
- WebMD Drug Reviews (deg 2)
- PsyTAR (deg 2)

