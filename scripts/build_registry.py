#!/usr/bin/env python3
"""
Build DR100 JSON + TSV registry from Excel base data + Supplementary docx annotations.

Excel files are treated as authoritative for base fields.
Supplementary Tables S1-S3 contribute Pathway / Identifier / Access / Update annotations.
For records with name mismatches, fuzzy matching is attempted; unmatched records
are flagged with data_quality="needs_review".

Usage:
    python scripts/build_registry.py
"""
from __future__ import annotations
import json
import csv
import sys
from pathlib import Path
from difflib import SequenceMatcher

try:
    from openpyxl import load_workbook
    from docx import Document
except ImportError:
    sys.exit("pip install openpyxl python-docx jsonschema")

REPO_ROOT = Path(__file__).resolve().parent.parent
PROJECT_ROOT = REPO_ROOT.parent  # the "drug resource" dir with the source xlsx/docx
REGISTRY_DIR = REPO_ROOT / "registry"

EXCEL_FILES = {
    "drug_centric": PROJECT_ROOT / "DrugCentric_complete.xlsx",
    "drug_related": PROJECT_ROOT / "DrugRelated_complete.xlsx",
    "auxiliary":    PROJECT_ROOT / "Auxiliary_complete.xlsx",
}
SUPP_DOCX = PROJECT_ROOT / "review paper" / "DR100_supplementary.docx"
SUPP_TABLE_IDX = {"drug_centric": 0, "drug_related": 1, "auxiliary": 2}


def norm(s: str) -> str:
    """Normalize a name for fuzzy comparison."""
    if not s:
        return ""
    return "".join(ch.lower() for ch in s if ch.isalnum())


def fuzzy_match(name: str, candidates: list[str], threshold: float = 0.88) -> str | None:
    """Conservative fuzzy match.

    threshold=0.88 is tuned to catch trivial version/punctuation variants
    (e.g., 'DILIrank' vs 'DILIrank 2.0', 'GenomicKB' vs 'GenomicKG')
    while rejecting unrelated names that share a common suffix (e.g.,
    'Molecular Targets Platform' vs 'Open Targets Platform').
    """
    if not name or not candidates:
        return None
    nn = norm(name)
    best, best_score = None, 0.0
    for c in candidates:
        score = SequenceMatcher(None, nn, norm(c)).ratio()
        if score > best_score:
            best, best_score = c, score
    return best if best_score >= threshold else None


def load_excel_rows(path: Path) -> list[dict]:
    wb = load_workbook(path, read_only=True)
    ws = wb[wb.sheetnames[0]]
    rows = list(ws.iter_rows(values_only=True))
    headers = [str(h).strip() if h else "" for h in rows[0]]
    out = []
    for r in rows[1:]:
        if not r or not r[0]:
            continue
        rec = {}
        for i, h in enumerate(headers):
            if not h:
                continue
            v = r[i]
            rec[h] = str(v).strip() if v is not None else None
        out.append(rec)
    return out


def load_supp_annotations(docx_path: Path, table_idx: int) -> dict[str, dict]:
    """Returns name -> {Pathway, Identifier, Access, Update}."""
    doc = Document(str(docx_path))
    t = doc.tables[table_idx]
    rows = list(t.rows)
    headers = [c.text.strip() for c in rows[0].cells]
    out = {}
    for r in rows[1:]:
        cells = [c.text.strip() for c in r.cells]
        if not cells[0]:
            continue
        rec = dict(zip(headers, cells))
        out[rec["Name"]] = rec
    return out


def map_pathway(s: str) -> str | None:
    if not s:
        return None
    s = s.strip()
    mapping = {
        "Direct Prompt": "Direct Prompt",
        "RAG": "RAG",
        "Graph Query": "Graph Query",
        "REST": "REST",
        "Computational": "Computational",
        "Hybrid": "Hybrid",
    }
    return mapping.get(s)


def map_access(s: str) -> str | None:
    if not s:
        return None
    s = s.strip()
    valid = {"Open API", "Open Download", "Academic API", "Academic Download", "Web Only", "Commercial"}
    return s if s in valid else None


def map_update(s: str) -> str | None:
    if not s:
        return None
    s = s.strip()
    valid = {"Continuous", "Periodic Recent", "Periodic Moderate", "Periodic Stale", "Abandoned Static"}
    return s if s in valid else None


def build_records(category_key: str, excel_rows: list[dict], supp: dict[str, dict]) -> tuple[list[dict], list[dict]]:
    """Returns (records, discrepancies)."""
    records = []
    discrepancies = []
    supp_names = list(supp.keys())
    used_supp_names: set[str] = set()

    # Map Excel category strings to schema enum values
    excel_to_enum_category = {
        "Drug-centric": "Drug-centric",
        "Drug-related (indirect)": "Drug-related (indirect)",
        "auxiliary": "auxiliary",
    }

    for ex in excel_rows:
        name = ex.get("Name") or ""
        matched_supp_name = None
        match_method = "exact"
        annot = None

        if name in supp:
            matched_supp_name = name
            annot = supp[name]
        else:
            fm = fuzzy_match(name, supp_names)
            if fm:
                matched_supp_name = fm
                match_method = "fuzzy"
                annot = supp[fm]
                discrepancies.append({
                    "category": category_key,
                    "issue": "name_fuzzy_matched",
                    "excel_name": name,
                    "supp_name": fm,
                    "note": "Fuzzy-matched between Excel and Supplementary Table.",
                })
            else:
                match_method = "none"
                discrepancies.append({
                    "category": category_key,
                    "issue": "no_supp_annotation",
                    "excel_name": name,
                    "supp_name": None,
                    "note": "No matching record in Supplementary Table; annotation axes left null.",
                })

        if matched_supp_name:
            used_supp_names.add(matched_supp_name)

        # Decide whether annotations are authoritative
        # For drug_related and auxiliary, supp annotations are placeholder-ish per analysis;
        # we still store them but mark data_quality as needs_review if values look default.
        data_quality = "authoritative"
        if category_key in ("drug_related", "auxiliary"):
            # The supp tables for these are mostly defaults — flag for review
            if annot and annot.get("Pathway") == "RAG" and annot.get("Identifier") == "name only":
                data_quality = "needs_review"
        if match_method != "exact":
            data_quality = "needs_review"

        # Build the record
        rec = {
            "name": name,
            "category": excel_to_enum_category.get(ex.get("Category", ""), ex.get("Category", "")),
            "type": ex.get("Type"),
            "subcategory": ex.get("Subcategory") or (annot.get("Subcategory") if annot else None),
            "paradigm": ex.get("Paradigm"),
            "pathway": map_pathway(annot.get("Pathway")) if annot else None,
            "identifier": annot.get("Identifier") if annot else None,
            "access": map_access(annot.get("Access")) if annot else None,
            "license": None,  # Not in current data; placeholder for future enrichment
            "update_cadence": map_update(annot.get("Update")) if annot else None,
            "task_tags": [],  # Not in current data; future enrichment
            "aim": ex.get("Aim"),
            "source": ex.get("Source"),
            "description": ex.get("Description") or "",
            "link": ex.get("Link") or "",
            "paper_link": ex.get("Paper_Link"),
            "data_quality": data_quality,
            "notes": None,
        }

        # Strip Nones from optional fields to keep JSON clean
        records.append(rec)

    # Records in supp but not in Excel
    for supp_name in supp_names:
        if supp_name not in used_supp_names:
            discrepancies.append({
                "category": category_key,
                "issue": "supp_only",
                "excel_name": None,
                "supp_name": supp_name,
                "note": "Present in Supplementary Table but not in Excel; not included in registry.",
            })

    return records, discrepancies


def write_outputs(category_key: str, records: list[dict]) -> None:
    REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
    json_path = REGISTRY_DIR / f"{category_key}.json"
    tsv_path = REGISTRY_DIR / f"{category_key}.tsv"

    with json_path.open("w", encoding="utf-8") as fp:
        json.dump(records, fp, ensure_ascii=False, indent=2)
        fp.write("\n")

    # TSV with a stable column order
    columns = [
        "name", "category", "type", "subcategory", "paradigm",
        "pathway", "identifier", "access", "license", "update_cadence",
        "task_tags", "aim", "source", "description", "link", "paper_link",
        "data_quality", "notes",
    ]
    with tsv_path.open("w", encoding="utf-8", newline="") as fp:
        w = csv.writer(fp, delimiter="\t", quoting=csv.QUOTE_MINIMAL)
        w.writerow(columns)
        for r in records:
            row = []
            for c in columns:
                v = r.get(c)
                if isinstance(v, list):
                    row.append(";".join(v))
                elif v is None:
                    row.append("")
                else:
                    row.append(str(v))
            w.writerow(row)

    print(f"  wrote {json_path.relative_to(REPO_ROOT)} and {tsv_path.relative_to(REPO_ROOT)}: {len(records)} records")


def main() -> int:
    all_discrepancies: list[dict] = []
    summary: dict[str, dict] = {}

    for category_key, xl_path in EXCEL_FILES.items():
        if not xl_path.exists():
            print(f"MISSING: {xl_path}", file=sys.stderr)
            return 1
        print(f"\n[{category_key}]")
        excel_rows = load_excel_rows(xl_path)
        supp = load_supp_annotations(SUPP_DOCX, SUPP_TABLE_IDX[category_key])
        records, discrepancies = build_records(category_key, excel_rows, supp)
        write_outputs(category_key, records)
        all_discrepancies.extend(discrepancies)

        nq = sum(1 for r in records if r["data_quality"] == "needs_review")
        summary[category_key] = {
            "n_records": len(records),
            "n_excel": len(excel_rows),
            "n_supp": len(supp),
            "n_authoritative": len(records) - nq,
            "n_needs_review": nq,
        }

    # Write discrepancies report
    disc_path = REPO_ROOT / "docs" / "data_quality_report.md"
    disc_path.parent.mkdir(parents=True, exist_ok=True)
    with disc_path.open("w", encoding="utf-8") as fp:
        fp.write("# DR100 Data-Quality Report (v1.0 build)\n\n")
        fp.write("This report is auto-generated by `scripts/build_registry.py` and lists every\n")
        fp.write("naming or coverage discrepancy detected between the Excel base files and the\n")
        fp.write("annotations in the paper's Supplementary Tables S1-S3.\n\n")
        fp.write("## Build summary\n\n")
        fp.write("| Category | Records | Excel rows | Supp rows | Authoritative | Needs review |\n")
        fp.write("|---|---:|---:|---:|---:|---:|\n")
        for k, s in summary.items():
            fp.write(f"| {k} | {s['n_records']} | {s['n_excel']} | {s['n_supp']} | {s['n_authoritative']} | {s['n_needs_review']} |\n")
        fp.write("\n## Discrepancies\n\n")
        if not all_discrepancies:
            fp.write("None.\n")
        else:
            fp.write("| Category | Issue | Excel name | Supp name | Note |\n")
            fp.write("|---|---|---|---|---|\n")
            for d in all_discrepancies:
                fp.write(f"| {d['category']} | {d['issue']} | {d.get('excel_name') or '—'} | {d.get('supp_name') or '—'} | {d['note']} |\n")
    print(f"\nDiscrepancy report: {disc_path.relative_to(REPO_ROOT)}")
    print(f"Total discrepancies: {len(all_discrepancies)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
