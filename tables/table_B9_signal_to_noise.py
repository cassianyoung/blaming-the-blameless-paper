#!/usr/bin/env python3
"""Table B.9: signal-to-noise for the duty test, per arm and pair.

Reads data/B9_signal_to_noise_long.csv (one row per arm and pair: the stated,
side-by-side gap divided by the arm's sentence-noise floor, signed) and
data/B9_signal_to_noise_arm.csv (the per-arm median over its pairs). 21 arms; the arm
read on the side-by-side comparison only is not in the data (see data/B9_excluded.csv).
'—' marks a pair with no stated gap; '*' marks a pair the arm states no convention on.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from paperlib import read_csv, write_table, num, f2, API_LABEL  # noqa: E402


def main():
    long_ = read_csv("B9_signal_to_noise_long.csv")
    arms = read_csv("B9_signal_to_noise_arm.csv")
    pairs = []
    for r in sorted(long_, key=lambda r: int(r["panel_order"])):
        if (r["pair_id"], r["pair_label"]) not in pairs:
            pairs.append((r["pair_id"], r["pair_label"]))
    cell = {(r["arm"], r["pair_id"]): r for r in long_}
    header = (["Model", "Reasoning", "Floor used, digits"]
              + [lab for _, lab in pairs] + ["Median", "Pairs"])
    out = []
    for title, rz in (("Deployed, without reasoning", "off"),
                      ("Deployed, with reasoning", "on")):
        out.append([title] + [""] * (len(header) - 1))
        for a in [a for a in arms if a["reasoning"] == rz]:
            arm = a["arm"]
            row = [API_LABEL[arm], rz,
                   f2(num(cell[(arm, pairs[0][0])]["floor_used"]))]
            for pid, _ in pairs:
                c = cell[(arm, pid)]
                v = num(c["signal_to_noise"])
                if v is None:
                    row.append("—")
                else:
                    row.append(f2(v, 1) + ("" if c["convention_stated"] == "1" else "*"))
            row += [f2(num(a["median_signal_to_noise"]), 1),
                    str(int(num(a["n_pairs"])))]
            out.append(row)
    notes = ["Signal-to-noise: the gap the model states when the professional and the "
             "private person are scored side by side, divided by the model's sentence-"
             "noise floor (what an innocuous change of wording moves its verdict by, "
             "floored at 0.30 digits). Signed: a negative value is a stated gap "
             "pointing the other way. *: the stated gap does not clear the floor, so no "
             "convention is stated. —: the comparison was not read."]
    print(write_table("table_B9_signal_to_noise", header, out, notes))


if __name__ == "__main__":
    main()
