#!/usr/bin/env python3
"""Figure 2 (methods): re-scaling raw readings, on Mistral-Small-24B's bicycle cases.

Reads data/B2_deployed_bicycle.csv (row mistral24b): blame for the blameless (N),
careless (C), deliberate (I) and target (P0) cases on the 0-9 scale, and shows P0's
position on the model's own scale, (P0 - N)/(C - N).

Writes figures/out/fig2_rescaling.png and figures/out/fig2_rescaling_values.csv.
"""
import csv
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from paperlib import read_csv, num, f2  # noqa: E402

ARM = "mistral24b"
COL = {"N": "#2e7d32", "P0": "#c0392b", "C": "#b8740a", "I": "#5b2a86"}


def main():
    out = os.path.join(ROOT, "figures", "out")
    os.makedirs(out, exist_ok=True)
    r = next(x for x in read_csv("B2_deployed_bicycle.csv") if x["model"] == ARM)
    v = {k: num(r[k]) for k in ("N", "C", "I", "P0")}
    pos = (v["P0"] - v["N"]) / (v["C"] - v["N"])
    fig, ax = plt.subplots(figsize=(10, 6.3))
    ax.set_xlim(-0.8, 9.6)
    ax.set_ylim(-1.2, 6.2)
    ax.axis("off")
    y = 5.0
    ax.add_patch(plt.Rectangle((0, y - 0.12), 9, 0.24, fc="#f2f2f2", ec="#888888"))
    for t in range(10):
        ax.plot([t, t], [y - 0.12, y - 0.2], color="#888888", lw=0.8)
        ax.text(t, y - 0.42, str(t), ha="center", color="#888888")
    ax.text(-0.75, y, "Blame\n(0–9)", va="center")
    names = {"N": "blameless case\n(careful, no harm)",
             "P0": "target case\n(careful, hidden flaw, harm)",
             "C": "careless case", "I": "deliberate case"}
    for k in ("N", "P0", "C", "I"):
        ax.plot([v[k], v[k]], [y - 0.25, y + 0.4], color=COL[k], lw=2)
        ax.plot(v[k], y, "o", color=COL[k], mec="white", ms=8)
        ax.text(v[k], y + 0.95, names[k], ha="center", fontsize=8.5)
        ax.text(v[k], y + 0.6, f"{k} = {f2(v[k])}", ha="center", color=COL[k],
                fontweight="bold")
    for k, yy in (("P0", 3.6), ("C", 2.9)):
        ax.plot([v["N"], v["N"], v[k], v[k]], [yy + 0.12, yy, yy, yy + 0.12],
                color=COL[k], lw=1.5)
        ax.text((v["N"] + v[k]) / 2, yy - 0.3,
                f"{k} − N = {f2(v[k] - v['N'])}", ha="center", color=COL[k])
    ax.text(4.0, 2.0, f"position of P0  =  (P0 − N) / (C − N)  =  "
                      f"{f2(v['P0'] - v['N'])} / {f2(v['C'] - v['N'])}  =  {f2(pos)}",
            ha="center", fontsize=13)
    yb = 0.2
    ax.plot([v["N"], v["C"]], [yb, yb], color="#222222", lw=1.8)
    for t in (0, 0.25, 0.5, 0.75, 1):
        x = v["N"] + t * (v["C"] - v["N"])
        ax.plot([x, x], [yb - 0.1, yb + 0.1], color="#222222")
        ax.text(x, yb - 0.4, f"{t:g}", ha="center")
    xp = v["N"] + pos * (v["C"] - v["N"])
    ax.plot(xp, yb, "o", color=COL["P0"], mec="white", ms=9)
    ax.text(xp, yb - 0.95, f"P0 at {f2(pos)}", ha="center", color=COL["P0"],
            fontweight="bold")
    ax.text(-0.75, yb, "Model's own\nscale", va="center")
    ax.text(v["N"], yb + 0.5, "0 = treated as blameless (N)", color=COL["N"], fontsize=8.5)
    ax.text(v["C"], yb + 0.5, "1 = treated as careless (C)", color=COL["C"], fontsize=8.5,
            ha="right")
    fig.savefig(os.path.join(out, "fig2_rescaling.png"), dpi=150, bbox_inches="tight")
    with open(os.path.join(out, "fig2_rescaling_values.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["quantity", "value"])
        for k in ("N", "P0", "C", "I"):
            w.writerow([k, round(v[k], 4)])
        w.writerow(["P0 - N", round(v["P0"] - v["N"], 4)])
        w.writerow(["C - N", round(v["C"] - v["N"], 4)])
        w.writerow(["P0 position", round(pos, 4)])
    print(os.path.join(out, "fig2_rescaling.png"))


if __name__ == "__main__":
    main()
