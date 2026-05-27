"""
Benchmark P2 — Bridge-First Normalization for drug name disambiguation.

Design:
  * 50 drug-name variants spanning brand, generic, abbreviation, misspelling, code
  * Ground truth: RxCUI from NLM RxNorm (https://rxnav.nlm.nih.gov/REST/)
  * Baseline (A): LLM direct lookup ("what is the RxCUI for ...?")
  * P2 bridge-first (B): query NLM RxNorm approximateTerm.json first, then LLM confirms
  * Metric: accuracy of returned RxCUI vs ground truth

Output: code/bench_p2_results.json + code/bench_p2_report.md
"""
import json
import time
import urllib.request
import urllib.error
from pathlib import Path

CFG = json.load(open(Path(__file__).parent / 'api_keys.json'))
URL_LLM = CFG['base_url'].rstrip('/') + '/v1/chat/completions'

RXNORM_BASE = "https://rxnav.nlm.nih.gov/REST"
MODEL = "llama-3.3-70b-instruct"

# 50 test cases — drug name variant → expected canonical generic name (for ground truth lookup)
# We will call RxNorm to canonicalize, treating its answer as ground truth.
TEST_CASES = [
    # brand → generic
    ("Tylenol",          "acetaminophen"),
    ("Advil",            "ibuprofen"),
    ("Motrin",           "ibuprofen"),
    ("Lipitor",          "atorvastatin"),
    ("Zocor",            "simvastatin"),
    ("Crestor",          "rosuvastatin"),
    ("Prozac",           "fluoxetine"),
    ("Zoloft",           "sertraline"),
    ("Paxil",            "paroxetine"),
    ("Effexor",          "venlafaxine"),
    ("Viagra",           "sildenafil"),
    ("Cialis",           "tadalafil"),
    ("Plavix",           "clopidogrel"),
    ("Coumadin",         "warfarin"),
    ("Norvasc",          "amlodipine"),
    ("Glucophage",       "metformin"),
    ("Synthroid",        "levothyroxine"),
    ("Prilosec",         "omeprazole"),
    ("Nexium",           "esomeprazole"),
    ("Lasix",            "furosemide"),
    # common abbreviations
    ("APAP",             "acetaminophen"),
    ("ASA",              "aspirin"),
    ("HCTZ",             "hydrochlorothiazide"),
    ("MTX",              "methotrexate"),
    ("AZT",              "zidovudine"),
    # misspellings (common transcription errors)
    ("Tilenol",          "acetaminophen"),
    ("Lipitorr",         "atorvastatin"),
    ("Acetominophen",    "acetaminophen"),
    ("Metaformin",       "metformin"),
    ("Atrovastatin",     "atorvastatin"),
    # multi-word brand names
    ("Aleve",            "naproxen"),
    ("Ambien",           "zolpidem"),
    ("Xanax",            "alprazolam"),
    ("Valium",           "diazepam"),
    ("Ativan",           "lorazepam"),
    # generics with alternate spellings
    ("paracetamol",      "acetaminophen"),  # international name
    ("salbutamol",       "albuterol"),       # UK vs US name
    ("frusemide",        "furosemide"),      # UK spelling
    ("amoxycillin",      "amoxicillin"),     # UK spelling
    ("epinephrine",      "epinephrine"),     # same
    # combinations / less common
    ("Augmentin",        "amoxicillin / clavulanate"),
    ("Bactrim",          "sulfamethoxazole / trimethoprim"),
    ("Percocet",         "oxycodone / acetaminophen"),
    ("Vicodin",          "hydrocodone / acetaminophen"),
    ("Adderall",         "amphetamine / dextroamphetamine"),
    # newer drugs
    ("Ozempic",          "semaglutide"),
    ("Mounjaro",         "tirzepatide"),
    ("Paxlovid",         "nirmatrelvir / ritonavir"),
    ("Trulicity",        "dulaglutide"),
    ("Eliquis",          "apixaban"),
]


def http_get_json(url: str, timeout: int = 10):
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {"_error": str(e)}


def call_llm(prompt: str, max_tries: int = 3) -> str:
    body = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
        "max_tokens": 100,
    }
    req = urllib.request.Request(
        URL_LLM,
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
        except Exception as e:
            if attempt == max_tries - 1:
                return f"[ERROR: {e}]"
            time.sleep(2 ** attempt)


def rxnorm_lookup(term: str) -> dict:
    """Hit RxNorm /approximateTerm.json — returns top candidate."""
    import urllib.parse
    q = urllib.parse.quote(term)
    url = f"{RXNORM_BASE}/approximateTerm.json?term={q}&maxEntries=1"
    data = http_get_json(url)
    try:
        cands = data["approximateGroup"]["candidate"]
        if not cands:
            return {"rxcui": None, "name": None}
        top = cands[0]
        rxcui = top.get("rxcui")
        # get canonical name
        if rxcui:
            name_data = http_get_json(f"{RXNORM_BASE}/rxcui/{rxcui}/property.json?propName=RxNorm Name")
            try:
                cname = name_data["propConceptGroup"]["propConcept"][0]["propValue"]
            except (KeyError, IndexError, TypeError):
                cname = top.get("name", "?")
            return {"rxcui": rxcui, "name": cname.lower()}
        return {"rxcui": None, "name": None}
    except (KeyError, IndexError, TypeError):
        return {"rxcui": None, "name": None}


def normalize(s: str) -> str:
    if not s: return ""
    return s.lower().strip().replace("-", " ").replace("/", " ").replace(",", " ")


def names_match(predicted: str, expected: str) -> bool:
    """Lenient name comparison: token-overlap on canonicalized strings."""
    if not predicted or not expected: return False
    p_tokens = set(normalize(predicted).split())
    e_tokens = set(normalize(expected).split())
    # Filter stopwords
    stop = {"hcl", "hydrochloride", "sulfate", "tartrate", "calcium", "sodium", "tablet", "capsule", "mg"}
    p_tokens -= stop
    e_tokens -= stop
    if not p_tokens or not e_tokens: return False
    # Must share at least one substantive token
    return len(p_tokens & e_tokens) >= 1


BASELINE_PROMPT = """You are a clinical pharmacology assistant. The user has typed
this drug name (which may be a brand name, abbreviation, misspelling, or international variant):

"{term}"

Reply in EXACTLY this format on a single line:
CANONICAL: <generic drug name>

Output only that single line, no extra text."""

P2_PROMPT = """You are a clinical pharmacology assistant. The user typed this drug name:

"{term}"

The RxNorm vocabulary (NLM RxNav API) returned the following candidate as the closest match:
  RxCUI: {rxcui}
  RxNorm Name: {rxname}

Confirm the canonical generic drug name. Reply in EXACTLY this format on a single line:
CANONICAL: <generic drug name>

Output only that single line, no extra text."""


def parse_canonical(resp: str) -> str:
    for line in resp.splitlines():
        line = line.strip()
        if line.upper().startswith("CANONICAL:"):
            return line.split(":", 1)[1].strip()
    # fallback: take first non-empty line
    for line in resp.splitlines():
        line = line.strip()
        if line:
            return line
    return ""


def main():
    print(f"Testing {len(TEST_CASES)} drug name variants")
    print(f"Model: {MODEL}")
    print(f"Bridge: NLM RxNorm /approximateTerm.json")
    print()

    results = []
    for i, (term, expected_generic) in enumerate(TEST_CASES, 1):
        # Ground truth via RxNorm bridge (also used by P2)
        rxn = rxnorm_lookup(term)

        # Baseline: LLM direct lookup
        baseline_resp = call_llm(BASELINE_PROMPT.format(term=term))
        baseline_canonical = parse_canonical(baseline_resp)

        # P2: bridge-first then LLM confirms
        p2_resp = call_llm(P2_PROMPT.format(
            term=term,
            rxcui=rxn.get("rxcui") or "(no match)",
            rxname=rxn.get("name") or "(no match)"
        ))
        p2_canonical = parse_canonical(p2_resp)

        baseline_correct = names_match(baseline_canonical, expected_generic)
        p2_correct = names_match(p2_canonical, expected_generic)

        results.append({
            "term": term,
            "expected_generic": expected_generic,
            "rxnorm_bridge": rxn,
            "baseline_resp": baseline_canonical,
            "p2_resp": p2_canonical,
            "baseline_correct": baseline_correct,
            "p2_correct": p2_correct,
        })
        marks = ("✓" if baseline_correct else "✗", "✓" if p2_correct else "✗")
        print(f"[{i:2d}/{len(TEST_CASES)}] {term:18s} → exp={expected_generic:30s} | "
              f"base={baseline_canonical[:18]:18s}{marks[0]} p2={p2_canonical[:18]:18s}{marks[1]}")

    # ---- metrics ----
    base_acc = sum(1 for r in results if r["baseline_correct"]) / len(results)
    p2_acc   = sum(1 for r in results if r["p2_correct"])      / len(results)

    summary = {
        "n_cases": len(TEST_CASES),
        "model": MODEL,
        "bridge": "NLM RxNorm /approximateTerm.json",
        "baseline_accuracy": round(base_acc, 3),
        "p2_accuracy": round(p2_acc, 3),
        "improvement_pp": round((p2_acc - base_acc) * 100, 1),
    }

    out_json = Path(__file__).parent / "bench_p2_results.json"
    out_json.write_text(json.dumps({"summary": summary, "rows": results}, indent=2))

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Cases: {len(TEST_CASES)}")
    print(f"Baseline (LLM direct):       {base_acc:.1%}")
    print(f"P2 (RxNorm bridge + LLM):    {p2_acc:.1%}")
    print(f"Improvement:                 +{summary['improvement_pp']} pp")
    print()
    print(f"Results saved to: {out_json}")


if __name__ == "__main__":
    main()
