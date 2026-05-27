"""
Benchmark P1 — Triangulated Consensus for DDI severity classification.

Design:
  * 30 known DDI pairs (positive cases, clinically validated severity)
  * 10 control pairs (no interaction expected)
  * Baseline (A): single model (llama-3.3-70b)
  * P1 consensus (B): three models majority vote (llama-3.3-70b + gpt-oss-120b + gemma-3-27b-it)
  * Metrics: recall, precision, F1, severity-classification accuracy

Output: code/bench_p1_results.json + code/bench_p1_report.md
"""
import json
import time
import urllib.request
import urllib.error
from pathlib import Path
from collections import Counter

CFG = json.load(open(Path(__file__).parent / 'api_keys.json'))
URL = CFG['base_url'].rstrip('/') + '/v1/chat/completions'

# ---------------------------------------------------------------------------
# Test cases — 30 positive DDIs + 10 controls
# Severity labels: "Major" | "Moderate" | "Minor" | "None"
# Sources: standard pharmacology references (Lexi-Comp, Stockley's Drug Interactions,
#          FDA labeling, BNF). All pairs are clinically established.
# ---------------------------------------------------------------------------
POSITIVE_DDIS = [
    ("warfarin", "aspirin", "Major", "additive bleeding risk"),
    ("warfarin", "ibuprofen", "Major", "additive bleeding, displacement"),
    ("warfarin", "amiodarone", "Major", "CYP2C9 inhibition → INR rise"),
    ("warfarin", "ciprofloxacin", "Moderate", "CYP inhibition → INR rise"),
    ("simvastatin", "clarithromycin", "Major", "CYP3A4 inhibition → rhabdomyolysis"),
    ("simvastatin", "cyclosporine", "Major", "OATP1B1/CYP3A4 → myopathy"),
    ("methotrexate", "trimethoprim", "Major", "additive antifolate → toxicity"),
    ("sildenafil", "nitroglycerin", "Major", "contraindicated; severe hypotension"),
    ("phenelzine", "fluoxetine", "Major", "MAOI + SSRI → serotonin syndrome"),
    ("linezolid", "sertraline", "Major", "MAOI activity + SSRI → serotonin syndrome"),
    ("digoxin", "verapamil", "Major", "P-gp inhibition → digoxin toxicity"),
    ("lithium", "lisinopril", "Moderate", "decreased Li clearance → toxicity"),
    ("lithium", "hydrochlorothiazide", "Major", "decreased Li clearance"),
    ("lithium", "ibuprofen", "Moderate", "decreased Li clearance"),
    ("allopurinol", "azathioprine", "Major", "XO inhibition → 6-MP toxicity"),
    ("carbamazepine", "ethinylestradiol", "Moderate", "CYP3A4 induction → OC failure"),
    ("theophylline", "ciprofloxacin", "Major", "CYP1A2 inhibition"),
    ("clopidogrel", "omeprazole", "Moderate", "CYP2C19 inhibition reduces active metabolite"),
    ("phenytoin", "fluconazole", "Major", "CYP2C9 inhibition → phenytoin toxicity"),
    ("tetracycline", "calcium carbonate", "Moderate", "chelation reduces absorption"),
    ("propranolol", "verapamil", "Major", "additive bradycardia / AV block"),
    ("sumatriptan", "ergotamine", "Major", "additive vasoconstriction"),
    ("disulfiram", "ethanol", "Major", "acetaldehyde accumulation"),
    ("levodopa", "pyridoxine", "Major", "peripheral DOPA decarboxylase activation"),
    ("cimetidine", "theophylline", "Moderate", "CYP1A2 inhibition"),
    ("erythromycin", "carbamazepine", "Major", "CYP3A4 inhibition"),
    ("furosemide", "lithium", "Major", "reduced Li clearance"),
    ("phenelzine", "tyramine", "Major", "MAOI + tyramine → hypertensive crisis"),
    ("metoprolol", "diltiazem", "Major", "additive negative chronotropy"),
    ("rifampin", "warfarin", "Major", "CYP induction → reduced anticoag effect"),
]

CONTROL_PAIRS = [  # expected: None / no clinically significant interaction
    ("acetaminophen", "vitamin c", "None"),
    ("loratadine", "calcium carbonate", "None"),
    ("amoxicillin", "ibuprofen", "None"),
    ("metformin", "loratadine", "None"),
    ("levothyroxine", "vitamin d", "None"),
    ("cetirizine", "atorvastatin", "None"),
    ("omeprazole", "loratadine", "None"),
    ("famotidine", "acetaminophen", "None"),
    ("docusate", "ibuprofen", "None"),
    ("multivitamin", "saline", "None"),
]

MODELS = {
    "llama70b": "llama-3.3-70b-instruct",
    "llama8b":  "llama-3.1-8b-instruct",
    "gemma":    "gemma-3-27b-it",
    # gpt-oss-120b also available; we use llama70b + llama8b + gemma for diversity
}

# ---------------------------------------------------------------------------

def call_llm(model: str, prompt: str, max_tries: int = 3) -> str:
    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,  # deterministic for reproducibility
        "max_tokens": 200,
    }
    req = urllib.request.Request(
        URL,
        data=json.dumps(body).encode('utf-8'),
        headers={
            'Authorization': f"Bearer {CFG['api_key']}",
            'Content-Type': 'application/json',
        },
    )
    for attempt in range(max_tries):
        try:
            with urllib.request.urlopen(req, timeout=CFG['timeout']) as resp:
                data = json.loads(resp.read())
                return data['choices'][0]['message']['content'].strip()
        except (urllib.error.URLError, KeyError, ValueError) as e:
            if attempt == max_tries - 1:
                return f"[ERROR after {max_tries} tries: {e}]"
            time.sleep(2 ** attempt)


PROMPT_TEMPLATE = """You are a clinical pharmacology assistant. Classify the
interaction severity of the following drug pair:

Drug A: {a}
Drug B: {b}

Respond with EXACTLY ONE line in this format:
SEVERITY: <Major|Moderate|Minor|None>

where:
- Major = potentially life-threatening, generally contraindicated
- Moderate = clinically significant, requires monitoring or dose adjustment
- Minor = limited clinical significance
- None = no documented interaction

Output only that single line, nothing else."""


def parse_severity(response: str) -> str:
    text = response.upper()
    for level in ("MAJOR", "MODERATE", "MINOR", "NONE"):
        if f"SEVERITY: {level}" in text:
            return level.capitalize() if level != "NONE" else "None"
    # fallback: search anywhere
    for level in ("MAJOR", "MODERATE", "MINOR", "NONE"):
        if level in text:
            return level.capitalize() if level != "NONE" else "None"
    return "?"


def majority_vote(votes: list) -> str:
    # If all three disagree, prefer the more conservative (more severe) call
    counts = Counter(v for v in votes if v != "?")
    if not counts:
        return "?"
    top, freq = counts.most_common(1)[0]
    if freq >= 2:
        return top
    # All three different — pick most conservative
    severity_rank = {"Major": 3, "Moderate": 2, "Minor": 1, "None": 0}
    return max(counts, key=lambda v: severity_rank.get(v, -1))


# ---------------------------------------------------------------------------

def main():
    pairs = [(a, b, sev) for a, b, sev, _ in POSITIVE_DDIS] + [(a, b, sev) for a, b, sev in CONTROL_PAIRS]
    print(f"Testing {len(pairs)} drug pairs ({len(POSITIVE_DDIS)} positive + {len(CONTROL_PAIRS)} control)")
    print(f"Models: {list(MODELS.values())}")
    print()

    results = []
    for i, (a, b, expected) in enumerate(pairs, 1):
        prompt = PROMPT_TEMPLATE.format(a=a, b=b)
        votes = {}
        for label, model in MODELS.items():
            t0 = time.time()
            resp = call_llm(model, prompt)
            sev = parse_severity(resp)
            votes[label] = {"sev": sev, "raw": resp[:80], "ms": int((time.time() - t0) * 1000)}
        baseline = votes["llama70b"]["sev"]
        consensus = majority_vote([v["sev"] for v in votes.values()])
        is_interaction_baseline = baseline != "None" and baseline != "?"
        is_interaction_consensus = consensus != "None" and consensus != "?"
        expected_is_interaction = expected != "None"
        results.append({
            "pair": f"{a} + {b}",
            "expected_severity": expected,
            "expected_interaction": expected_is_interaction,
            "votes": votes,
            "baseline_severity": baseline,
            "consensus_severity": consensus,
            "baseline_correct_severity": baseline == expected,
            "consensus_correct_severity": consensus == expected,
            "baseline_detected_interaction": is_interaction_baseline,
            "consensus_detected_interaction": is_interaction_consensus,
        })
        marks = (
            ("✓" if is_interaction_baseline == expected_is_interaction else "✗"),
            ("✓" if is_interaction_consensus == expected_is_interaction else "✗"),
        )
        print(f"[{i:2d}/{len(pairs)}] {a:15s} + {b:18s} | exp={expected:9s} | "
              f"base={baseline:9s}{marks[0]} cons={consensus:9s}{marks[1]} "
              f"[{','.join(v['sev'][:3] for v in votes.values())}]")

    # --- metrics ---
    def metrics(rows, key):
        tp = sum(1 for r in rows if r[key] and r["expected_interaction"])
        fp = sum(1 for r in rows if r[key] and not r["expected_interaction"])
        fn = sum(1 for r in rows if not r[key] and r["expected_interaction"])
        tn = sum(1 for r in rows if not r[key] and not r["expected_interaction"])
        prec = tp / (tp + fp) if (tp + fp) else 0
        rec  = tp / (tp + fn) if (tp + fn) else 0
        f1   = 2 * prec * rec / (prec + rec) if (prec + rec) else 0
        return {"tp": tp, "fp": fp, "fn": fn, "tn": tn,
                "precision": round(prec, 3), "recall": round(rec, 3), "f1": round(f1, 3)}

    sev_acc = lambda rows, key: sum(1 for r in rows if r[key]) / len(rows)

    summary = {
        "n_pairs": len(pairs),
        "n_positive": len(POSITIVE_DDIS),
        "n_control": len(CONTROL_PAIRS),
        "models": MODELS,
        "baseline_interaction_metrics": metrics(results, "baseline_detected_interaction"),
        "consensus_interaction_metrics": metrics(results, "consensus_detected_interaction"),
        "baseline_severity_accuracy": round(sev_acc(results, "baseline_correct_severity"), 3),
        "consensus_severity_accuracy": round(sev_acc(results, "consensus_correct_severity"), 3),
    }

    out_json = Path(__file__).parent / "bench_p1_results.json"
    out_json.write_text(json.dumps({"summary": summary, "rows": results}, indent=2))

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Pairs: {len(pairs)} ({len(POSITIVE_DDIS)} positive + {len(CONTROL_PAIRS)} control)")
    print()
    print("Detection (interaction yes/no):")
    print(f"  Baseline (single llama-3.3-70b): {summary['baseline_interaction_metrics']}")
    print(f"  Consensus (3-model majority):    {summary['consensus_interaction_metrics']}")
    print()
    print("Severity classification accuracy:")
    print(f"  Baseline: {summary['baseline_severity_accuracy']:.1%}")
    print(f"  Consensus: {summary['consensus_severity_accuracy']:.1%}")
    print()
    print(f"Results saved to: {out_json}")


if __name__ == "__main__":
    main()
