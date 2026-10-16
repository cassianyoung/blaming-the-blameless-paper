#!/usr/bin/env python3
"""Table B.10: the duty test by model and pair.

Reads data/B10_duty_long.csv (one row per model and pair: the stated, side-by-side gap,
the gap with each case judged alone, the share of the stated slack given, and the gap
when the convention is stated) and data/B10_duty_arm.csv (one row per model: its order
in Figure 6, its wording and draw floors, and its signal-to-noise ratio). 21 models; the
model read on the side-by-side comparison only is not in the data (see
data/B10_excluded.csv).

Told carries its class against Stated, from the withheld share 1 - Told / Stated:
'=' within a tenth, '-' or '--' short by a tenth to three tenths or by more, '+' or '++'
over likewise. '–' marks a value with no reading: 'a' the stated gap does not clear the
wording floor, 'b' unread, 'c' the told reading was not returned. '†' marks a stated gap
whose two presentation orders differ by more than 1.0.
"""
import os
import sys
from decimal import Decimal, ROUND_HALF_UP

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from paperlib import read_csv, write_table, num, API_LABEL  # noqa: E402

PAIR = {"prawns": "Prawns", "1": "Electrical", "3": "Gas", "4": "Childcare",
        "5": "Driving", "7": "Hair dye"}
MARK = {"within a tenth": "=", "a tenth to three tenths short": "-",
        "more than three tenths short": "--", "a tenth to three tenths over": "+",
        "more than three tenths over": "++"}


def r2(v):
    """Two decimals, half up, from the value read at nine places (1.8249999999999997 is
    the mean 1.825)."""
    if v is None:
        return ""
    q = Decimal(repr(round(v, 9))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return str(abs(q) if q == 0 else q)


def main():
    long_ = read_csv("B10_duty_long.csv")
    arms = sorted(read_csv("B10_duty_arm.csv"), key=lambda a: int(a["fig6_rank"]))
    pairs = []
    for r in sorted(long_, key=lambda r: int(r["panel_order"])):
        if r["pair_id"] not in pairs:
            pairs.append(r["pair_id"])
    cell = {(r["arm"], r["pair_id"]): r for r in long_}
    header = (["Model", "Reasoning"]
              + [f"{PAIR[p]} {c}" for p in pairs for c in ("Stated", "Alone", "Share",
                                                           "Told")]
              + ["Wording floor", "Draw floor", "S/N"])
    out = []
    for title, rz in (("Deployed, without reasoning", "off"),
                      ("Deployed, with reasoning", "on")):
        out.append([title] + [""] * (len(header) - 1))
        for a in [a for a in arms if a["reasoning"] == rz]:
            row = [API_LABEL[a["arm"]], rz]
            for p in pairs:
                c = cell[(a["arm"], p)]
                s = num(c["stated_gap"])
                if s is None:
                    row += ["–b"] * 4
                    continue
                sp = num(c["order_spread"])
                row.append(r2(s) + ("†" if sp is not None and round(sp, 9) > 1.0 else ""))
                row.append(r2(num(c["separate_gap"])) or "–b")
                row.append(r2(num(c["share"])) or "–a")
                t = num(c["told_gap"])
                row.append("–c" if t is None else
                           (r2(t) + (" " + MARK[c["told_class"]] if c["told_class"]
                                     else "")))
            row += [r2(num(a["floor_sentence"])), r2(num(a["floor_draw"])),
                    r2(num(a["signal_to_noise"]))]
            out.append(row)
    notes = ["Gaps in points on the 0-9 scale, professional minus private person. "
             "Stated: side by side, mean of the two orders. Alone: each case judged on "
             "its own. Share: Alone / Stated. Told: the gap with the convention stated "
             "before each case, with its class against Stated. Ordered as Figure 6: "
             "within each group, by the mean over pairs of Stated minus Alone, largest "
             "first. S/N: median stated gap / wording floor (floored at 0.30)."]
    print(write_table("table_B10_duty_by_model", header, out, notes))


if __name__ == "__main__":
    main()
