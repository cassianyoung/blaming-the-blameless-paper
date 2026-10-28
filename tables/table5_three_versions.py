#!/usr/bin/env python3
"""Table 5: positions on the worksheet across the three versions, nine families.

Reads data/A6_bystander_long.csv: for each version (pretrained base, after the study
adapter, after developer post-training), the mean over the nine families and six scenarios
(54 pairs) of the uninvolved bystander's position and of the careful subject's. The two
smaller Yi base models, read as base models only, are left out, as in Table A.6's panel B.
Each mean is paper_numbers.csv ids 1123 to 1128.

Writes tables/out/table5_three_versions.csv: the manuscript's header and two rows.
"""
import os
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from paperlib import read_csv, write_table, num, f2  # noqa: E402

BASE_ONLY = ["yi9b", "yi6b"]
VERSIONS = ["base", "adapter", "instruct"]


def main():
    long_ = read_csv("A6_bystander_long.csv")
    header = ["Position on the worksheet, nine families", "Base",
              "After the study adapter", "After developer post-training"]
    rows = []
    for label, col in (("The uninvolved bystander", "BYST_pos"),
                       ("The careful subject", "P0_pos")):
        row = [label]
        for v in VERSIONS:
            vals = [num(r[col]) for r in long_
                    if r["version"] == v and r["family"] not in BASE_ONLY]
            if len(vals) != 54:
                raise SystemExit(f"{v} {col}: {len(vals)} pairs, expected 54 (9 x 6)")
            row.append(f2(st.mean(vals)))
        rows.append(row)
    print(write_table("table5_three_versions", header, rows))


if __name__ == "__main__":
    main()
