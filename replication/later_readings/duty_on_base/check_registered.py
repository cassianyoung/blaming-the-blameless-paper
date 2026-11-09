#!/usr/bin/env python3
"""Recompute duty_on_base's registered figures from this folder's committed results.

    python3 replication/later_readings/duty_on_base/check_registered.py

Standard library only; no model is loaded. The code in code/ is as run, so its paths are the
working repository's (../README.md, Names and paths). This script lays this folder's files
out in that layout, as symbolic links in a temporary directory, and then:
  1. runs the analysis script's own self-test (analyse_duty_on_base.py --selftest, 7 of 7);
  2. recomputes the registered figures with the analysis script's functions (worksheet, legs,
     cells, analyse) from readings/cells/, through the seeder that registered them
     (seed_duty_on_base.py), and requires them to equal the figures formatted from the
     banked result file;
  3. requires each figure to equal the printed value of its id in ../../../paper_numbers.csv
     (ids 1133 to 1152, in the seeder's order) and in readings/records/duty_on_base_REGISTERED.json.
Exits 1 on any difference.
"""
import csv
import glob
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
LR = os.path.dirname(HERE)
PAPER = os.path.dirname(os.path.dirname(LR))
FIRST_ID = 1133


def link(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    os.symlink(src, dst)


def layout(t):
    run = os.path.join(t, "runs", "duty_on_base")
    for f in glob.glob(os.path.join(HERE, "readings/cells/worksheet/*.json")):
        arm, scen = os.path.basename(f)[:-5].split("__")
        link(f, os.path.join(run, "worksheet/results", f"pod223__{arm}__{scen}__completion.json"))
    for f in glob.glob(os.path.join(HERE, "readings/cells/duty/*.json")):
        link(f, os.path.join(run, "duty", "duty_on_base__" + os.path.basename(f)))
    for name, src in (("frames.json", "prompts/duty_on_base_FRAMES.json"),
                      ("result.json", "readings/records/duty_on_base_RESULT.json"),
                      ("registered.json", "readings/records/duty_on_base_REGISTERED.json")):
        link(os.path.join(HERE, src), os.path.join(t, "records", name))
    for src in ("duty_on_base/code/analyse_duty_on_base.py",
                "duty_on_base/code/seed_duty_on_base.py",
                "question_word/code/analyse_question_word.py", "common/results_derive.py"):
        link(os.path.join(LR, src), os.path.join(t, "scripts", os.path.basename(src)))


def main():
    with tempfile.TemporaryDirectory() as t:
        layout(t)
        st = subprocess.run([sys.executable, os.path.join(t, "scripts/analyse_duty_on_base.py"),
                             "--selftest"], capture_output=True, text=True)
        print(f"  analyse_duty_on_base.py --selftest: {st.stdout.strip() or st.stderr.strip()}")
        sys.path.insert(0, os.path.join(t, "scripts"))
        import seed_duty_on_base as S
        now, banked = S.both()
    frozen = {d["key"]: d["value"] for d in json.load(open(os.path.join(
        HERE, "readings/records/duty_on_base_REGISTERED.json")))["figures"]}
    with open(os.path.join(PAPER, "paper_numbers.csv"), encoding="utf-8") as fh:
        printed = {int(r["id"]): r["printed"] for r in
                   csv.DictReader(l for l in fh if not l.startswith("#"))}
    bad = 0 if st.returncode == 0 and "7/7" in st.stdout else 1
    for i, k in enumerate(S.LOCS):
        pid = FIRST_ID + i
        ok = now[k] == banked[k] == frozen.get(k) == printed.get(pid)
        bad += not ok
        print(f"  {'ok  ' if ok else 'DIFF'} id {pid}  {now[k]:>9}  {k}"
              + ("" if ok else f"  (result file {banked[k]!r}, frozen {frozen.get(k)!r}, "
                                f"paper_numbers {printed.get(pid)!r})"))
    n_ok = sum(now[k] == banked[k] == frozen.get(k) == printed.get(FIRST_ID + i)
               for i, k in enumerate(S.LOCS))
    print(f"  {n_ok} of {len(S.LOCS)} figures reproduce; self-test "
          f"{'passed' if st.returncode == 0 and '7/7' in st.stdout else 'FAILED'}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
