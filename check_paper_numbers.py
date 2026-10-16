#!/usr/bin/env python3
"""Check paper_numbers.csv against the CSVs in data/.

paper_numbers.csv lists numbers registered against the manuscript with their location,
the printed form, the query that produced them (documentation only; the database is not
distributed) and the value at build time. For each number:

  1. The printed form is parsed to a number and its printed precision (decimal places).
     A printed form with no number (a word, or '—' for an absence) is NOT CHECKABLE.
  2. The value at build is located in data/: a CSV cell locates it when the two agree
     to the cell's own precision (half a unit in the cell's last decimal place, and at
     most 5e-5). Whole-number values (counts) are not located by value, because a count
     matches unrelated cells; they are NOT CHECKABLE from the CSVs.
  3. A located number PASSES when some locating cell agrees with the printed number:
     rounding some value within the cell's own rounding interval half-up to the
     printed precision gives the printed number (or, where the printed form is more
     precise than the cell, the printed number lies within that interval). It FAILS
     when no locating cell agrees.
     A number no cell locates is NOT CHECKABLE.

A pass on a value of exactly 0 or 1 is reported as WEAK, because such values occur in
many unrelated cells. Writes check_paper_numbers_report.csv beside this file and prints
a summary. Exit status 1 when any located number fails.
"""
import csv
import os
import re
import sys
from decimal import Decimal, ROUND_HALF_UP

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
NUM = re.compile(r"[-+−]?\d+(?:\.\d+)?")


def rows(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(l for l in fh if not l.startswith("#")))


def parse_printed(s):
    m = NUM.search((s or "").replace("−", "-"))
    if not m:
        return None, None
    t = m.group(0)
    return float(t), (len(t.split(".")[1]) if "." in t else 0)


def parse_value(s):
    m = NUM.search((s or "").replace("−", "-"))
    return float(m.group(0)) if m else None


def round_half_up(v, nd):
    q = Decimal(1).scaleb(-nd)
    return float(Decimal(repr(v)).quantize(q, rounding=ROUND_HALF_UP))


def agrees(cell, p, nd):
    """Does the printed number fit this cell, given both precisions?

    The cell stands for any value within its own rounding interval; the printed number
    agrees when rounding some value in that interval to the printed precision gives it.
    Where the printed form is more precise than the cell, the printed number is rounded
    to the cell's precision instead.
    """
    v, tol = cell[0], cell[1]
    lo, hi = round_half_up(v - tol, nd), round_half_up(v + tol, nd)
    if lo <= p <= hi:
        return True
    return abs(p - v) <= tol


def data_cells():
    cells = []
    for name in sorted(os.listdir(DATA)):
        if not name.endswith(".csv"):
            continue
        for i, r in enumerate(rows(os.path.join(DATA, name))):
            for col, txt in r.items():
                if txt is None:
                    continue
                t = txt.strip()
                if not re.fullmatch(r"[-+]?\d+(?:\.\d+)?(?:e[-+]?\d+)?", t):
                    continue
                v = float(t)
                nd = len(t.split(".")[1]) if ("." in t and "e" not in t) else 0
                tol = min(0.5 * 10 ** (-nd), 5e-5) if nd else 5e-5
                cells.append((v, tol, name, i + 1, col))
    return cells


def main():
    cells = data_cells()
    pn = rows(os.path.join(ROOT, "paper_numbers.csv"))
    report, counts = [], {"PASS": 0, "PASS (weak)": 0, "FAIL": 0, "NOT CHECKABLE": 0}
    for r in pn:
        p, nd = parse_printed(r["printed"])
        v = parse_value(r["value_at_build"])
        status, where, why = "NOT CHECKABLE", "", ""
        if p is None or v is None:
            why = "printed form or value carries no number"
        elif float(v).is_integer() and abs(v) > 1:
            why = "a whole-number count is not located by value"
        else:
            hits = [c for c in cells if abs(c[0] - v) <= c[1]]
            if not hits:
                why = "no CSV cell carries this value"
            else:
                good = [c for c in hits if agrees(c, p, nd)]
                if good:
                    c = good[0]
                    status = "PASS (weak)" if v in (0.0, 1.0, -1.0) else "PASS"
                    where = f"{c[2]} row {c[3]} column {c[4]}"
                    why = f"{len(good)} locating cell(s) agree at {nd} dp"
                else:
                    c = hits[0]
                    status = "FAIL"
                    where = f"{c[2]} row {c[3]} column {c[4]}"
                    why = (f"located value {c[0]} rounds to "
                           f"{round_half_up(c[0], nd)}, printed {p}")
        counts[status] += 1
        report.append([r["id"], r["location"], r["printed"], r["value_at_build"],
                       status, where, why])
    with open(os.path.join(ROOT, "check_paper_numbers_report.csv"), "w",
              newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "location", "printed", "value_at_build", "status",
                    "located_in", "detail"])
        w.writerows(report)
    checkable = counts["PASS"] + counts["PASS (weak)"] + counts["FAIL"]
    print(f"  {len(pn)} numbers in paper_numbers.csv")
    print(f"  checkable from data/: {checkable}")
    print(f"    pass {counts['PASS']}, pass on a 0 or 1 value (weak) "
          f"{counts['PASS (weak)']}, fail {counts['FAIL']}")
    print(f"  not checkable from the CSVs: {counts['NOT CHECKABLE']}")
    for row in report:
        if row[4] == "FAIL":
            print(f"    FAIL id {row[0]}: {row[1]}: {row[6]}")
    return 1 if counts["FAIL"] else 0


if __name__ == "__main__":
    sys.exit(main())
