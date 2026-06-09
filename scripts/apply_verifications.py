"""
Apply verification log to RIG CSV. Updates confidence + evidence_url for
edges that have been verified via Chrome browsing this round.

Source: main/rig_outputs/verify_logs/results.json
Target: main/rig_outputs/rig_edges_v1.csv  (in-place update)
Backup: main/rig_outputs/rig_edges_v1.csv.pre_verify.bak
"""
import csv, json, shutil
from pathlib import Path

LOG = Path.home() / "Desktop/DrugResource100/main/rig_outputs/verify_logs/results.json"
CSV = Path.home() / "Desktop/DrugResource100/main/rig_outputs/rig_edges_v1.csv"
BAK = Path(str(CSV) + ".pre_verify.bak")

shutil.copy(CSV, BAK)
print(f"Backup → {BAK.name}")

log = json.loads(LOG.read_text())
verifications = {(v["source"], v["target"], v["edge_type"]): v for v in log["verified_edges"]}
print(f"Loaded {len(verifications)} verification records")

# Update CSV
with open(CSV) as f:
    fieldnames = csv.DictReader(f).fieldnames
    f.seek(0)
    rows = list(csv.DictReader(f))

n_updated = 0
for r in rows:
    key = (r["source"], r["target"], r["edge_type"])
    if key in verifications:
        v = verifications[key]
        old_conf = r["confidence"]
        r["confidence"] = "high"
        r["evidence_url"] = v["evidence_url"]
        # Append note about quote if there's a notes column
        if "notes" in r:
            r["notes"] = (r.get("notes", "") + f" | Chrome verify: {v['evidence_quote'][:200]}").strip(" |")
        n_updated += 1
        if n_updated <= 5:
            print(f"  ✓ {r['source'][:25]} → {r['target'][:25]} ({r['edge_type']}) [{old_conf} → high]")

print(f"\nUpdated {n_updated} edges")

with open(CSV, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(rows)

# Verify new distribution
from collections import Counter
conf = Counter(r["confidence"] for r in rows)
print(f"\nNew confidence distribution: {dict(conf)}")
print(f"  high   : {conf.get('high', 0)} ({conf.get('high', 0)*100/len(rows):.0f}%)")
print(f"  medium : {conf.get('medium', 0)}")
print(f"  low    : {conf.get('low', 0)}")
