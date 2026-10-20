# DR100 Resource Interconnection Graph (RIG) — v1.0 Summary

**Nodes**: 177 resources (105 drug-centric + 29 drug-related + 43 auxiliary)
**Edges**: 440 typed edges (after validation)

## Edge type distribution

| Edge type | Count | %  |
|---|---|---|
| incorporates | 163 | 37.0% |
| derived_from | 43 | 9.8% |
| mirrors | 8 | 1.8% |
| bridges | 83 | 18.9% |
| complements | 100 | 22.7% |
| feeds_pipeline | 43 | 9.8% |

## Top 20 hub resources (by total degree)

Total = number of typed relationships incident to the resource, counting parallel relationships.
The Review's degree counts distinct neighbors instead (for example, DrugBank 34); see `rig/topology.md`.

| Rank | Resource | In-deg | Out-deg | Total | Category |
|---|---|---|---|---|---|
| 1 | DrugBank | 34 | 9 | 43 | drug_centric |
| 2 | PubMed Central Open Access Subset | 19 | 4 | 23 | auxiliary |
| 3 | UMLS (Unified Medical Language System) | 7 | 11 | 18 | drug_related |
| 4 | ChEMBL | 14 | 3 | 17 | drug_centric |
| 5 | ROBOKOP | 1 | 15 | 16 | drug_related |
| 6 | DailyMed | 14 | 1 | 15 | drug_centric |
| 7 | RxNorm | 7 | 8 | 15 | drug_centric |
| 8 | PubChem | 6 | 9 | 15 | drug_centric |
| 9 | Hetionet | 4 | 10 | 14 | drug_related |
| 10 | OREGANO | 4 | 9 | 13 | drug_centric |
| 11 | PrimeKG | 2 | 11 | 13 | drug_related |
| 12 | Open Targets Platform | 0 | 12 | 12 | drug_centric |
| 13 | ATC/DDD | 9 | 3 | 12 | drug_centric |
| 14 | LINCS L1000 | 6 | 5 | 11 | drug_centric |
| 15 | KEGG Drug | 7 | 4 | 11 | drug_centric |
| 16 | SIDER | 8 | 3 | 11 | drug_centric |
| 17 | DRKG | 5 | 5 | 10 | drug_centric |
| 18 | TDC (Therapeutics Data Commons) | 4 | 6 | 10 | drug_centric |
| 19 | DGIdb | 1 | 9 | 10 | drug_centric |
| 20 | STITCH | 2 | 7 | 9 | drug_centric |

## Top 10 incorporators (out-degree of `incorporates` edges)

| Rank | Aggregator | # integrated resources |
|---|---|---|
| 1 | ROBOKOP | 15 |
| 2 | Open Targets Platform | 11 |
| 3 | PrimeKG | 11 |
| 4 | Hetionet | 9 |
| 5 | OREGANO | 9 |
| 6 | STITCH | 7 |
| 7 | BioKG | 7 |
| 8 | BLUE Benchmark | 7 |
| 9 | TDC (Therapeutics Data Commons) | 6 |
| 10 | BLURB Benchmark | 6 |

## Most-integrated resources (in-degree of `incorporates` edges)

| Rank | Resource | # times integrated | Category |
|---|---|---|---|
| 1 | DrugBank | 16 | drug_centric |
| 2 | Reactome | 9 | auxiliary |
| 3 | SIDER | 6 | drug_centric |
| 4 | UMLS (Unified Medical Language System) | 6 | drug_related |
| 5 | DrugCentral | 5 | drug_centric |
| 6 | ChEMBL | 5 | drug_centric |
| 7 | Disease Ontology (DO) | 4 | auxiliary |
| 8 | MeSH Drug Pharmacological Actions | 4 | drug_centric |
| 9 | Gene Ontology (GO) | 4 | auxiliary |
| 10 | CTD (Comparative Toxicogenomics DB) | 4 | drug_related |
| 11 | KEGG Drug | 4 | drug_centric |
| 12 | GWAS Catalog | 4 | auxiliary |
| 13 | Hetionet | 3 | drug_related |
| 14 | LINCS L1000 | 3 | drug_centric |
| 15 | UniProt | 3 | auxiliary |

## Cross-category edge distribution

| Source cat → Target cat | Edges |
|---|---|
| drug_centric → drug_centric | 218 |
| auxiliary → auxiliary | 45 |
| drug_related → auxiliary | 36 |
| drug_related → drug_centric | 35 |
| drug_centric → auxiliary | 33 |
| drug_centric → drug_related | 29 |
| drug_related → drug_related | 22 |
| auxiliary → drug_related | 12 |
| auxiliary → drug_centric | 10 |

## Major aggregator details

### ROBOKOP (15 integrations)

- CTD (Comparative Toxicogenomics DB)
- GTEx (Genotype-Tissue Expression)
- GWAS Catalog
- LINCS L1000
- Reactome
- STRING
- ChEBI
- ClinicalTrials
- DrugCentral
- DRUGMECHDB
- Hetionet
- HMDB (Human Metabolome Database)
- IUPHAR/BPS Guide to Pharmacology
- CORD-19
- Monarch Initiative

### Open Targets Platform (11 integrations)

- ClinVar
- UniProt
- Orphanet
- Reactome
- Europe PMC
- GWAS Catalog
- ChEMBL
- DrugBank
- FAERS
- PharmGKB/ClinPGx
- CIViC

### PrimeKG (11 integrations)

- CTD (Comparative Toxicogenomics DB)
- DisGeNET
- DrugBank
- DrugCentral
- Gene Ontology (GO)
- HPO (Human Phenotype Ontology)
- OMIM (Online Mendelian Inheritance in Man)
- Reactome
- SIDER
- UMLS (Unified Medical Language System)
- Disease Ontology (DO)

### Hetionet (9 integrations)

- DrugBank
- Disease Ontology (DO)
- MeSH Drug Pharmacological Actions
- SIDER
- Gene Ontology (GO)
- Reactome
- DrugCentral
- UMLS (Unified Medical Language System)
- LINCS L1000

### OREGANO (9 integrations)

- DrugBank
- SIDER
- UniProt
- Reactome
- PharmGKB/ClinPGx
- HPO (Human Phenotype Ontology)
- ATC/DDD
- UMLS (Unified Medical Language System)
- Orphanet

### STITCH (7 integrations)

- DrugBank
- TTD
- CTD (Comparative Toxicogenomics DB)
- KEGG Drug
- Reactome
- ChEMBL
- PDB (Protein Data Bank)

### BioKG (7 integrations)

- UniProt
- DrugBank
- KEGG Drug
- SIDER
- Reactome
- CTD (Comparative Toxicogenomics DB)
- MeSH Drug Pharmacological Actions

### BLUE Benchmark (7 integrations)

- MedSTS
- BIOSSES
- BC5CDR
- DDI Corpus 2013
- ChemProt
- i2b2/VA 2010 Concepts/Assertions/Relations
- MedNLI

### TDC (Therapeutics Data Commons) (6 integrations)

- BindingDB
- KIBA
- DrugBank
- nSIDES
- DrugComb
- PrimeKG

### BLURB Benchmark (6 integrations)

- BC5CDR
- ChemProt
- DDI Corpus 2013
- BIOSSES
- BioASQ
- PubMedQA

### TarKG (6 integrations)

- Disease Ontology (DO)
- MeSH Drug Pharmacological Actions
- Gene Ontology (GO)
- DrugBank
- ChEMBL
- PubTator3

### DrugMAP (6 integrations)

- Orphanet
- HPO (Human Phenotype Ontology)
- DisGeNET
- KEGG Drug
- TTD
- PubChem

### PharmacoDB (5 integrations)

- CCLE (Cancer Cell Line Encyclopedia)
- CTRP (Cancer Therapeutics Response Portal)
- GDSC/GDSC2
- NCI-60
- PRISM DepMap

### SPOKE (5 integrations)

- LINCS L1000
- GWAS Catalog
- ChEMBL
- DrugBank
- SIDER

### DRKG (4 integrations)

- DrugBank
- Hetionet
- STRING
- DGIdb

### TOXRIC (4 integrations)

- ToxCast
- Open TG-GATEs
- DrugMatrix
- DILIrank 2.0

### CKG (Clinical Knowledge Graph) (4 integrations)

- DrugBank
- DisGeNET
- Reactome
- UMLS (Unified Medical Language System)

### GenomicKB (4 integrations)

- GWAS Catalog
- ClinVar
- GTEx (Genotype-Tissue Expression)
- TCGA (The Cancer Genome Atlas)

### MSI (Multiscale Interactome) (3 integrations)

- DrugBank
- DrugCentral
- Gene Ontology (GO)

### PubTator3 (3 integrations)

- PubMed Central Open Access Subset
- ChEBI
- MeSH Drug Pharmacological Actions

### PharmKG (3 integrations)

- DrugBank
- STITCH
- OMIM (Online Mendelian Inheritance in Man)

### OpenBioLink (3 integrations)

- DrugBank
- Hetionet
- Disease Ontology (DO)

### STRING (3 integrations)

- KEGG Drug
- Reactome
- PDB (Protein Data Bank)

### PubMed Knowledge Graph (PKG) (2 integrations)

- PubMed Central Open Access Subset
- ClinicalTrials

### SemMedDB (2 integrations)

- PubMed Central Open Access Subset
- UMLS (Unified Medical Language System)

### PROMISCUOUS 2.0 (2 integrations)

- DrugBank
- SIDER

### UniD3 (2 integrations)

- DrugBank
- ChEMBL

### NCATS Pharmaceutical Collection (NPC) (2 integrations)

- DailyMed
- ClinicalTrials

### CCLE (Cancer Cell Line Encyclopedia) (1 integrations)

- NCI-60

### LINCS L1000 (1 integrations)

- Drug Repurposing Hub

### MIMIC IV (1 integrations)

- MIMIC III

### IDG (1 integrations)

- DrugCentral

### MIMIC III (1 integrations)

- MIMIC II

### MIMIC II (1 integrations)

- MIMIC I

### BioKDE (1 integrations)

- UMLS (Unified Medical Language System)

### Drugs.com (1 integrations)

- DDInter

### ALMANAC (1 integrations)

- NCI-60

### DRMref (1 integrations)

- CCLE (Cancer Cell Line Encyclopedia)

### Drug Repurposing Hub (1 integrations)

- NCATS Pharmaceutical Collection (NPC)

### Cell Painting Gallery (1 integrations)

- JUMP-Cell Painting

