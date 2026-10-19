#!/usr/bin/env python3
"""rebuild_v11_syll_from_log.py : an H7/H8 artefact rebuilt from its call log, for a
reader that was stopped before it could write one.

    python3 scripts/rebuild_v11_syll_from_log.py --completeness_fill --arm deepseek_r --reason "..."

read_v11_syllogism.py writes its artefact only when an arm finishes. completeness_fill's deepseek_r
reader hung on one call (2026-10-17, from 12:35 UTC) and was stopped by hand on the author's
instruction, so its completed calls exist only in runs/completeness_fill/logs/or_<arm>.jsonl. This
rebuilds the artefact from that log alone, with the reader's own plan, prompt-hash check
and parsers (read_v11_syllogism.plan and .score), and adds what the reader would not need
to: which cells are complete, which are partial, and which were never reached, with the
reason. Write-once at the reader's own path, marked `rebuilt_from_log`.
"""
import argparse, hashlib, json, os, sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(R, "scripts"))
import read_v11_syllogism as RV


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", type=int, required=True)
    ap.add_argument("--arm", required=True)
    ap.add_argument("--reason", required=True)
    a = ap.parse_args()
    out = f"{R}/records/RUN{a.run}_V11_SYLL__{a.arm}.json"
    if os.path.exists(out):
        sys.exit(f"write-once: {out} exists")
    log = f"{R}/runs/run{a.run}/logs/or_{a.arm}.jsonl"
    frames = RV.load_frames()
    plan = RV.plan(frames, a.arm)
    recs = {}
    for line in open(log):
        try:
            x = json.loads(line)
        except Exception:
            continue
        lab = x.get("label", "")
        base, _, d = lab.rpartition("|d")
        recs.setdefault(base, []).append((int(d), x))
    cells, served, models, unread, partial = {}, set(), set(), {}, []
    usd = 0.0
    for label, key, kind, m, want16, s, draws in plan:
        got = sorted(recs.get(label, []), key=lambda t: t[0])
        for _, x in got:
            if x["prompt_sha256_16"] != want16:
                sys.exit(f"REFUSING: {label}: logged prompt {x['prompt_sha256_16']} is not "
                         f"the frozen {want16}")
            served.add(x.get("provider_served"))
            models.add(x.get("served_model"))
            usd += x.get("cost_usd") or 0.0
        if not got:
            unread[label] = a.reason
            continue
        if len(got) < draws:
            partial.append(label)
        cells[label] = {"key": key, "kind": kind, "draws": [RV.score(kind, key, x)
                                                           for _, x in got],
                        "prompt16": want16, "settings": s, "n_planned": draws,
                        "complete": len(got) >= draws}
    if len(served) > 1:
        sys.exit(f"REFUSING: more than one provider served: {sorted(served)}")
    json.dump({"arm": a.arm, "run": a.run, "group": frames["arms"][a.arm]["group"],
               "rebuilt_from_log": {"log": os.path.relpath(log, R),
                                    "log_sha256": hashlib.sha256(open(log, "rb").read()).hexdigest(),
                                    "reason": a.reason},
               "frames": RV.FRAMES, "frames_sha256": hashlib.sha256(
                   open(f"{R}/{RV.FRAMES}", "rb").read()).hexdigest(),
               "providers_served": sorted(served), "models_served": sorted(models),
               "calls": sum(len(v["draws"]) for v in cells.values()), "spent_usd": usd,
               "cells": cells, "cells_partial": partial, "cells_unread": unread},
              open(out, "w"), indent=1)
    print(f"{a.arm}: {len(cells)} cells from the log ({len(partial)} partial), "
          f"{len(unread)} never reached; ${usd:.4f} -> {os.path.relpath(out, R)}")


if __name__ == "__main__":
    main()
