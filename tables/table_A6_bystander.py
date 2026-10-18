#!/usr/bin/env python3
"""Table A.6: base models and the bystander, per family and scenario, as one grid.

Panel A reads data/A6_bystander_long.csv (base rows): the careful subject's position minus
the bystander's, in the model's noise bands, per scenario; the number of scenarios
clearing two bands; and the bicycle positions. Rows are the nine families ordered by the
careful subject's bicycle position, then the two smaller Yi base models.

Panel B reads the same file for each version's mean positions over nine families and
six scenarios, and data/A6_within_family.csv for the changes and the number of
model-scenario pairs lowered by more than one pooled band.

Writes tables/out/table_A6_bystander.csv: panel A's header and rows, its summary line,
panel B's title, header and rows, in the manuscript's order.
"""
import os
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from paperlib import (read_csv, write_table, num, f2, signed,  # noqa: E402
                      FAMILY_LABEL, SCENARIOS, SCENARIO_LABEL)

PASSES_OBJECT = {"ladder", "scaffolding"}
BASE_ONLY = ["yi9b", "yi6b"]


def main():
    long_ = read_csv("A6_bystander_long.csv")
    base = [r for r in long_ if r["version"] == "base"]
    cell = {(r["family"], r["scenario"]): r for r in base}
    fams = sorted({r["family"] for r in base} - set(BASE_ONLY),
                  key=lambda f: -num(cell[(f, "bicycle")]["P0_pos"])) + BASE_ONLY
    header = (["Family"]
              + [SCENARIO_LABEL[s] + (" †" if s in PASSES_OBJECT else "")
                 for s in SCENARIOS]
              + ["Scenarios clearing 2 bands", "Bicycle: careful subject",
                 "Bicycle: bystander"])
    out = []
    for f in fams:
        row = [FAMILY_LABEL[f]]
        for s in SCENARIOS:
            row.append(f2(num(cell[(f, s)]["gap_bands"]), 1))
        n = sum(1 for s in SCENARIOS if cell[(f, s)]["clears_2_bands"] == "true")
        row += [f"{n} of 6", f2(num(cell[(f, "bicycle")]["P0_pos"])),
                f2(num(cell[(f, "bicycle")]["BYST_pos"]))]
        out.append(row)
    nine = [r for r in base if r["family"] not in BASE_ONLY]
    cl = sum(1 for r in nine if r["clears_2_bands"] == "true")
    outside = [r for r in nine if r["scenario"] not in PASSES_OBJECT]
    clo = sum(1 for r in outside if r["clears_2_bands"] == "true")
    summary = (f"Nine families: {cl} of {len(nine)} model–scenario pairs clear two "
               f"bands; {clo} of {len(outside)} outside the two scenarios marked †.")
    out.append([summary])
    out.append(["B. Within each family: what post-training removes (worksheet, nine "
                "families × six scenarios)"])

    wf = read_csv("A6_within_family.csv")
    hb = ["Version", "Bystander, mean position", "Careful subject, mean position",
          "Change in bystander", "Change in careful subject",
          "Bystander lowered beyond one band", "Careful subject lowered beyond one band"]
    rows_b = [hb]
    for version, label, comp in (("base", "Pretrained base", None),
                                 ("adapter", "Study adapter", "adapter"),
                                 ("instruct", "Developer's release",
                                  "developer release")):
        rr = [r for r in long_ if r["version"] == version
              and r["family"] not in BASE_ONLY]
        mb = st.mean(num(r["BYST_pos"]) for r in rr)
        mp = st.mean(num(r["P0_pos"]) for r in rr)
        if comp is None:
            rows_b.append([label, f2(mb), f2(mp), "–", "–", "–", "–"])
            continue
        ww = [r for r in wf if r["comparison"].endswith(comp)]
        rows_b.append([label, f2(mb), f2(mp),
                       signed(st.mean(num(r["d_BYST_pos"]) for r in ww)),
                       signed(st.mean(num(r["d_P0_pos"]) for r in ww)),
                       f"{sum(1 for r in ww if num(r['d_BYST_bands']) < -1)} of {len(ww)}",
                       f"{sum(1 for r in ww if num(r['d_P0_bands']) < -1)} of {len(ww)}"])
    print(write_table("table_A6_bystander", header, out + rows_b))


if __name__ == "__main__":
    main()
