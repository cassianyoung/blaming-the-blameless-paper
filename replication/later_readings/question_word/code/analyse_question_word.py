"""analyse_question_word.py : the question-word test, on CPU, from question_word's artefacts.

    python3 scripts/analyse_question_word.py                    # runs/question_word -> records/result.json
    python3 scripts/analyse_question_word.py --run question_word_dry --out -   # dry-run artefacts, print only

Discovery mode: nothing here is registered and nothing enters the manuscript.

EVERY DEFINITION IS THE PROGRAMME'S OWN, CALLED, NOT RE-WRITTEN (results_derive):
  band      2.33 x pstdev over the five orderings, mean over P0, P1, BYSTANDER
  gate      (C - N) >= 3.0 bands AND min answer mass >= 0.70 over the scenario's orderings
  position  (P0 - N) / (C - N), on each wording's OWN anchors
  pooled    sqrt((b_blame^2 + b_wording^2) / 2), §3.4's band for a difference

Per arm x scenario x wording: N, C, I, P0 means; band; C - N in bands; answer mass;
verdict; P0 position; (P0 - N) / band. Against blame, for at_fault and responsible:
the change in P0 position, and the change in N, C, I and (P0 - N), each in pooled bands.
Counts: scenarios with (P0 - N) > 1 band, of those LICENSED, per wording.

THE BLAME RE-READ IS ALSO A REPRODUCTION: every blame cell's ev is compared with run
223's banked ev for the same (arm, scenario, role, ordering), and the largest absolute
difference is reported per arm.
"""
import argparse
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import results_derive as D                                        # noqa: E402

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARMS = ["llama31_base", "mistral_base", "qwen3_base", "olmo2_base", "falcon3_base",
        "gemma9_base"]
FAMS = ["bicycle", "cheque", "ladder", "prawns_home", "prawns_restaurant",
        "scaffolding"]
WORDINGS = ["blame", "at_fault", "responsible"]
VARIANTS = ["at_fault", "responsible"]


def load(path):
    if not os.path.exists(path):
        return None
    d = json.load(open(path))
    by_role, mass = {}, []
    for k, c in d["cells"].items():
        role, ch, fid = k.split("|")
        if ch != "BLAME" or c.get("void") or c.get("ev") is None:
            continue
        by_role.setdefault(role, {})[fid] = c["ev"]
        if c.get("answer_mass") is not None:
            mass.append(c["answer_mass"])
    return by_role, (min(mass) if mass else None)


def cell(by_role, amass):
    m = {r: D.mean(list(v.values())) for r, v in by_role.items()}
    bd = D.band({r: list(v.values()) for r, v in by_role.items()})
    n, c, i, p0 = (m.get(x) for x in ("N", "C", "I", "P0"))
    cn = (c - n) / bd if (bd and None not in (c, n)) else None
    verdict, _ = D.completion_gate(cn, amass)
    pos = D.position(p0, n, c)
    p0n = (p0 - n) / bd if (bd and None not in (p0, n)) else None
    return {"N": n, "C": c, "I": i, "P0": p0, "band": bd, "C_minus_N_bands": cn,
            "answer_mass_min": amass, "gate": verdict, "P0_position": pos,
            "P0_minus_N_bands": p0n,
            "n_orderings": {r: len(by_role.get(r, {})) for r in ("N", "C", "I", "P0")}}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="question_word")
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--out", default="records/result.json")
    a = ap.parse_args(argv)
    arms = [x for x in a.arms.split(",") if x]

    cells, repro = {}, {}
    for arm in arms:
        repro[arm] = {"max_abs_ev_diff": None, "n": 0}
        for fam in FAMS:
            for wd in WORDINGS:
                got = load(f"{R}/runs/{a.run}/{wd}/results/pod223__{arm}__{fam}__completion.json")
                if got is None:
                    continue
                cells[(arm, fam, wd)] = cell(*got)
                if wd == "blame":
                    old = load(f"{R}/runs/local_frames_R/results/pod223__{arm}__{fam}__completion.json")
                    if old:
                        for role, fe in got[0].items():
                            for fid, ev in fe.items():
                                o = old[0].get(role, {}).get(fid)
                                if o is None:
                                    continue
                                dlt = abs(ev - o)
                                cur = repro[arm]["max_abs_ev_diff"]
                                repro[arm]["max_abs_ev_diff"] = dlt if cur is None else max(cur, dlt)
                                repro[arm]["n"] += 1

    # changes from blame
    changes = {}
    for (arm, fam, wd), c in cells.items():
        if wd == "blame":
            continue
        b = cells.get((arm, fam, "blame"))
        if not b:
            continue
        pb = D.pooled_band(b["band"], c["band"])
        ch = {"pooled_band": pb,
              "both_licensed": b["gate"] == "LICENSED" and c["gate"] == "LICENSED",
              "P0_position_change": (None if None in (c["P0_position"], b["P0_position"])
                                     else c["P0_position"] - b["P0_position"])}
        for x in ("N", "C", "I"):
            ch[f"{x}_change_pooled_bands"] = (None if not pb or None in (c[x], b[x])
                                              else (c[x] - b[x]) / pb)
        ch["P0_minus_N_change_pooled_bands"] = (
            None if not pb or None in (c["P0"], c["N"], b["P0"], b["N"])
            else ((c["P0"] - c["N"]) - (b["P0"] - b["N"])) / pb)
        changes[(arm, fam, wd)] = ch

    # counts and pooled summaries
    summary = {}
    for wd in WORDINGS:
        lic = [(k, c) for k, c in cells.items() if k[2] == wd and c["gate"] == "LICENSED"]
        above = [k for k, c in lic if c["P0_minus_N_bands"] is not None
                 and c["P0_minus_N_bands"] > 1.0]
        pos = [c["P0_position"] for _, c in lic if c["P0_position"] is not None]
        s = {"cells_read": sum(1 for k in cells if k[2] == wd),
             "licensed": len(lic),
             "P0_above_N_by_more_than_one_band": len(above),
             "P0_position_median_licensed": statistics.median(pos) if pos else None,
             "P0_position_mean_licensed": statistics.mean(pos) if pos else None,
             "per_scenario": {}}
        for fam in FAMS:
            fl = [c for k, c in lic if k[1] == fam]
            fp = [c["P0_position"] for c in fl if c["P0_position"] is not None]
            s["per_scenario"][fam] = {
                "licensed": len(fl),
                "above_one_band": sum(1 for c in fl if (c["P0_minus_N_bands"] or 0) > 1.0),
                "P0_position_median": statistics.median(fp) if fp else None}
        if wd in VARIANTS:
            both = [ch for k, ch in changes.items() if k[2] == wd and ch["both_licensed"]]
            def med(key):
                v = [ch[key] for ch in both if ch[key] is not None]
                return statistics.median(v) if v else None
            s["vs_blame_on_cells_licensed_under_both"] = {
                "n": len(both),
                "P0_position_change_median": med("P0_position_change"),
                "P0_minus_N_change_pooled_bands_median": med("P0_minus_N_change_pooled_bands"),
                "N_change_pooled_bands_median": med("N_change_pooled_bands"),
                "C_change_pooled_bands_median": med("C_change_pooled_bands"),
                "I_change_pooled_bands_median": med("I_change_pooled_bands"),
                "P0_minus_N_within_one_pooled_band": sum(
                    1 for ch in both if ch["P0_minus_N_change_pooled_bands"] is not None
                    and abs(ch["P0_minus_N_change_pooled_bands"]) <= 1.0),
                "C_moved_more_than_one_pooled_band": sum(
                    1 for ch in both if ch["C_change_pooled_bands"] is not None
                    and abs(ch["C_change_pooled_bands"]) > 1.0)}
        summary[wd] = s

    res = {"run": "239", "mode": "discovery; nothing registered",
           "definitions": "results_derive: band, completion_gate, position, pooled_band",
           "artefact_run": a.run,
           "reproduction_blame_vs_local_frames": repro,
           "summary": summary,
           "cells": {"|".join(k): v for k, v in sorted(cells.items())},
           "changes": {"|".join(k): v for k, v in sorted(changes.items())}}
    text = json.dumps(res, indent=1) + "\n"
    if a.out == "-":
        print(json.dumps({"reproduction": repro, "summary": summary}, indent=1))
        return 0
    if os.path.exists(f"{R}/{a.out}"):
        sys.exit(f"REFUSING: {a.out} exists. Write-once, no override.")
    open(f"{R}/{a.out}", "w").write(text)
    print(json.dumps({"reproduction": repro, "summary": summary}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
