#!/usr/bin/env python3
"""reasoning_traces coding: apply the frozen guide to every re-read trace.

Implements `records/coding_guide.md` (sha checked at start) and nothing it does
not say. One call per trace returns R, C and S (design A); temperature 0, reasoning off,
provider pinned; strict JSON, one retry, then uncoded and never defaulted. The coder sees
the case type, the case text and the trace: never the answer, the digit, the model or
the pair.

**THE STRATA ARE PASSED EXPLICITLY AND RECORDED.** The guide fixes the expected grouping
and lets the recorded `reasoning_kinds` correct it; which correction applies is a ruling,
so this script takes `--full` and `--summary` arm lists and writes them into every
output rather than inferring them.

  --coder primary   Qwen3-235B on every trace
  --coder second    Kimi-K3 on the 20% sample, random within each stratum
  --plan-only       list the traces, strata, sample and pre-pass; no key, no call
"""
import argparse
import glob
import hashlib
import json
import os
import random
import re
import sys
import time

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(R, "scripts"))
import or_harness as OH
import read_reasoning_traces as RR

GUIDE = "records/coding_guide.md"
GUIDE_SHA = "52c80dfc0bdedaa73982bf1ffe3fcee061327b5be7b0e816fc0bb0ceb6101322"
# Primary provider moved GMICloud -> Nebius by Amendment 3 (same model, same fp8
# quantisation): GMICloud, Parasail, DeepInfra, Venice and Google all returned
# upstream 429 on 2026-10-12; Nebius was the only endpoint answering.
CODERS = {"primary": ("qwen/qwen3-235b-a22b-2507", "Nebius"),
          "second": ("moonshotai/kimi-k3", "Sail Research")}
SAMPLE_SEED, SAMPLE_SHARE = 230, 0.2
KEYS, VALUES = ("R", "C", "S"), ("yes", "no")
KEYWORDS = ("professional", "tradesman", "electrician", "engineer", "chef", "cook",
            "hairdresser", "childminder", "nanny", "driver", "landlord", "plumber",
            "mechanic", "amateur", "layperson", "layman", "hobbyist", "friend", "host",
            "parent", "neighbour", "homeowner", "volunteer", "paid", "for a living",
            "qualified", "licensed", "certified", "trained", "standard", "duty",
            "expected of", "should have known", "reasonable person")
CJK = re.compile(r"[㐀-鿿豈-﫿]")


def coder_text():
    p = os.path.join(R, GUIDE)
    got = hashlib.sha256(open(p, "rb").read()).hexdigest()
    if got != GUIDE_SHA:
        sys.exit(f"REFUSING: {GUIDE} is sha {got[:16]}, frozen at {GUIDE_SHA[:16]}")
    t = open(p).read()
    a = t.index("## CODER INSTRUCTIONS (begin)") + len("## CODER INSTRUCTIONS (begin)")
    b = t.index("## CODER INSTRUCTIONS (end)")
    return t[a:b].strip()


def case_text(b, pair, leg):
    """The description the model was shown, before the question."""
    content = RR.build_messages(b, pair, leg)[1]["content"]
    suffix = b["frame"]["body"].format(item="", agent="Alaric")
    if not content.endswith(suffix):
        sys.exit(f"REFUSING: cannot strip the question from {pair} {leg}")
    return content[:-len(suffix)]


def traces(arts_dir=os.path.join(R, "records")):
    """Every reasoning_traces draw, with its trace text from the log (empty if none)."""
    out = []
    for p in sorted(glob.glob(os.path.join(arts_dir, "traces__*.json"))):
        art = json.load(open(p))
        log = {}
        for line in open(os.path.join(R, art["log"])):
            if line.strip():
                x = json.loads(line)
                log.setdefault(x["label"], []).append(x)
        for key, c in sorted(art["cells"].items()):
            if "refused" in c:
                continue
            for d in c["draws"]:
                if d.get("lost"):
                    continue
                recs = log.get(d["label"], [])
                if len(recs) != 1:
                    sys.exit(f"REFUSING: {len(recs)} log records for {d['label']}")
                x = recs[0]
                out.append({"label": d["label"], "arm": art["arm"], "pair": c["pair"],
                            "leg": c["leg"], "digit": d["digit"],
                            "kinds": x.get("reasoning_kinds") or [],
                            "trace": x.get("reasoning_text") or ""})
    return out


def prepass(t):
    if not t:
        return None
    if len(CJK.findall(t)) > 0.2 * len(t):
        return "UNREADABLE"
    low = t.lower()
    return sorted(k for k in KEYWORDS if re.search(r"\b" + re.escape(k) + r"\b", low))


def sample(trs, strata):
    """round(0.2 n) per stratum, random.Random(230) over the sorted labels."""
    picked = set()
    for name in ("full", "summary"):
        labs = sorted(t["label"] for t in trs if t["trace"] and t["arm"] in strata[name])
        k = round(SAMPLE_SHARE * len(labs))
        picked |= set(random.Random(SAMPLE_SEED).sample(labs, k))
    return picked


def user_message(b, t):
    return (f"CASE: {'PRIVATE' if t['leg'] == 'priv' else 'PROFESSIONAL'}\n\n"
            f"DESCRIPTION:\n{case_text(b, t['pair'], t['leg'])}\n\n"
            f"REASONING:\n{t['trace']}")


def validate(raw):
    """The three codes, or None. Exactly R, C, S, each 'yes' or 'no'; nothing else."""
    try:
        d = json.loads((raw or "").strip())
    except ValueError:
        return None
    if not isinstance(d, dict) or set(d) != set(KEYS):
        return None
    if any(d[k] not in VALUES for k in KEYS):
        return None
    return {k: d[k] for k in KEYS}


def code_one(h, model, provider, msgs, label):
    attempts = []
    for i in range(2):                       # the call, and ONE retry
        try:
            x = h.rate(model, provider, messages=msgs, mode="chat", temperature=0.0,
                       max_tokens=40, want_logprobs=False, reasoning_off=True,
                       label=f"{label}|try{i + 1}")
        except SystemExit:
            raise
        except Exception as exc:
            attempts.append({"error": repr(exc)[:160]})
            continue
        codes = validate(x.get("answer_text"))
        attempts.append({"answer": (x.get("answer_text") or "")[:200],
                         "valid": codes is not None, "temperature": x["temperature"]})
        if codes is not None:
            return codes, attempts
    return None, attempts


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--coder", choices=tuple(CODERS), required=True)
    ap.add_argument("--full", required=True, help="arms in the full-trace stratum")
    ap.add_argument("--summary", required=True, help="arms in the summary stratum")
    ap.add_argument("--cap-usd", type=float, default=1.0)
    ap.add_argument("--outdir", default=os.path.join(R, "records"))
    ap.add_argument("--artsdir", default=os.path.join(R, "records"))
    ap.add_argument("--logdir", default=None)
    ap.add_argument("--plan-only", action="store_true")
    a = ap.parse_args(argv)
    strata = {"full": [x for x in a.full.split(",") if x],
              "summary": [x for x in a.summary.split(",") if x]}
    if set(strata["full"]) & set(strata["summary"]):
        sys.exit("REFUSING: an arm is in both strata")
    system = coder_text()
    b = RR.banks()
    trs = traces(a.artsdir)
    arms_seen = sorted({t["arm"] for t in trs})
    unplaced = [x for x in arms_seen if x not in strata["full"] + strata["summary"]]
    if unplaced:
        sys.exit(f"REFUSING: arms in no stratum: {unplaced}")
    picked = sample(trs, strata)
    todo = [t for t in trs if t["trace"] and
            (a.coder == "primary" or t["label"] in picked)]
    for name in ("full", "summary"):
        n_all = sum(1 for t in trs if t["arm"] in strata[name])
        n_txt = sum(1 for t in trs if t["arm"] in strata[name] and t["trace"])
        n_smp = sum(1 for t in trs if t["arm"] in strata[name] and t["label"] in picked)
        print(f"  {name:8s} {n_txt} traces of {n_all} draws ({n_all - n_txt} no trace); "
              f"second-coder sample {n_smp}")
    print(f"  {a.coder}: {len(todo)} traces to code")
    if a.plan_only:
        return 0

    model, provider = CODERS[a.coder]
    out_p = os.path.join(a.outdir, f"codes__{a.coder}.json")
    if os.path.exists(out_p):
        sys.exit(f"REFUSING: {out_p} exists. Write-once, no override.")
    logdir = a.logdir or os.path.join(R, f"runs/reasoning_traces/coding/{a.coder}")
    os.makedirs(logdir, exist_ok=True)
    h = OH.Harness(os.path.join(logdir, "read.jsonl"), cap_usd=a.cap_usd)
    res = {"run": "230", "coder": a.coder, "model": model, "provider": provider,
           "guide": GUIDE, "guide_sha256": GUIDE_SHA, "temperature": 0.0,
           "strata": strata, "sample_seed": SAMPLE_SEED, "sample_share": SAMPLE_SHARE,
           "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "codes": {}}
    for t in todo:
        msgs = [{"role": "system", "content": system},
                {"role": "user", "content": user_message(b, t)}]
        codes, att = code_one(h, model, provider, msgs, f"reasoning_traces_code|{a.coder}|{t['label']}")
        res["codes"][t["label"]] = {
            "arm": t["arm"], "pair": t["pair"], "leg": t["leg"],
            "stratum": "full" if t["arm"] in strata["full"] else "summary",
            "codes": codes, "uncoded": codes is None, "attempts": att,
            "prepass": prepass(t["trace"])}
    res["n_coded"] = sum(1 for v in res["codes"].values() if not v["uncoded"])
    res["n_uncoded"] = sum(1 for v in res["codes"].values() if v["uncoded"])
    res["calls"], res["spent_usd"] = h.calls, h.spent
    if os.path.exists(out_p):
        sys.exit(f"REFUSING: {out_p} appeared during coding; not overwriting.")
    with open(out_p, "w") as fh:
        json.dump(res, fh, indent=1)
    h.log.close()
    print(f"  coded {res['n_coded']}, uncoded {res['n_uncoded']}; {h.calls} calls, "
          f"${h.spent:.4f} -> {os.path.relpath(out_p, R)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
