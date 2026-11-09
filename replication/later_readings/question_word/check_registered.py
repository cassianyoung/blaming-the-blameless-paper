#!/usr/bin/env python3
"""Recompute question_word's registered figures from this folder's committed cells.

    python3 replication/later_readings/question_word/check_registered.py

Standard library only; no model is loaded. The code in code/ is as run, with the working
repository's paths (../README.md, Names and paths), and its scenario names are the public
labels: it reads the bicycle scenario as `bicycle`, while the cell files keep the name they
were read under, `<model>__bicycle216.json`. A layout that copies the file names across
therefore loses the bicycle on every model and wording, and the analysis runs on five
scenarios without complaint (corrected 2026-11-09; CHANGELOG, Corrections to v1.1). This
script reads each cell file by its real name and links it, in a temporary directory, under
the name the code reads, then:
  1. runs code/analyse_question_word.py's main (printing only) on those cells;
  2. formats the four registered figures as the seeder that registered them did, and
     requires each to equal readings/records/question_word_RESULT.json,
     readings/records/question_word_REGISTERED.json and its line in ../../../paper_numbers.csv
     (ids 1076 to 1079);
  3. reports, beside them, what the file-name layout reads, so the defect stays visible.
Exits 1 on any difference.
"""
import contextlib
import csv
import glob
import io
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
LR = os.path.dirname(HERE)
PAPER = os.path.dirname(os.path.dirname(LR))
IDS = {"blame_median": 1076, "fault_median": 1077, "fault_within": 1078, "fault_gate": 1079}
REAL_NAME = {"bicycle": "bicycle216"}      # public scenario label -> the cell file's name


def figures(s):
    b, f = s["blame"], s["at_fault"]
    vs = f["vs_blame_on_cells_licensed_under_both"]
    return {"blame_median": f"{b['P0_position_median_licensed']:.3f}",
            "fault_median": f"{f['P0_position_median_licensed']:.3f}",
            "fault_within": f"{vs['P0_minus_N_within_one_pooled_band']} of {vs['n']}",
            "fault_gate": f"{f['licensed']} of {f['cells_read']}"}


def run(by_real_name):
    with tempfile.TemporaryDirectory() as t:
        for src in ("question_word/code/analyse_question_word.py", "common/results_derive.py"):
            os.makedirs(os.path.join(t, "scripts"), exist_ok=True)
            os.symlink(os.path.join(LR, src), os.path.join(t, "scripts", os.path.basename(src)))
        sys.path.insert(0, os.path.join(t, "scripts"))
        sys.modules.pop("analyse_question_word", None)
        import analyse_question_word as A
        for wd in A.WORDINGS:
            d = os.path.join(t, "runs", "question_word", wd, "results")
            os.makedirs(d)
            for arm in A.ARMS:
                for fam in A.FAMS:
                    name = REAL_NAME.get(fam, fam) if by_real_name else fam
                    src = os.path.join(HERE, "readings/cells", wd, f"{arm}__{name}.json")
                    if os.path.exists(src):
                        os.symlink(src, os.path.join(d, f"pod223__{arm}__{fam}__completion.json"))
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            A.main(["--out", "-"])
        sys.path.pop(0)
    return json.loads(buf.getvalue())["summary"]


def main():
    n_files = len(glob.glob(os.path.join(HERE, "readings/cells/*/*.json")))
    naive = run(by_real_name=False)
    real = run(by_real_name=True)
    now = figures(real)
    banked = figures(json.load(open(os.path.join(HERE, "readings/records/question_word_RESULT.json")))["summary"])
    frozen = {d["key"]: d["value"] for d in json.load(open(os.path.join(
        HERE, "readings/records/question_word_REGISTERED.json")))["figures"]}
    with open(os.path.join(PAPER, "paper_numbers.csv"), encoding="utf-8") as fh:
        printed = {int(r["id"]): r["printed"] for r in
                   csv.DictReader(l for l in fh if not l.startswith("#"))}
    print(f"  cell files: {n_files}; readings per wording, files read under their real names: "
          f"{real['blame']['cells_read']}; under the code's scenario names: "
          f"{naive['blame']['cells_read']} (the defect, which would print {figures(naive)})")
    bad = 0
    for k, i in IDS.items():
        ok = now[k] == banked[k] == frozen.get(k) == printed.get(i)
        bad += not ok
        print(f"  {'ok  ' if ok else 'DIFF'} id {i}  {now[k]:>9}  {k}"
              + ("" if ok else f"  (result file {banked[k]!r}, frozen {frozen.get(k)!r}, "
                                f"paper_numbers {printed.get(i)!r})"))
    print(f"  {len(IDS) - bad} of {len(IDS)} figures reproduce")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
