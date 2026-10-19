#!/usr/bin/env python3
"""reasoning_traces analysis: agreement, then the three pre-registered analyses, per stratum and
with Gemini alone (Amendment 2). Reads the artefacts and the two code files; computes
nothing the pre-registration does not name, and labels the one addition (counts of no
trace and uncoded beside every share) as bookkeeping.

  --handcheck-sheet   print the 30 hand-check traces WITHOUT the coders' codes, so the
                      hand coding is blind; writes the label list to compare later
  --handcheck FILE    JSON {label: {"R":..,"C":..,"S":..}} of the hand codes; compares
  (default)           agreement and analyses -> records/analysis.{json,md}
  --c-only            Amendment 4: R and S stopped, analyses on C alone ->
                      records/analysis_c.json; with --handcheck-sheet or
                      --handcheck, the hand check on C (A4.4)
"""
import argparse
import json
import os
import random
import statistics as st
import sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(R, "scripts"))
import code_reasoning_traces as CR
import read_reasoning_traces as RR

FULL = ("deepseek_r", "haiku_r")
SUMMARY = ("grok43_r", "gemini_r", "gpt6l_r", "gpt6s_r")
FLOOR = 0.70
KEYS = ("R", "C", "S")
HC_SEED, HC_PER = 2301, 15
GROUPS = (("full", FULL), ("summary", SUMMARY), ("gemini alone", ("gemini_r",)))


def ac1(pairs):
    """Gwet's AC1 for two raters on one binary code; pairs of 'yes'/'no'."""
    n = len(pairs)
    if not n:
        return None
    pa = sum(1 for a, b in pairs if a == b) / n
    pi = sum((a == "yes") + (b == "yes") for a, b in pairs) / (2 * n)
    pe = 2 * pi * (1 - pi)
    return 1.0 if pe == 1 else (pa - pe) / (1 - pe)


def load():
    trs = CR.traces()
    p1 = json.load(open(os.path.join(R, "records/reasoning_traces_CODES__primary.json")))
    p2 = json.load(open(os.path.join(R, "records/reasoning_traces_CODES__second.json")))
    for p in (p1, p2):
        if p["strata"] != {"full": list(FULL), "summary": list(SUMMARY)}:
            sys.exit(f"REFUSING: {p['coder']} codes were made under strata {p['strata']}")
    return trs, p1["codes"], p2["codes"]


def agreement(prim, sec):
    out = {}
    for gname, arms in GROUPS:
        labs = [l for l, v in sec.items() if v["arm"] in arms]
        both = [l for l in labs if not sec[l]["uncoded"] and l in prim
                and not prim[l]["uncoded"]]
        row = {"sampled": len(labs), "both_coded": len(both),
               "excluded_uncoded": len(labs) - len(both)}
        for k in KEYS:
            ps = [(prim[l]["codes"][k], sec[l]["codes"][k]) for l in both]
            row[k] = {"ac1": ac1(ps), "raw_agreement":
                      (sum(a == b for a, b in ps) / len(ps)) if ps else None,
                      "yes_primary": sum(a == "yes" for a, _ in ps),
                      "yes_second": sum(b == "yes" for _, b in ps)}
        out[gname] = row
    return out


def shares(trs, prim, arms, leg):
    """Shares of traces coded C and S, with every denominator."""
    draws = [t for t in trs if t["arm"] in arms and t["leg"] == leg]
    traced = [t for t in draws if t["trace"]]
    coded = [t for t in traced if not prim[t["label"]]["uncoded"]]
    n = len(coded)
    c = sum(prim[t["label"]]["codes"]["C"] == "yes" for t in coded)
    s = sum(prim[t["label"]]["codes"]["S"] == "yes" for t in coded)
    r = sum(prim[t["label"]]["codes"]["R"] == "yes" for t in coded)
    return {"draws": len(draws), "no_trace": len(draws) - len(traced),
            "uncoded": len(traced) - n, "coded": n,
            "C": c, "S": s, "R": r, "C_or_S": sum(
                prim[t["label"]]["codes"]["C"] == "yes" or
                prim[t["label"]]["codes"]["S"] == "yes" for t in coded),
            "share_C": c / n if n else None, "share_S": s / n if n else None,
            "share_R": r / n if n else None}


def score_split(trs, prim, arms):
    """Analysis 3: private traces coded C or S against neither, digit from the call."""
    coded = [t for t in trs if t["arm"] in arms and t["leg"] == "priv" and t["trace"]
             and not prim[t["label"]]["uncoded"] and t["digit"] is not None]
    yes = [t["digit"] for t in coded if prim[t["label"]]["codes"]["C"] == "yes"
           or prim[t["label"]]["codes"]["S"] == "yes"]
    no = [t["digit"] for t in coded if not (prim[t["label"]]["codes"]["C"] == "yes"
                                           or prim[t["label"]]["codes"]["S"] == "yes")]
    m = lambda xs: (sum(xs) / len(xs)) if xs else None
    return {"n_C_or_S": len(yes), "n_neither": len(no), "mean_C_or_S": m(yes),
            "mean_neither": m(no),
            "difference": (m(yes) - m(no)) if yes and no else None}


def handcheck_labels(trs, prim):
    """15 per stratum, round-robin over cells of the primary codes, Random(2301)."""
    rng = random.Random(HC_SEED)
    picked = []
    for _, arms in GROUPS[:2]:
        cells = {}
        for t in sorted((t for t in trs if t["arm"] in arms and t["trace"]),
                        key=lambda t: t["label"]):
            v = prim[t["label"]]
            key = "uncoded" if v["uncoded"] else "".join(v["codes"][k][0] for k in KEYS)
            cells.setdefault(key, []).append(t["label"])
        order = sorted(cells)
        for k in order:
            rng.shuffle(cells[k])
        got = []
        while len(got) < HC_PER and any(cells[k] for k in order):
            for k in order:
                if cells[k] and len(got) < HC_PER:
                    got.append(cells[k].pop())
        picked += got
    return picked


def c_shares(trs, prim, arms, leg):
    """Amendment 4, analyses 1 and 2: share of traces coded C, every denominator."""
    draws = [t for t in trs if t["arm"] in arms and t["leg"] == leg]
    traced = [t for t in draws if t["trace"]]
    coded = [t for t in traced if not prim[t["label"]]["uncoded"]]
    c = sum(prim[t["label"]]["codes"]["C"] == "yes" for t in coded)
    return {"draws": len(draws), "no_trace": len(draws) - len(traced),
            "uncoded": len(traced) - len(coded), "coded": len(coded), "C": c,
            "share_C": c / len(coded) if coded else None}


def c_split(trs, prim, arms):
    """Amendment 4, analysis 3: private traces coded C against not, digit from the call."""
    coded = [t for t in trs if t["arm"] in arms and t["leg"] == "priv" and t["trace"]
             and not prim[t["label"]]["uncoded"] and t["digit"] is not None]
    yes = [t["digit"] for t in coded if prim[t["label"]]["codes"]["C"] == "yes"]
    no = [t["digit"] for t in coded if prim[t["label"]]["codes"]["C"] != "yes"]
    m = lambda xs: (sum(xs) / len(xs)) if xs else None
    return {"n_C": len(yes), "n_not_C": len(no), "mean_C": m(yes), "mean_not_C": m(no),
            "difference": (m(yes) - m(no)) if yes and no else None}


def handcheck_labels_c(trs, prim, exclude):
    """A4.4: 15 per stratum, round-robin over the primary's C yes / C no, Random(2301),
    never a trace in `exclude` (already read with the codes visible)."""
    rng = random.Random(HC_SEED)
    picked = []
    for _, arms in GROUPS[:2]:
        cells = {"no": [], "yes": [], "uncoded": []}
        for t in sorted((t for t in trs if t["arm"] in arms and t["trace"]
                         and t["label"] not in exclude), key=lambda t: t["label"]):
            v = prim[t["label"]]
            cells["uncoded" if v["uncoded"] else v["codes"]["C"]].append(t["label"])
        order = sorted(k for k in cells if cells[k])
        for k in order:
            rng.shuffle(cells[k])
        got = []
        while len(got) < HC_PER and any(cells[k] for k in order):
            for k in order:
                if cells[k] and len(got) < HC_PER:
                    got.append(cells[k].pop())
        picked += got
    return picked


def c_only(a, trs, prim, sec, by):
    if a.handcheck_sheet:
        excl = {r["label"] for r in json.load(open(os.path.join(
            R, "records/disagreement_reading.json")))["rows"]}
        labs = handcheck_labels_c(trs, prim, excl)
        out = os.path.join(R, "records/handcheck_c_labels.json")
        if os.path.exists(out):
            sys.exit(f"REFUSING: {out} exists. Write-once, no override.")
        rng = random.Random(HC_SEED + 1)
        shown = labs[:]
        rng.shuffle(shown)                   # the sheet's order hides the strata
        json.dump(shown, open(out, "w"), indent=1)
        b = RR.banks()
        for i, l in enumerate(shown, 1):
            print(f"\n===== {i}\n{CR.user_message(b, by[l])}")
        return 0
    if a.handcheck:
        hand = json.load(open(a.handcheck))
        shown = json.load(open(os.path.join(R, "records/handcheck_c_labels.json")))
        if len(hand) != len(shown):
            sys.exit(f"REFUSING: {len(hand)} hand codes for {len(shown)} sheet items")
        rows, dis = [], []
        for i, l in enumerate(shown, 1):
            hc = hand[str(i)]
            v = prim[l]
            pc = None if v["uncoded"] else v["codes"]["C"]
            rows.append({"item": i, "label": l, "stratum": v["stratum"], "hand": hc["C"],
                         "primary": pc, "why": hc.get("why", "")})
            if pc != hc["C"]:
                dis.append(rows[-1])
        res = {"amendment": 4, "code": "C", "traces": len(rows),
               "agree": len(rows) - len(dis), "disagreements": dis, "rows": rows}
        out = os.path.join(R, "records/handcheck_c.json")
        if os.path.exists(out):
            sys.exit(f"REFUSING: {out} exists. Write-once, no override.")
        json.dump(res, open(out, "w"), indent=1)
        print(json.dumps({k: res[k] for k in ("traces", "agree", "disagreements")},
                         indent=1))
        return 0
    agr = agreement(prim, sec)
    if any(agr[g]["C"]["ac1"] is None or agr[g]["C"]["ac1"] < FLOOR
           for g in ("full", "summary")):
        sys.exit("REFUSING: C is below the floor; Amendment 4 does not apply")
    res = {"amendment": 4, "codes_stopped": {
        k: {g: {"ac1": agr[g][k]["ac1"], "yes_primary": agr[g][k]["yes_primary"],
                "yes_second": agr[g][k]["yes_second"]} for g, _ in GROUPS}
        for k in ("R", "S")},
        "C_agreement": {g: agr[g]["C"] for g, _ in GROUPS}, "floor": FLOOR,
        "analysis": {}}
    for gname, arms in GROUPS:
        g = {"private": c_shares(trs, prim, arms, "priv"),
             "professional": c_shares(trs, prim, arms, "pro"),
             "score_split": c_split(trs, prim, arms), "per_arm": {}, "per_pair": {}}
        for arm in arms:
            g["per_arm"][arm] = {"private": c_shares(trs, prim, (arm,), "priv"),
                                 "professional": c_shares(trs, prim, (arm,), "pro"),
                                 "score_split": c_split(trs, prim, (arm,))}
        for pair in RR.PAIRS:
            sub = [t for t in trs if t["pair"] == pair]
            g["per_pair"][pair] = {"private": c_shares(sub, prim, arms, "priv"),
                                   "professional": c_shares(sub, prim, arms, "pro")}
        sc = g["private"]["share_C"]
        g["prediction_1_C_under_one_fifth"] = None if sc is None else sc < 0.2
        d = g["score_split"]["difference"]
        g["prediction_3_lower_when_C"] = None if d is None else d < 0
        res["analysis"][gname] = g
    out = os.path.join(R, "records/analysis_c.json")
    if os.path.exists(out):
        sys.exit(f"REFUSING: {out} exists. Write-once, no override.")
    json.dump(res, open(out, "w"), indent=1)
    print(json.dumps({g: {"private": v["private"], "professional": v["professional"],
                          "score_split": v["score_split"]}
                      for g, v in res["analysis"].items()}, indent=1))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--handcheck-sheet", action="store_true")
    ap.add_argument("--handcheck", default=None)
    ap.add_argument("--c-only", action="store_true")
    a = ap.parse_args(argv)
    trs, prim, sec = load()
    by = {t["label"]: t for t in trs}
    if a.c_only:
        return c_only(a, trs, prim, sec, by)

    if a.handcheck_sheet:
        b = RR.banks()
        labs = handcheck_labels(trs, prim)
        json.dump(labs, open(os.path.join(R, "records/handcheck_labels.json"),
                             "w"), indent=1)
        for i, l in enumerate(labs, 1):
            print(f"\n===== {i}. {l}\n{CR.user_message(b, by[l])}")
        return 0

    if a.handcheck:
        hand = json.load(open(a.handcheck))
        dis = []
        for l, hc in hand.items():
            v = prim[l]
            pc = None if v["uncoded"] else v["codes"]
            for k in KEYS:
                if pc is None or pc[k] != hc[k]:
                    dis.append({"label": l, "code": k, "hand": hc[k],
                                "primary": None if pc is None else pc[k],
                                "reason": hc.get("why", {}).get(k, "")})
        print(json.dumps({"traces": len(hand), "code_decisions": 3 * len(hand),
                          "disagreements": dis}, indent=1))
        return 0

    agr = agreement(prim, sec)
    below = [(g, k, agr[g][k]["ac1"]) for g in ("full", "summary") for k in KEYS
             if agr[g][k]["ac1"] is None or agr[g][k]["ac1"] < FLOOR]
    res = {"agreement": agr, "floor": FLOOR, "below_floor": below}
    if below:
        res["stopped"] = "agreement below the 0.70 floor; analyses not run"
    else:
        res["analysis"] = {}
        for gname, arms in GROUPS:
            g = {"private": shares(trs, prim, arms, "priv"),
                 "professional": shares(trs, prim, arms, "pro"),
                 "score_split": score_split(trs, prim, arms),
                 "per_arm": {}, "per_pair": {}}
            for arm in arms:
                g["per_arm"][arm] = {"private": shares(trs, prim, (arm,), "priv"),
                                     "professional": shares(trs, prim, (arm,), "pro"),
                                     "score_split": score_split(trs, prim, (arm,))}
            for pair in RR.PAIRS:
                sub = [t for t in trs if t["pair"] == pair]
                g["per_pair"][pair] = {"private": shares(sub, prim, arms, "priv"),
                                       "professional": shares(sub, prim, arms, "pro")}
            sp = g["private"]
            g["prediction_1"] = {
                "C_under_one_fifth": sp["share_C"] is not None and sp["share_C"] < 0.2,
                "S_under_one_fifth": sp["share_S"] is not None and sp["share_S"] < 0.2}
            ss = g["score_split"]
            g["prediction_3_lower_when_C_or_S"] = (ss["difference"] < 0
                                                   if ss["difference"] is not None
                                                   else None)
            res["analysis"][gname] = g
    out = os.path.join(R, "records/analysis.json")
    if os.path.exists(out):
        sys.exit(f"REFUSING: {out} exists. Write-once, no override.")
    json.dump(res, open(out, "w"), indent=1)
    print(json.dumps({"agreement": agr, "below_floor": below}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
