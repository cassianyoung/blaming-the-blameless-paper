#!/usr/bin/env python3
"""analyse_duty_on_base.py : duty_on_base's registered analysis (records/PREREG_duty_on_base_DUTY_BASE.md).

    .venv/bin/python scripts/analyse_duty_on_base.py --selftest
    .venv/bin/python scripts/analyse_duty_on_base.py            # -> records/result.json (write-once)

Definitions are results_derive's (band, pooled band, completion gate), through
analyse_question_word's loader for the worksheet cells. Per arm:
  worksheet  per scenario: N, C, band, gate (LICENSED iff C - N >= 3 bands and mass >= 0.7).
             The arm is LICENSED on the frame if at least 4 of its 6 scenarios are (A0.5).
             RULER = median (C - N) in digits over its licensed scenarios.
  duty leg   mean over the five orderings, band 2.33 x pstdev over them, gated if every
             ordering's answer mass >= 0.7.
  duty cell  gap = PRO mean - PRIV mean; band = pooled_band(b_PRO, b_PRIV); gated if both
             legs are and the arm is licensed. gap_ruler = gap / RULER.
Predictions (A0.6 to A0.8):
  duty_on_base P1  per family, median gap over its gated non-driving pairs, base minus release:
          DECIDES in ruler units, >= 0.16 (0.5 digits on the base arms' pooled median ruler,
          3.1, question_word); raw digits >= 0.5 beside. PASS on >= 4 of 6 families.
  duty_on_base P2  |gap| <= its pooled band on >= 20 of the 30 base non-driving cells (ungated: not within).
  duty_on_base P3  driving: |gap| <= its pooled band on at least 10 of the 12 arms, base and release
          (ruling 2026-11-06); an ungated arm counts as not within.
"""
import argparse, json, os, statistics, sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(R, "scripts"))
import results_derive as D                                         # noqa: E402
import analyse_question_word as A239                                      # noqa: E402

FRAMES = "records/frames.json"
OUT = "records/result.json"
FAMS = ("bicycle", "cheque", "ladder", "prawns_home", "prawns_restaurant", "scaffolding")
PAIRS = ("prawns", "1", "3", "4", "5", "7")
NONDRIVING = ("prawns", "1", "3", "4", "7")
FAMILIES = ("gemma9", "llama31", "mistral", "qwen3", "olmo2", "falcon3")
MIN_LICENSED_SCEN = 4
P1_RULER, P1_DIGITS, P1_NEED = 0.16, 0.5, 4
P2_NEED = 20
P3_NEED = 10                      # ruling: at least 10 of 12, not every model


def worksheet(arm, run="duty_on_base"):
    scen = {}
    for f in FAMS:
        x = A239.load(f"{R}/runs/{run}/worksheet/results/pod223__{arm}__{f}__completion.json")
        scen[f] = A239.cell(*x) if x else None
    lic = [s for s in scen.values() if s and s["gate"] == "LICENSED"]
    ruler = statistics.median(s["C"] - s["N"] for s in lic) if lic else None
    return {"scenarios": scen, "licensed": len(lic), "arm_licensed": len(lic) >= MIN_LICENSED_SCEN,
            "ruler_C_minus_N": ruler,
            "median_N": statistics.median(s["N"] for s in lic) if lic else None}


def legs(duty, fr):
    out = {}
    for key in fr["legs"]:
        evs = [duty["cells"][f"{key}|{fid}"] for fid in fr["frames"]]
        ok = [c for c in evs if not c.get("void") and c.get("ev") is not None]
        e = [c["ev"] for c in ok]
        sd = D.pstdev(e)
        out[key] = {"mean": D.mean(e), "band": sd * D.BAND_SD_K if sd is not None else None,
                    "evs": e, "answer_mass_min": min((c["answer_mass"] for c in ok), default=None),
                    "gated": len(ok) == len(fr["frames"]) and min((c["answer_mass"] for c in ok), default=0) >= D.AMASS_MIN}
    return out


def cells(arm, ws, lg):
    out = {}
    for p in PAIRS:
        a, b = lg[f"p{p}|PRO"], lg[f"p{p}|PRIV"]
        gap = (a["mean"] - b["mean"]) if None not in (a["mean"], b["mean"]) else None
        pb = D.pooled_band(a["band"], b["band"])
        ru = ws["ruler_C_minus_N"]
        out[p] = {"pro": a["mean"], "priv": b["mean"], "gap": gap, "pooled_band": pb,
                  "gap_ruler": gap / ru if (gap is not None and ru) else None,
                  "pro_position": ((a["mean"] - ws["median_N"]) / ru if (ru and a["mean"] is not None) else None),
                  "priv_position": ((b["mean"] - ws["median_N"]) / ru if (ru and b["mean"] is not None) else None),
                  "within_band": (abs(gap) <= pb + 1e-12) if (gap is not None and pb is not None) else None,
                  "gated": a["gated"] and b["gated"] and ws["arm_licensed"]}
    return out


def analyse(arms, per):
    """arms: [{arm, version, family}]; per: {arm: {"ws": ..., "cells": ...}}."""
    v = {(a["family"], a["version"]): a["arm"] for a in arms}
    med = lambda xs: statistics.median(xs) if xs else None
    fam = {}
    for f in FAMILIES:
        row = {}
        for ver in ("base", "release"):
            c = per.get(v.get((f, ver)), {}).get("cells") or {}
            g = [c[p] for p in NONDRIVING if p in c and c[p]["gated"]]
            row[ver] = {"median_gap": med([x["gap"] for x in g]),
                        "median_gap_ruler": med([x["gap_ruler"] for x in g if x["gap_ruler"] is not None]),
                        "gated_pairs": len(g)}
        b, r = row["base"], row["release"]
        dr = (b["median_gap_ruler"] - r["median_gap_ruler"]
              if None not in (b["median_gap_ruler"], r["median_gap_ruler"]) else None)
        dd = (b["median_gap"] - r["median_gap"] if None not in (b["median_gap"], r["median_gap"]) else None)
        row.update(base_minus_release_ruler=dr, base_minus_release_digits=dd,
                   exceeds_ruler=dr is not None and dr >= P1_RULER - 1e-12,
                   exceeds_digits=dd is not None and dd >= P1_DIGITS - 1e-12)
        fam[f] = row
    n1 = sum(r["exceeds_ruler"] for r in fam.values())
    n1d = sum(r["exceeds_digits"] for r in fam.values())
    p1 = {"families_exceeding_ruler": n1, "need": P1_NEED, "criterion": "PASS" if n1 >= P1_NEED else "FAIL",
          "beside_raw_digits": {"families_exceeding": n1d, "criterion": "PASS" if n1d >= P1_NEED else "FAIL"},
          "per_family": fam}
    base = [a["arm"] for a in arms if a["version"] == "base"]
    within = sum(1 for a in base for p in NONDRIVING
                 if (per.get(a, {}).get("cells") or {}).get(p, {}).get("gated")
                 and per[a]["cells"][p]["within_band"])
    p2 = {"within_one_pooled_band": within, "of": len(base) * len(NONDRIVING), "need": P2_NEED,
          "criterion": "PASS" if within >= P2_NEED else "FAIL"}
    drv = {a["arm"]: (per.get(a["arm"], {}).get("cells") or {}).get("5") for a in arms}
    gated = {k: c for k, c in drv.items() if c and c["gated"]}
    w3 = sum(c["within_band"] for c in gated.values())
    p3 = {"gated_arms": len(gated), "within": w3, "of": len(arms), "need": P3_NEED,
          "outside": sorted(k for k, c in gated.items() if not c["within_band"]),
          "ungated": sorted(k for k in drv if k not in gated),
          "criterion": ("UNTESTABLE" if not gated else ("PASS" if w3 >= P3_NEED else "FAIL"))}
    reading = {("PASS", "FAIL"): "RESIDUE: the base gives the private person more of the allowance than the release",
               ("FAIL", "PASS"): "NOTHING THERE: the base does not distinguish the legs",
               ("FAIL", "FAIL"): "THE BASE DISTINGUISHES THE LEGS, NO MORE THAN THE RELEASE: the null for the residue claim",
               ("PASS", "PASS"): "BOTH: base gaps near zero and releases' gaps negative (the release blames the private person more)"}
    return {"P245_1": p1, "P245_2": p2, "P245_3": p3,
            "reading": reading[(p1["criterion"], p2["criterion"])],
            "Null_residue": "FIRES" if p1["criterion"] == "FAIL" else "does not fire"}


def selftest():
    ok = 0
    arms = [{"arm": f"{f}_{v[:4] if v == 'base' else 'rel'}", "version": v, "family": f}
            for f in FAMILIES for v in ("base", "release")]
    for a in arms:
        a["arm"] = a["arm"].replace("_base", "_base")

    def per_for(base_gap, rel_gap, band=0.2, drive=0.0, ruler=3.0, gated=True):
        per = {}
        for a in arms:
            gp = base_gap if a["version"] == "base" else rel_gap
            c = {}
            for p in PAIRS:
                g = drive if p == "5" else (gp(a, p) if callable(gp) else gp)
                c[p] = {"gap": g, "pooled_band": band, "gap_ruler": g / ruler,
                        "within_band": abs(g) <= band, "gated": gated}
            per[a["arm"]] = {"cells": c}
        return per
    r = analyse(arms, per_for(1.5, 0.3))
    assert r["P245_1"]["criterion"] == "PASS" and r["P245_2"]["criterion"] == "FAIL"
    assert r["P245_3"]["criterion"] == "PASS" and r["reading"].startswith("RESIDUE"); ok += 1
    r = analyse(arms, per_for(0.1, 0.8))
    assert r["P245_1"]["criterion"] == "FAIL" and r["P245_2"]["criterion"] == "PASS"
    assert r["reading"].startswith("NOTHING") and r["Null_residue"] == "FIRES"; ok += 1
    r = analyse(arms, per_for(0.8, 0.8))
    assert r["reading"].startswith("THE BASE DISTINGUISHES"); ok += 1
    # ruler decides, digits beside: 0.45 digits on a 2.0 ruler is 0.225 >= 0.16
    r = analyse(arms, per_for(0.75, 0.30, ruler=2.0))
    assert r["P245_1"]["criterion"] == "PASS" and r["P245_1"]["beside_raw_digits"]["criterion"] == "FAIL"; ok += 1
    # duty_on_base P2 boundary: 20 within passes, 19 fails; ungated never counts as within
    def g20(a, p):
        i = FAMILIES.index(a["family"]) * 5 + NONDRIVING.index(p)
        return 0.1 if i < 20 else 1.0
    def g19(a, p):
        i = FAMILIES.index(a["family"]) * 5 + NONDRIVING.index(p)
        return 0.1 if i < 19 else 1.0
    assert analyse(arms, per_for(g20, 0.3))["P245_2"]["within_one_pooled_band"] == 20
    assert analyse(arms, per_for(g20, 0.3))["P245_2"]["criterion"] == "PASS"
    assert analyse(arms, per_for(g19, 0.3))["P245_2"]["criterion"] == "FAIL"
    assert analyse(arms, per_for(0.0, 0.3, gated=False))["P245_2"]["within_one_pooled_band"] == 0; ok += 1
    # duty_on_base P3: 10 of 12 within passes, 9 fails; all outside fails; none gated is untestable
    def per_drive(n_out):
        per = per_for(1.0, 0.3)
        for a in arms[:n_out]:
            per[a["arm"]]["cells"]["5"].update(gap=0.5, within_band=False)
        return per
    assert analyse(arms, per_drive(2))["P245_3"]["criterion"] == "PASS"
    assert analyse(arms, per_drive(3))["P245_3"]["criterion"] == "FAIL"
    assert analyse(arms, per_for(1.0, 0.3, drive=0.5))["P245_3"]["criterion"] == "FAIL"
    assert analyse(arms, per_for(1.0, 0.3, gated=False))["P245_3"]["criterion"] == "UNTESTABLE"; ok += 1
    # the real worksheet loader: the dry-run artefacts, if present, load and gate without error
    if os.path.exists(f"{R}/runs/duty_on_base_dry/worksheet/results"):
        ws = worksheet("gemma9_base", run="duty_on_base_dry")
        assert len(ws["scenarios"]) == 6 and all(s is not None for s in ws["scenarios"].values())
        fr = json.load(open(os.path.join(R, FRAMES))) if os.path.exists(os.path.join(R, FRAMES)) else None
        if fr:
            lg = legs(json.load(open(f"{R}/runs/duty_on_base_dry/duty/duty_on_base__gemma9_base.json")), fr)
            assert len(lg) == 12 and all(len(x["evs"]) == 5 for x in lg.values())
    ok += 1
    print(f"selftest {ok}/7")
    return 0 if ok == 7 else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if os.path.exists(os.path.join(R, OUT)):
        sys.exit(f"write-once: {OUT} exists")
    fr = json.load(open(os.path.join(R, FRAMES)))
    per, missing = {}, []
    for x in fr["arms"]:
        dp = f"{R}/runs/duty_on_base/duty/duty_on_base__{x['arm']}.json"
        if not os.path.exists(dp):
            missing.append(x["arm"]); continue
        ws = worksheet(x["arm"])
        lg = legs(json.load(open(dp)), fr)
        per[x["arm"]] = {"ws": ws, "legs": lg, "cells": cells(x["arm"], ws, lg)}
    res = analyse(fr["arms"], per)
    # reproduction: base arms' worksheet cells against question_word's banked blame read
    rep = {}
    for x in fr["arms"]:
        if x["version"] != "base" or x["arm"] not in per:
            continue
        worst = 0.0
        for f in FAMS:
            new = json.load(open(f"{R}/runs/duty_on_base/worksheet/results/pod223__{x['arm']}__{f}__completion.json"))["cells"]
            old = json.load(open(f"{R}/runs/question_word/blame/results/pod223__{x['arm']}__{f}__completion.json"))["cells"]
            for k, c in new.items():
                if c.get("ev") is not None and old.get(k, {}).get("ev") is not None:
                    worst = max(worst, abs(c["ev"] - old[k]["ev"]))
        rep[x["arm"]] = worst
    res.update(reproduction_max_abs_ev_vs_question_word=rep, arms_missing=missing,
               per_arm={k: {"worksheet": v["ws"], "cells": v["cells"],
                            "legs": {lk: {kk: vv for kk, vv in lv.items()} for lk, lv in v["legs"].items()}}
                        for k, v in per.items()})
    json.dump(res, open(os.path.join(R, OUT), "w"), indent=1, default=str)
    print(json.dumps({k: res[k] for k in ("P245_1", "P245_2", "P245_3", "reading", "Null_residue",
                                          "reproduction_max_abs_ev_vs_question_word", "arms_missing")},
                     indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
