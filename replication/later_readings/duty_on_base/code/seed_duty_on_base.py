#!/usr/bin/env python3
"""Register duty_on_base's figures in `paper_numbers` (the duty test on base checkpoints).

    seed_duty_on_base.py [--freeze]

Cassian, 2026-11-09: "bank duty_on_base ... register as new ids (next free numbers, labels with
condition tokens, location §4.5 and B.7)": the per-family base-minus-release difference in
ruler units and the count clearing 0.16; base gaps positive and beyond noise, with the pairs
they fall on; the driving control (positive, beyond the band, Llama-3.1-8B-Instruct's gap);
the pooled medians for base and release. "Confirm the ids against the result file at printed
precision; no value typed by hand."

duty_on_base IS PRE-REGISTERED (records/PREREG_duty_on_base_DUTY_BASE.md, ruled 2026-11-06 before any
pod). The value at build is analyse_duty_on_base's own functions (worksheet, legs, cells,
analyse) re-run on the committed artefacts (runs/duty_on_base/{worksheet,duty}/), with
results_derive's definitions; it must equal the same figure formatted from the banked
records/result.json and the value frozen in records/registered.json
(write-once). duty_on_base's cells are not ingested into the database, so the reproduction is
from the artefacts, as question_word's is. Appended after seed_v027_footnote and before
relocate_v019, so no id moves.

THE DRIVING COUNT IS 11 OF 12, NOT 12 OF 12. records/outcomes.md says "All twelve
driving gaps are positive"; OLMo-2-7B base's is -0.0074 digits in the result file. The
figure is the file's.
"""
import json
import os
import statistics
import sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(R, "scripts"))

FROZEN = "records/registered.json"
RESULT = "records/result.json"
STATUS = (f"new 2026-11-09 (seed_duty_on_base, frozen in {FROZEN}); pre-registered in "
          "records/PREREG_duty_on_base_DUTY_BASE.md")
FAM_NAMES = {"gemma9": "gemma-2-9b", "llama31": "Llama-3.1-8B", "mistral": "Mistral-7B-v0.3",
             "qwen3": "Qwen3-8B", "olmo2": "OLMo-2-7B", "falcon3": "Falcon3-7B"}
PAIR_NAMES = {"prawns": "prawns", "1": "electrical work", "3": "gas safety",
              "4": "childcare", "7": "hair dye"}
HEAD = ("§4.5 / Appendix B.7 (duty_on_base, pre-registered): the duty test on {who}, worksheet "
        "frame, five orderings, each leg read as a separate case; gap = professional leg "
        "minus private leg; ")
BOTH = HEAD.format(who="six pretrained base models and their developer releases")
BASE = HEAD.format(who="six pretrained base models")
REL = HEAD.format(who="six developer releases")
RULER = "in ruler units (the model's own median careful-to-careless range on the worksheet)"
LOCS = {}
for f, n in FAM_NAMES.items():
    LOCS[f"fam_{f}"] = (BOTH + f"{n}: median gap over the five pairs other than driving, base "
                        f"minus release, {RULER}")
LOCS.update({
    "p1_count": BOTH + "families whose base-minus-release difference in median gap reaches "
                "the pre-registered 0.16 " + RULER + " (duty_on_base P1, the residue claim)",
    "base_gt_rel": BOTH + "families whose base median gap exceeds the release's, " + RULER,
    "base_pos": BASE + "cells (six models x five pairs other than driving) whose gap is "
                "positive",
    "base_out": BASE + "cells (six models x five pairs other than driving) whose gap lies "
                "beyond one pooled noise band of zero",
})
for p, n in PAIR_NAMES.items():
    LOCS[f"base_out_{p}"] = (BASE + f"{n}: models whose gap lies beyond one pooled noise "
                             "band of zero")
LOCS.update({
    "drive_pos": BOTH + "driving (the control pair): models, base and release, whose gap is "
                 "positive",
    "drive_out": BOTH + "driving (the control pair): models, base and release, whose gap lies "
                 "beyond one pooled noise band of zero (duty_on_base P3)",
    "drive_llama_rel": REL + "driving (the control pair): Llama-3.1-8B-Instruct's gap, in "
                       "digits",
    "med_base": BASE + "median gap pooled over the 30 cells other than driving, " + RULER,
    "med_rel": REL + "median gap pooled over the 30 cells other than driving, " + RULER,
})
QUERY = ("-- scripts/analyse_duty_on_base.py (worksheet, legs, cells, analyse) over "
         "runs/duty_on_base/worksheet/results/ and runs/duty_on_base/duty/ (results_derive band, "
         "pooled_band, completion gate); checked against records/result.json; "
         "scripts/seed_duty_on_base.py")


def from_artefacts():
    """analyse_duty_on_base.main's computation, without its write: {"P245_1": ..., "per_arm":
    {arm: {"cells": ...}}}."""
    import analyse_duty_on_base as A
    fr = json.load(open(os.path.join(R, A.FRAMES)))
    per = {}
    for x in fr["arms"]:
        ws = A.worksheet(x["arm"])
        lg = A.legs(json.load(open(f"{R}/runs/duty_on_base/duty/duty_on_base__{x['arm']}.json")), fr)
        per[x["arm"]] = {"ws": ws, "legs": lg, "cells": A.cells(x["arm"], ws, lg)}
    res = A.analyse(fr["arms"], per)
    res["per_arm"] = {k: {"cells": v["cells"]} for k, v in per.items()}
    return res, fr["arms"]


def figures(res, arms):
    import analyse_duty_on_base as A
    fam = res["P245_1"]["per_family"]
    by = {(a["family"], a["version"]): a["arm"] for a in arms}
    cells = {a: res["per_arm"][a]["cells"] for a in res["per_arm"]}
    base = [by[(f, "base")] for f in A.FAMILIES]
    rel = [by[(f, "release")] for f in A.FAMILIES]
    for a in base + rel:                          # every cell gated, so every count is over all
        assert all(cells[a][p]["gated"] for p in A.PAIRS), a
    nd = lambda arms_: [cells[a][p] for a in arms_ for p in A.NONDRIVING]
    out = {f"fam_{f}": f"{fam[f]['base_minus_release_ruler']:.2f}" for f in A.FAMILIES}
    out["p1_count"] = f"{res['P245_1']['families_exceeding_ruler']} of {len(A.FAMILIES)}"
    out["base_gt_rel"] = (f"{sum(fam[f]['base_minus_release_ruler'] > 0 for f in A.FAMILIES)} "
                          f"of {len(A.FAMILIES)}")
    out["base_pos"] = f"{sum(c['gap'] > 0 for c in nd(base))} of {len(nd(base))}"
    out["base_out"] = f"{sum(not c['within_band'] for c in nd(base))} of {len(nd(base))}"
    for p in A.NONDRIVING:
        out[f"base_out_{p}"] = (f"{sum(not cells[a][p]['within_band'] for a in base)} of "
                                f"{len(base)}")
    drv = [cells[a]["5"] for a in base + rel]
    out["drive_pos"] = f"{sum(c['gap'] > 0 for c in drv)} of {len(drv)}"
    out["drive_out"] = f"{sum(not c['within_band'] for c in drv)} of {len(drv)}"
    out["drive_llama_rel"] = f"{cells[by[('llama31', 'release')]]['5']['gap']:.2f}"
    out["med_base"] = f"{statistics.median(c['gap_ruler'] for c in nd(base)):.2f}"
    out["med_rel"] = f"{statistics.median(c['gap_ruler'] for c in nd(rel)):.2f}"
    # the cross-checks the registered verdicts carry
    assert out["base_out"] == f"{30 - res['P245_2']['within_one_pooled_band']} of 30"
    assert out["drive_out"] == f"{len(res['P245_3']['outside'])} of 12"
    assert set(out) == set(LOCS), sorted(set(out) ^ set(LOCS))
    return out


def both():
    now = figures(*from_artefacts())
    arms = json.load(open(os.path.join(R, "records/frames.json")))["arms"]
    banked = figures(json.load(open(os.path.join(R, RESULT))), arms)
    return now, banked


def seed(con):
    """Returns (n_attempted, n_reproducing, [mismatch strings])."""
    try:
        now, banked = both()
    except Exception as e:                        # noqa: BLE001
        return 1, 0, [f"{type(e).__name__}: {e}"]
    p = os.path.join(R, FROZEN)
    frozen = ({d["key"]: d["value"] for d in json.load(open(p))["figures"]}
              if os.path.exists(p) else {})
    ok, bad = 0, []
    for k, loc in LOCS.items():
        v = now[k]
        printed = frozen.get(k, v)
        m = int(printed == v == banked[k])
        ok += int(m and k in frozen)
        if not m:
            bad.append(f"{k}: frozen {printed!r}, artefacts {v!r}, result file {banked[k]!r}")
        if k not in frozen:
            bad.append(f"NOT YET FROZEN: {k} = {v!r}")
        con.execute("INSERT INTO paper_numbers(location,printed,query,value_at_build,"
                    "matches,location_registered,location_status) VALUES(?,?,?,?,?,?,?)",
                    (loc, printed, QUERY, v, m, loc, STATUS))
    return len(LOCS), ok, bad


if __name__ == "__main__":
    now, banked = both()
    if now != banked:
        sys.exit(f"REFUSING: artefacts {now} differ from {RESULT} {banked}")
    if sys.argv[1:] == ["--freeze"]:
        p = os.path.join(R, FROZEN)
        if os.path.exists(p):
            sys.exit(f"REFUSING: {FROZEN} exists (write-once)")
        json.dump({"frozen_from": "runs/duty_on_base artefacts via analyse_duty_on_base, equal to "
                                  "records/result.json at printed precision, 2026-11-09",
                   "note": "drive_pos is 11 of 12: OLMo-2-7B base's driving gap is -0.0074 "
                           "digits; records/outcomes.md's 'All twelve' is wrong",
                   "figures": [{"key": k, "location": LOCS[k], "value": now[k]}
                               for k in LOCS]},
                  open(p, "x"), indent=1, ensure_ascii=False)
        print(f"  wrote {FROZEN}")
    for k in LOCS:
        print(f"  {now[k]:>9}  {k}")
