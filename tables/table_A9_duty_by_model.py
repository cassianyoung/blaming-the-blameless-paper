#!/usr/bin/env python3
"""Table A.9: the duty test by model and pair, written as its two printed panels
(table_A9A_duty_by_model: prawns, electrical, gas; table_A9B_duty_by_model: childcare,
driving, hair dye), each with its two header rows and the two group rows.

Reads data/A9_duty_long.csv (one row per model and pair: the stated, side-by-side gap,
the gap with each case judged alone, the share of the stated slack given, and the gap
when the convention is stated) and data/A9_duty_arm.csv (one row per model: its order
in Figure 6, its wording and draw floors, and its signal-to-noise ratio): 22 rows, the
21 counted models and the sampled DeepSeek readout, a check shown and marked "(check; not
counted)". Models left out are listed in data/A9_excluded.csv.

Told carries its class against Stated, from the withheld share 1 - Told / Stated:
'=' within a tenth, '-' or '--' short by a tenth to three tenths or by more, '+' or '++'
over likewise. '–' marks a value with no reading: 'a' the stated gap does not clear the
wording floor, 'b' unread, 'c' the told reading was not returned, 'd' unread because one
presentation order is void. Where the comparison is unread, Stated and Share carry the
mark, Alone and Told print if read, and Told's class is replaced by the mark. '†' marks a
stated gap whose two presentation orders differ by more than 1.0.
"""
import os
import sys
from decimal import Decimal, ROUND_HALF_UP

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from paperlib import read_csv, write_table, num, API_LABEL  # noqa: E402

PAIR = {"prawns": "Prawns", "1": "Electrical", "3": "Gas", "4": "Childcare",
        "5": "Driving", "7": "Hair dye"}
MARK = {"within a tenth": "=", "a tenth to three tenths short": "\u2212",
        "more than three tenths short": "\u2212\u2212", "a tenth to three tenths over": "+",
        "more than three tenths over": "++"}


def r2(v):
    """Two decimals, half up, from the value read at nine places (1.8249999999999997 is
    the mean 1.825)."""
    if v is None:
        return ""
    q = Decimal(repr(round(v, 9))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return str(abs(q) if q == 0 else q)


CHECK = " (check; not counted)"
DASH = "\u2013"
MARKS = {"floor": "a", "unread": "b", "told": "c", "void": "d"}


def label(a):
    """The manuscript's row label; a check readout (counted 0) is shown and marked."""
    return API_LABEL[a["arm"]] + ("" if a.get("counted", "1") == "1" else CHECK)


def pair_cells(c):
    """Stated, Alone, Share, Told for one model and pair, as printed."""
    s = num(c["stated_gap"])
    al = num(c["separate_gap"])
    alone = r2(al) if al is not None else DASH + MARKS["unread"]
    t = num(c["told_gap"])
    if s is None:
        # comparison unread: Stated and Share carry the mark (-d where one presentation
        # order is void, -b otherwise); Alone and Told print if read, Told's class (which
        # needs Stated) replaced by the mark
        mk = DASH + MARKS["void" if "VOID" in (c["share_reason"] or "") else "unread"]
        return [mk, alone, mk, (r2(t) + " " + mk) if t is not None else DASH + MARKS["told"]]
    sp = num(c["order_spread"])
    stated = r2(s) + ("\u2020" if sp is not None and round(sp, 9) > 1.0 else "")
    sh = num(c["share"])
    share = r2(sh) if sh is not None else DASH + MARKS["floor"]
    if t is None:
        told = DASH + MARKS["told"]
    else:
        mk = MARK.get(c["told_class"], "")
        told = r2(t) + (" " + mk if mk else "")
    return [stated, alone, share, told]


def main():
    long_ = read_csv("A9_duty_long.csv")
    arms = sorted(read_csv("A9_duty_arm.csv"), key=lambda a: int(a["fig6_rank"]))
    pairs = []
    for r in sorted(long_, key=lambda r: int(r["panel_order"])):
        if r["pair_id"] not in pairs:
            pairs.append(r["pair_id"])
    cell = {(r["arm"], r["pair_id"]): r for r in long_}
    notes = ["Gaps in points on the 0-9 scale, professional minus private person. "
             "Stated: side by side, mean of the two orders. Alone: each case judged on "
             "its own. Share: Alone / Stated. Told: the gap with the convention stated "
             "before each case, with its class against Stated. Ordered as Figure 6: "
             "within each group, by the mean over pairs of Stated minus Alone, largest "
             "first. S/N: median stated gap / wording floor (floored at 0.30)."]
    for stem, chunk in (("table_A9A_duty_by_model", pairs[:3]),
                        ("table_A9B_duty_by_model", pairs[3:])):
        header = ["Model"] + [PAIR[p] for p in chunk] + ["Wording floor", "Draw floor", "S/N"]
        out = [[""] + ["Stated", "Alone", "Share", "Told"] * len(chunk)]
        for title, rz in (("Deployed, without reasoning", "off"),
                          ("Deployed, with reasoning", "on")):
            out.append([title])
            for a in [a for a in arms if a["reasoning"] == rz]:
                row = [label(a)]
                for p in chunk:
                    row += pair_cells(cell[(a["arm"], p)])
                row += [r2(num(a["floor_sentence"])), r2(num(a["floor_draw"])),
                        r2(num(a["signal_to_noise"]))]
                out.append(row)
        print(write_table(stem, header, out, notes))


if __name__ == "__main__":
    main()
