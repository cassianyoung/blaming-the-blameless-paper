#!/usr/bin/env python3
"""reasoning_traces: re-read the duty test's SEPARATE condition on the six reasoning arms, text
kept. Pre-registered in `records/PREREG_reasoning_traces_TRACES.md` (Amendment 1).

Six arms x six reported pairs x two legs, BLAME, at the banked draw counts (10, 20 on
gpt6s_r): 840 draws. The harness keeps the full reasoning and answer text of every call
(`84b648d6`), so the log is the trace record; the artefact carries the scores and a
per-draw index into it.

**THE INSTRUMENT IS TAKEN FROM THE BANKED CALLS, NOT REBUILT FROM MEMORY.** For every
arm and cell the banked call log supplies the prompt hash and the wire (model, pinned
provider, max_tokens, logprobs, reasoning setting, temperature). The cell's prompt is
rebuilt from its frozen bank and frame and hashed exactly as the harness hashes it; **a
cell whose rebuilt prompt does not hash to the banked one is REFUSED before any call is
paid** (A1.2), and so is a cell whose banked calls disagree among themselves on prompt
or wire, or whose banked count is not the banked draw count.

Prompts: pairs 1, 3, 4, 5 from the duty_pairs duty bank, pair 7 from the duty_hair_dye bank,
prawns from the families bank (careless chef = pro, careless home cook = priv); all
three through frames' blame frame with the subject named Alaric, as banked.

Scores are parsed as duty_pairs parsed them: the expected value if logprobs came back,
else the first digit of `raw_text`, else void. The digit and the trace come from the
same call (A1.4).

  --check-only   build and hash every prompt and read every wire, no key, no call
"""
import argparse
import glob
import hashlib
import json
import os
import re
import sqlite3
import sys
import time

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(R, "scripts"))
import or_harness as OH

RUN = "230"
ARMS = ("deepseek_r", "haiku_r", "grok43_r", "gpt6l_r", "gpt6s_r", "gemini_r")
PAIRS = ("prawns", "1", "3", "4", "5", "7")
LEGS = ("pro", "priv")
DRAWS = {a: (20 if a == "gpt6s_r" else 10) for a in ARMS}

B225 = ("data/duty_bank/moral__duty__v1.jsonl",
        "b0ca3175775f9c1f13d87a7dbf25f82f02be627aabf349e5ddadbd4c44baa9d6")
B228 = ("data/duty_bank/moral__duty228__v1.jsonl",
        "1ac42d76dcf2ab18812cf721954c356d466241ad080017186c5d4f100e33c21b")
BFAM = ("data/families_bank/moral__families__v1.jsonl",
        "cb77f3cb50528b089e978f8cec1069baf293f41d803d7a5e8ad00afd136918e6")
FRAMES = ("records/frames.json",
          "ea34a1b8d0eed2c923b28e7a9df366bc11a543843c61d6a51ca0e2794ebeaa83")
PRAWNS_FAMILY = {"pro": "prawns_restaurant", "priv": "prawns_home"}

# ── WHERE EACH ARM'S PRAWNS BLAME CALLS WERE BANKED ──────────────────────────────
# The families pass, under the name each reading was banked as (`deepseek_r` is
# `deepseek_r_mt8192` there, probe_duty_pairs.SEP_ALIAS).
FAMILY_LOGS = {
    "deepseek_r": ("runs/deployed_scenarios/logs/or_deepseek_r_mt8192.jsonl", "deepseek_r_mt8192"),
    "gemini_r": ("runs/deployed_scenarios/logs/or_gemini_r.jsonl", "gemini_r"),
    "gpt6l_r": ("runs/deployed_scenarios/logs/or_gpt6l_r.jsonl", "gpt6l_r"),
    "gpt6s_r": ("runs/deployed_scenarios/logs/or_gpt6s_r.jsonl", "gpt6s_r"),
    "grok43_r": ("runs/deployed_scenarios/logs/or_grok43_r.jsonl", "grok43_r"),
    "haiku_r": ("runs/deployed_added_models/logs/or_haiku_r.jsonl", "haiku_r"),
}
# duty_pairs's `g1` batch is a 4-draw pre-launch batch on haiku_r, not the banked cell
EXCLUDED_BATCHES = ("runs/duty_pairs/logs/g1/",)
ATTEMPTS, BACKOFF = 4, (3, 8, 20)


def sha(t):
    return hashlib.sha256(t.encode()).hexdigest()


def prompt_hash(msgs):
    """Exactly or_harness's `prompt_sha256_16` for a chat call."""
    return hashlib.sha256(json.dumps(msgs).encode()).hexdigest()[:16]


def load_bank(path, want):
    p = os.path.join(R, path)
    got = hashlib.sha256(open(p, "rb").read()).hexdigest()
    if got != want:
        sys.exit(f"REFUSING: {path} is sha {got[:16]}, frozen at {want[:16]}")
    return [json.loads(l) for l in open(p) if l.strip()]


def banks():
    p = os.path.join(R, FRAMES[0])
    if hashlib.sha256(open(p, "rb").read()).hexdigest() != FRAMES[1]:
        sys.exit(f"REFUSING: {FRAMES[0]} is not the frozen frame file")
    fr = json.load(open(p))["blame"]
    out = {"frame": fr}
    for name, (path, want) in (("225", B225), ("228", B228), ("fam", BFAM)):
        rows = load_bank(path, want)
        for d in rows:
            k = "text" if "text" in d else ("item" if "item" in d else None)
            sk = "text_sha256" if "text_sha256" in d else "sha256"
            if k and sk in d and sha(d[k]) != d[sk]:
                sys.exit(f"REFUSING: {path} row {d.get('uid')} does not hash to its sha")
        out[name] = rows
    return out


def build_messages(b, pair, leg):
    """The chat messages for one cell, from its frozen bank and the blame frame."""
    if pair == "prawns":
        rows = [d for d in b["fam"] if d.get("family") == PRAWNS_FAMILY[leg]
                and d.get("role") == "C"]
        if len(rows) != 1:
            sys.exit(f"REFUSING: {len(rows)} families rows for prawns {leg}, want 1")
        text = rows[0]["text"]
    else:
        src = b["228"] if pair == "7" else b["225"]
        uid = f"DUTY{pair}_{leg.upper()}"
        rows = [d for d in src if d.get("uid") == uid]
        if len(rows) != 1:
            sys.exit(f"REFUSING: {len(rows)} bank rows for {uid}, want 1")
        text = rows[0]["text"]
    fr = b["frame"]
    return [{"role": "system", "content": fr["system"]},
            {"role": "user", "content": fr["body"].format(item=text, agent="Alaric")}]


def _wire(r):
    return {"model": r["model"], "provider": r["provider_asked"],
            "max_tokens": r["max_tokens"], "want_logprobs": bool(r["want_logprobs"]),
            "reasoning": r["reasoning_on_the_wire"], "temperature": r["temperature"]}


def banked_index():
    """{(arm, pair, leg): {'sha': set, 'wire': set of json, 'n': int, 'logs': set}}"""
    idx = {}

    def add(k, r, f):
        c = idx.setdefault(k, {"sha": set(), "wire": set(), "n": 0, "logs": set()})
        c["sha"].add(r["prompt_sha256_16"])
        c["wire"].add(json.dumps(_wire(r), sort_keys=True))
        c["n"] += 1
        c["logs"].add(os.path.relpath(f, R))

    for f in sorted(glob.glob(os.path.join(R, "runs/duty_pairs/logs/*/read.jsonl"))
                    + glob.glob(os.path.join(R, "runs/duty_hair_dye/logs/*/read.jsonl"))):
        if any(x in os.path.relpath(f, R) + "/" for x in EXCLUDED_BATCHES):
            continue
        for line in open(f):
            if not line.strip():
                continue
            r = json.loads(line)
            p = (r.get("label") or "").split("|")
            if len(p) < 5 or p[1] not in ARMS or p[2] != "sep":
                continue
            pair = p[3][1:]
            if (p[0] == "duty_pairs" and pair in ("1", "3", "4", "5")) or \
               (p[0] == "duty_hair_dye" and pair == "7"):
                add((p[1], pair, p[4].lower()), r, f)
    for arm, (rel, banked_as) in FAMILY_LOGS.items():
        f = os.path.join(R, rel)
        for line in open(f):
            if not line.strip():
                continue
            r = json.loads(line)
            for leg, fam in PRAWNS_FAMILY.items():
                if r.get("label") == f"{banked_as}|{fam}__C|BLAME":
                    add((arm, "prawns", leg), r, f)
    return idx


def plan(b, idx):
    """Every cell with its messages and wire, or the reason it is refused."""
    cells = []
    for arm in ARMS:
        for pair in PAIRS:
            for leg in LEGS:
                k = (arm, pair, leg)
                msgs = build_messages(b, pair, leg)
                h = prompt_hash(msgs)
                c = idx.get(k)
                why = None
                if c is None:
                    why = "no banked calls found for this cell"
                elif len(c["sha"]) != 1:
                    why = f"banked calls carry {len(c['sha'])} prompt hashes"
                elif len(c["wire"]) != 1:
                    why = f"banked calls carry {len(c['wire'])} wires"
                elif c["n"] != DRAWS[arm]:
                    why = f"banked count {c['n']} is not the banked draw count {DRAWS[arm]}"
                elif h not in c["sha"]:
                    why = f"rebuilt prompt hash {h} != banked {next(iter(c['sha']))}"
                cells.append({"arm": arm, "pair": pair, "leg": leg, "messages": msgs,
                              "prompt_sha256_16": h,
                              "wire": json.loads(next(iter(c["wire"]))) if c and
                              len(c["wire"]) == 1 else None,
                              "banked_logs": sorted(c["logs"]) if c else [],
                              "refused": why})
    return cells


def banked_means():
    con = sqlite3.connect(os.path.join(R, "results/results.sqlite"))
    return {(a, p, l): ev for a, p, l, ev in con.execute(
        "SELECT arm, pair_id, leg, ev FROM duty_reported WHERE question = 'BLAME' "
        "AND condition = 'bare'")}


def one_draw(h, w, msgs, label):
    errs = []
    for i in range(ATTEMPTS):
        try:
            return h.rate(w["model"], w["provider"], messages=msgs, mode="chat",
                          temperature=w["temperature"], max_tokens=w["max_tokens"],
                          want_logprobs=w["want_logprobs"], reasoning=w["reasoning"],
                          label=label), errs
        except SystemExit:
            raise
        except Exception as exc:
            errs.append(f"attempt {i + 1}: {repr(exc)[:160]}")
            if i < len(BACKOFF):
                time.sleep(BACKOFF[i])
    return None, errs


def digit(x):
    """duty_pairs's parse: ev, else the first digit of raw_text, else None."""
    if x.get("ev") is not None:
        return float(x["ev"])
    m = re.search(r"\d", x.get("raw_text") or "")
    return float(m.group(0)) if m else None


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--cap-usd", type=float, default=3.0)
    ap.add_argument("--outdir", default=os.path.join(R, "records"))
    ap.add_argument("--logdir", default=os.path.join(R, f"runs/run{RUN}/logs"))
    ap.add_argument("--check-only", action="store_true")
    a = ap.parse_args(argv)
    arms = [x.strip() for x in a.arms.split(",") if x.strip()]
    bad = [x for x in arms if x not in ARMS]
    if bad:
        sys.exit(f"REFUSING: not a reasoning_traces arm: {bad}")

    b = banks()
    cells = [c for c in plan(b, banked_index()) if c["arm"] in arms]
    ok = [c for c in cells if not c["refused"]]
    print(f"  {len(ok)} of {len(cells)} cells match their banked prompt and wire; "
          f"{sum(DRAWS[c['arm']] for c in ok)} draws")
    for c in cells:
        if c["refused"]:
            print(f"    REFUSED {c['arm']} {c['pair']} {c['leg']}: {c['refused']}")
    if a.check_only:
        return 0 if len(ok) == len(cells) else 1

    for arm in arms:
        p = os.path.join(a.outdir, f"RUN{RUN}_TRACES__{arm}.json")
        if os.path.exists(p):
            sys.exit(f"REFUSING: {p} exists. Write-once, no override.")
    os.makedirs(a.logdir, exist_ok=True)
    logp = os.path.join(a.logdir, "read.jsonl")
    h = OH.Harness(logp, cap_usd=a.cap_usd)
    banked = banked_means()
    for arm in arms:
        res = {"run": RUN, "arm": arm, "prereg": "records/PREREG_reasoning_traces_TRACES.md",
               "harness_keeps_text": True, "log": os.path.relpath(logp, R),
               "draws_per_cell": DRAWS[arm],
               "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "served_models": [], "served_providers": [], "cells": {}}
        served_m, served_p = set(), set()
        for c in (c for c in cells if c["arm"] == arm):
            key = f"{c['pair']}|{c['leg']}"
            if c["refused"]:
                res["cells"][key] = {"refused": c["refused"]}
                continue
            draws, errs = [], []
            for d in range(DRAWS[arm]):
                lab = f"run{RUN}|{arm}|sep|{c['pair']}|{c['leg'].upper()}|d{d + 1}"
                x, e = one_draw(h, c["wire"], c["messages"], lab)
                errs += [f"draw {d + 1}: {m}" for m in e]
                if x is None:
                    draws.append({"d": d + 1, "label": lab, "lost": True})
                    continue
                served_m.add(x.get("served_model"))
                served_p.add(x.get("provider_served"))
                draws.append({"d": d + 1, "label": lab, "ts": x["ts"],
                              "digit": digit(x), "reasoned": OH.reasoned(x),
                              "reasoning_text_len": x.get("reasoning_text_len"),
                              "reasoning_kinds": x.get("reasoning_kinds"),
                              "answer_len": len(x.get("answer_text") or ""),
                              "served_model": x.get("served_model"),
                              "provider_served": x.get("provider_served")})
            vals = [q["digit"] for q in draws if q.get("digit") is not None]
            bm = banked.get((arm, c["pair"], c["leg"]))
            mean = sum(vals) / len(vals) if vals else None
            res["cells"][key] = {
                "pair": c["pair"], "leg": c["leg"],
                "prompt_sha256_16": c["prompt_sha256_16"], "wire": c["wire"],
                "banked_logs": c["banked_logs"], "n_drawn": DRAWS[arm],
                "n_parsed": len(vals),
                "n_reasoned": sum(1 for q in draws if q.get("reasoned")),
                "n_with_text": sum(1 for q in draws if q.get("reasoning_text_len")),
                "mean": mean, "banked_mean": bm,
                "drift": (mean - bm) if (mean is not None and bm is not None) else None,
                "draws": draws, "errors": errs}
            print(f"    {arm:10s} {key:12s} {len(vals)}/{DRAWS[arm]}  mean "
                  f"{'-' if mean is None else format(mean, '.3f')}  banked "
                  f"{'-' if bm is None else format(bm, '.3f')}")
        res["served_models"] = sorted(map(str, served_m))
        res["served_providers"] = sorted(map(str, served_p))
        res["served_constant"] = len(served_m) <= 1 and len(served_p) <= 1
        res["calls_so_far"], res["spent_so_far_usd"] = h.calls, h.spent
        final = os.path.join(a.outdir, f"RUN{RUN}_TRACES__{arm}.json")
        if os.path.exists(final):
            sys.exit(f"REFUSING: {final} appeared during the read; not overwriting. "
                     f"The calls are in {logp}.")
        with open(final, "w") as fh:
            json.dump(res, fh, indent=1)
        print(f"    -> {os.path.relpath(final, R)}  served "
              f"{res['served_models']} via {res['served_providers']}")
    h.log.close()
    print(f"\n  {h.calls} calls, ${h.spent:.4f} spent (cap ${a.cap_usd})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
