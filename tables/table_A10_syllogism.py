#!/usr/bin/env python3
"""Table A.10: the syllogism, the structured prompt and the general principle, per model.

Written as the manuscript prints it: two header rows, the group row, the read models in
the data's order, then each unread model with its reason. The sampled DeepSeek row is a
check readout (counted 0), shown and marked "(check; not counted)".

Reads data/A10_syllogism.csv (one row per model: 13 read, and two listed as unread with
the reason) and data/A10_pooled.csv (the pooled figures the table's note quotes, each
with its paper_numbers id).

Fault blindness: Principle, the share answering "no" to the case-free principle question
(log-prob models: 1 - mean P(yes)); Fact, cells where the careful subject could not have
prevented the harm, of the cells read; Blames anyway, of the cells where both premises
hold, blame position above 0.10 (in brackets, above 0.30); One answer and Direct, median
blame position with fact, principle and verdict in one answer, and read directly.

Role blindness: G1 more in both orders; G2 yes share; G3 general gap; Named pairs on
which the convention is affirmed (of four, driving excluded); Alone, cells whose separate
gap is zero or below / within the wording floor / clear of it; Falls short, cells where
stated minus separate exceeds the combined floor; Structured, the median share of the
stated slack given under the structured prompt, and its class.
"""
import os
import sys
from decimal import Decimal, ROUND_HALF_UP

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from paperlib import read_csv, write_table, num, API_LABEL  # noqa: E402

CLASS = {"within a tenth": "within 0.1", "a tenth to three tenths short": "short 0.1\u20130.3",
         "more than three tenths short": "short > 0.3",
         "a tenth to three tenths over": "over 0.1\u20130.3",
         "more than three tenths over": "over > 0.3"}


def r2(v):
    if v is None:
        return ""
    q = Decimal(repr(round(v, 9))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return str(abs(q) if q == 0 else q)


CHECK = " (check; not counted)"
DASH = "\u2013"


def label(r):
    """The manuscript's row label; a read check readout (counted 0) is shown and marked.
    An unread model is not counted either, and carries its reason instead of the mark."""
    check = r["status"] == "READ" and r.get("counted", "1") != "1"
    return API_LABEL[r["arm"]] + (CHECK if check else "")


def main():
    rows = read_csv("A10_syllogism.csv")
    pooled = read_csv("A10_pooled.csv")
    header = ["Model", "Fault blindness (practical_syllogism)",
              "Role blindness (syllogism_duty and Amendment G)"]
    out = [["", "Principle", "Fact", "Blames anyway", "One answer", "Direct",
            "G1 more", "G2 yes", "G3 gap", "Named pairs",
            "Alone \u2264" "0 / within / clear", "Falls short", "Structured share",
            "Structured class"],
           ["Deployed, without reasoning"]]
    read_rows = [r for r in rows if r["status"] == "READ"]
    for r in read_rows:
        out.append([
            label(r), r2(num(r["principle_no_share"])),
            f"{r['fact_held']} of {r['fact_of']}",
            f"{r['blame_gt010']} ({r['blame_gt030']}) of {r['premises_held']}",
            r2(num(r["one_answer_median"])), r2(num(r["direct_median"])),
            "yes" if r["g1_both_orders"] == "1"
            else f"no ({r['g1_more_first']}, {r['g1_more_second']})",
            r2(num(r["g2_yes_share"])),
            r2(num(r["g3_general_gap"])) if r["g3_general_gap"] else "not measured",
            f"{r['named_pairs_held']} of {r['named_pairs_of']}",
            f"{r['alone_zero_or_below']} / {r['alone_within_floor']} / {r['alone_clear']}",
            f"{r['falls_short']} of {r['falls_short_cells']}",
            r2(num(r["structured_share"])) if r["structured_share"] else DASH,
            CLASS.get(r["structured_class"], DASH)])
    for r in rows:
        if r["status"] != "READ":
            why = r["unread_reason"]
            out.append([label(r), why[:1].upper() + why[1:]])
    notes = ["Pooled (paper_numbers id): " + "; ".join(
        f"{p['location']}: {p['printed']} ({p['paper_numbers_id']})" for p in pooled)]
    print(write_table("table_A10_syllogism", header, out, notes))


if __name__ == "__main__":
    main()
