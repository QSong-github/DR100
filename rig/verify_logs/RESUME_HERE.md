# Verification Progress — Resume Notes for Next Session

## Current state (as of session 2026-05-28 round 2)

- **228/441 edges verified (52%)** — up from 208/441 (47%) at session start
- **38 verification records** in `results.json` (some duplicates / name mismatches with CSV; 20 successfully applied)
- **213 edges remain unverified**

## What worked (highest yield)

**Third-party integrators** — each visit verifies 4-10 edges:

| Integrator | URL | Verified |
|---|---|---|
| CKG README | github.com/MannLabs/CKG | DrugBank/DisGeNET/Reactome/STRING |
| PharmacoDB datasets | pharmacodb.ca/datasets | CCLE/GDSC/PRISM/CTRP/NCI-60 cross-pairs |
| UniChem sources | ebi.ac.uk/unichem/sources | DrugBank/ChEMBL/ChEBI/HMDB/PubChem/BindingDB/DrugCentral chemistry bridges |
| Open Targets downloads | platform.opentargets.org/downloads | ChEMBL/DrugBank/Reactome/FAERS/HPO/Europe PMC |
| OpenBioLink README | github.com/openbiolink/openbiolink | DO/STITCH/GO/Reactome data tables |
| PharmKG README | github.com/MindRank-Biotech/PharmKG | DrugBank/STITCH/OMIM |
| Drug Repurposing Hub | repo-hub.broadinstitute.org | LINCS L1000/CMap |
| nSIDES README | github.com/tatonetti-lab/nsides-release | FAERS dependency |
| Clue.io /data | clue.io/data | LINCS L1000/CMap/Drug Repurposing Hub |
| KEGG Drug overview | kegg.jp/kegg/drug/ | ATC/DDD bridge |

## What failed (common patterns)

- **Cloudflare/anti-bot 403/CAPTCHA**: DrugBank, HMDB, Drugs.com, PMC papers (need user-session auth)
- **JS-rendered modern SPAs**: ChEMBL UI, DepMap, ROBOKOP, Clue.io app pages, DGIdb v5
- **404 / URL drift**: PrimeKG (snap-stanford → mims-harvard), some GitHub repos

## What to try in NEXT SESSION

### High-priority integrators not yet hit
1. **Hetionet eLife paper** (open access): https://elifesciences.org/articles/26726 — should list all 29 source resources
2. **DRKG paper** (arXiv 2010.09600): integrates 6 KGs + STRING/STITCH/IntAct
3. **PrimeKG README** (already fetched, results not yet recorded): mims-harvard/PrimeKG lists 20 sources including Bgee/CTD/DisGeNET/DrugBank/DrugCentral/Entrez/GO/HPO/MONDO/OMIM/Reactome/SIDER/UBERON/UMLS
4. **PubTator3 docs**: PMC-derived; lists which papers/databases it links
5. **Wikidata** for ATC/MeSH/RxNorm cross-references
6. **DailyMed structured product label** sample (any drug with SPL): shows ATC/MeSH/RxNorm fields directly
7. **DrugBank About / external links** via different URL bypassing Cloudflare (try search engine cache)
8. **HMDB downloads page** via NCBI cached version or paper

### Sources with no visible integrator path
For ~80-100 of remaining edges (mostly soft "complements" in narrow domains):
- Examples: WebMD ↔ Druglib, askapatient ↔ PsyTAR, BC5CDR ↔ CHEMDNER, n2c2 ↔ DDI Corpus
- Best strategy: cite the **§5.5 RIG construction paper review** as expert-curation evidence
- These should be labeled `provenance_tier=2` (DR100 panel consensus) in CSV
- Add CSV column: `provenance_tier ∈ {1=web-verified, 2=expert-curated, 3=conventional}`

## Files in this session

- `results.json` — 38 verification records (cumulative across all sessions)
- `verification_plan.json` — original 233-edge plan grouped by source
- `RESUME_HERE.md` — this file
- CSV: `main/rig_outputs/rig_edges_v1.csv` (228 high / 210 medium / 3 low)
- CSV backup: `rig_edges_v1.csv.pre_verify.bak`

## To resume next session

```bash
# Load this resume note
cat main/rig_outputs/verify_logs/RESUME_HERE.md

# Check current verification stats
python3 -c "import csv; from collections import Counter; 
rows=list(csv.DictReader(open('main/rig_outputs/rig_edges_v1.csv')));
print(Counter(r['confidence'] for r in rows))"

# Read pending integrators to try
# Then fire browser_batch calls to each
```

## Realistic completion estimate

- Current pace: ~10-20 verifications per focused session
- Remaining 213 edges → 12-20 sessions to fully verify
- Pragmatic stopping point: ~280-320 verified (65-72%); remainder honestly tagged as `provenance_tier=2`
