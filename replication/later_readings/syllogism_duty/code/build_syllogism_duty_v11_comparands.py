#!/usr/bin/env python3
"""build_syllogism_duty_v11_comparands.py : freeze run syllogism_duty's comparands under the v1.1 fill.

    .venv/bin/python scripts/build_syllogism_duty_v11_comparands.py --db <a v1.1 build>

Writes records/v11_comparands.json (write-once). completeness_fill_amendment H7:
"the comparands for prawns (stated gap, separate gap, floor) are frozen at ingest from the
H4 recompute, in the manner of build_syllogism_duty_frames.py". The same function as that file's
`comparands()`, over `duty_fig7` at the v1.1 database, for every arm syllogism_duty and its H8
stratum read and for all six reported pairs, prawns included.

**ALL SIX PAIRS ARE RE-FROZEN, NOT ONLY PRAWNS.** The v1.1 floor pools 18 neutral
deviations where 781e1e83's pooled 15, so every arm's wording floor moves, and the
amendment lists run syllogism_duty's floor counts (ids 454 to 464, 470) among the figures the pooled
floor may move. Freezing prawns at the new floor beside five pairs at the old one would
judge one arm's cells against two floors. The banked comparands in frames.json are
untouched and stay the record of the banked result.

A comparand cell the v1.1 database does not have (prawns' full-text stated gap MISSING:
grok43_s, one order void; Qwen3-235B and Qwen3-30B are not syllogism_duty arms) is frozen with
status "missing" and its reason, never refused and never filled.

The build (seed_syllogism_duty) re-reads duty_fig7 and refuses if any frozen value differs, so a
later rebuild cannot move a comparand under the result silently.
"""
import argparse, hashlib, json, os, sqlite3, sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(R, "records", "v11_comparands.json")
PAIRS = ["prawns", "1", "3", "4", "5", "7"]
COLS = ("arm", "pair_id", "stated_gap", "separate_gap", "sep_pro", "sep_priv",
        "floor_used", "floor_used_source", "share", "stated_condition_gap",
        "convention_stated", "status", "missing_reason")


def fsha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def comparands(con, arms):
    q = ("SELECT " + ", ".join(COLS) + " FROM duty_fig7 WHERE arm = ? AND pair_id = ?")
    out = {}
    for arm in arms:
        for p in PAIRS:
            r = con.execute(q, (arm, p)).fetchone()
            if r is None:
                raise SystemExit(f"REFUSING: duty_fig7 has no row for {arm} pair {p}")
            d = dict(zip(COLS, r))
            d["comparand_status"] = ("read" if None not in (d["stated_gap"],
                                                            d["separate_gap"],
                                                            d["floor_used"])
                                     else "missing")
            out[f"{arm}|{p}"] = d
    return out


def arms():
    import analyse_syllogism_duty as A
    fr = json.load(open(os.path.join(R, "records", "v11_frames.json")))
    return list(A.ARMS) + sorted(a for a, v in fr["arms"].items() if v["group"] == "H8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    a = ap.parse_args()
    if os.path.exists(OUT):
        sys.exit(f"REFUSED: {OUT} exists (write-once)")
    sys.path.insert(0, os.path.join(R, "scripts"))
    con = sqlite3.connect(f"file:{a.db}?mode=ro", uri=True)
    cells = comparands(con, arms())
    miss = {k: v["missing_reason"] for k, v in cells.items()
            if v["comparand_status"] == "missing"}
    json.dump({"what": "run syllogism_duty's comparands under the v1.1 fill, all six pairs "
                       "(scripts/build_syllogism_duty_v11_comparands.py)",
               "amendment": "records/completeness_fill_amendment_20261017.md (H7, H8)",
               "source": f"duty_fig7 and duty_floor_used at database sha256 {fsha(a.db)}",
               "cells": cells, "missing": miss},
              open(OUT, "w"), indent=1, sort_keys=True)
    print(f"{len(cells)} comparand cells, {len(miss)} missing -> "
          f"{os.path.relpath(OUT, R)}")
    for k, v in miss.items():
        print(f"  missing {k}: {v}")


if __name__ == "__main__":
    main()
