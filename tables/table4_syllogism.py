#!/usr/bin/env python3
"""Table 4: the practical syllogism, per model, each step from its own call.

Reads data/table4_syllogism.csv (one row per model, then the pooled row "All models"):
the universal premise (the share asked with no case that says a person is not at fault
for a harm he could not reasonably have prevented), the particular premise (cases where
the model states the subject could not have prevented the harm), the conclusion not
drawn (of those, cases where it still blames), blames anyway (that share), and the
medians of the direct verdict and of the one-answer verdict, each a position on the
model's own scale. The pooled row prints counts over the twelve counted models and, beside
each median, the share of cells above 0.10. The sampled DeepSeek row is a check and is
not counted in the pooled row.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from paperlib import read_csv, write_table, num, f2  # noqa: E402

HEADER = ["Model", "Universal premise", "Particular premise", "Conclusion not drawn",
          "Blames anyway", "Direct verdict", "One answer"]


def pct(v):
    return f"{f2(100 * v, 0)}%"


def main():
    out = []
    for r in read_csv("table4_syllogism.csv"):
        g = lambda k: num(r[k])  # noqa: E731
        i = lambda k: int(g(k))  # noqa: E731
        if r["arm"] == "pooled":
            n = i("cells")
            out.append([r["model"], f"{i('universal')} of {i('universal_of')}",
                        f"{i('particular')} of {i('particular_of')}",
                        f"{i('not_drawn')} of {i('not_drawn_of')}", pct(g("blames_anyway")),
                        f"{f2(g('direct_median'))} "
                        f"({pct(g('direct_cells_gt010') / n)} above 0.10)",
                        f"{f2(g('one_answer_median'))} "
                        f"({pct(g('one_answer_cells_gt010') / n)} above 0.10)"])
        else:
            out.append([r["model"], pct(g("universal")),
                        f"{i('particular')} of {i('particular_of')}",
                        f"{i('not_drawn')} of {i('not_drawn_of')}", pct(g("blames_anyway")),
                        f2(g("direct_median")), f2(g("one_answer_median"))])
    print(write_table("table4_syllogism", HEADER, out))


if __name__ == "__main__":
    main()
