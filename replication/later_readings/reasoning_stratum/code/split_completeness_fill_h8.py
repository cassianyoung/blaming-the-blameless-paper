#!/usr/bin/env python3
"""split_completeness_fill_h8.py : one write-once file per H8 arm, so the stratum enters the database
under the build's one-artefact-one-arm rule (the precedent is split_yi_adapter_controls_arms.py).

    .venv/bin/python scripts/split_completeness_fill_h8.py

Reads records/syll_cells.json and writes records/h8__<arm>.json for the
seven arms of completeness_fill_amendment H8: run syllogism_duty's A, R and B on all six pairs, run
general_principle's five prompts, and (Gemini 3.1 Pro) reasoning_traces's trace re-read digits. The cells are
copied unchanged; each file names its source and the source's sha.
"""
import hashlib, json, os, sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# the reasoning-only record (ruled 2026-10-17) is split into h8ro__<arm>.json; the
# all-draws split h8__<arm>.json stays as written and is no longer ingested
SRC = os.environ.get("H8_SRC") or "records/syll_cells_ro.json"
PREFIX = "h8ro__" if SRC.endswith("_RO.json") else "h8__"


def main():
    blob = open(os.path.join(R, SRC), "rb").read()
    d = json.loads(blob)
    for arm, a in sorted(d["arms"].items()):
        if a["group"] != "H8":
            continue
        out = os.path.join(R, "records", f"{PREFIX}{arm}.json")
        if os.path.exists(out):
            sys.exit(f"REFUSED: {out} exists (write-once)")
        json.dump(dict(a, arm=arm, run="reasoning_stratum", stratum="H8, separate, never pooled",
                       readout=d.get("readout_H8"), reasoning_traces_traces=d.get("reasoning_traces_traces"),
                       source={SRC: hashlib.sha256(blob).hexdigest()},
                       amendment=d["amendment"]),
                  open(out, "w"), indent=1, sort_keys=True)
        print("wrote", os.path.relpath(out, R))


if __name__ == "__main__":
    main()
