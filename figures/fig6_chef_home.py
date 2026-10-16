#!/usr/bin/env python3
"""Figure 6: slack for the private host, stated and given.

Reads data/chef_home.csv and data/chef_home_cmp3_probabilities.csv, deployed (API) arms.
Each row is the careless chef's blame minus the careless home cook's on the 0-9 scale:
scored side by side (square, the stated gap) and judged as separate cases (triangle, the
applied gap). Right-hand columns: the one-word comparison, P(chef) - P(home) averaged
over the two orders, the two gaps, and the separate gap as a share of the paired gap,
coloured green at two thirds or more, amber one to two thirds, red under a third. The
share is read from the data and is withheld ("within floor") where the paired gap does
not clear the model's wording floor.
Annotated values use Python's two-decimal float formatting.

Writes figures/out/fig6_chef_home.png and figures/out/fig6_chef_home_values.csv.
"""
import csv
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402
from matplotlib.transforms import blended_transform_factory  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from paperlib import read_csv, num, API_LABEL  # noqa: E402

BLUE, ORANGE = "#2c5f9e", "#e08a00"
C_GREEN, C_AMBER, C_RED = "#c8ecd0", "#fde9a6", "#f2b8b0"


def word(s):
    return s.split(" (")[0]


def main():
    out = os.path.join(ROOT, "figures", "out")
    os.makedirs(out, exist_ok=True)
    rows = [r for r in read_csv("chef_home.csv") if r["source"] == "api"]
    probs = {}
    for p in read_csv("chef_home_cmp3_probabilities.csv"):
        probs.setdefault(p["model"], []).append(num(p["p_chef"]) - num(p["p_home"]))

    def lab(r):
        on = r["reasoning"].startswith("on")
        mark = (" ‡" if r["cmp3_first_listed_both_orders"] == "true" else
                " §" if r["cmp3_last_listed_both_orders"] == "true" else "")
        return API_LABEL[r["model"]] + (" (reasoning)" if on else "") + mark

    off = sorted([r for r in rows if not r["reasoning"].startswith("on")],
                 key=lambda r: (-num(r["stated_gap_digits"]), lab(r).lower()))
    on = sorted([r for r in rows if r["reasoning"].startswith("on")],
                key=lambda r: (-num(r["stated_gap_digits"]), lab(r).lower()))
    layout = [("Deployed, without reasoning", None)] + [(None, r) for r in off] + \
             [("", None), ("Deployed, with reasoning", None)] + [(None, r) for r in on]
    n = len(layout)
    fig = plt.figure(figsize=(14, 9.4))
    ax = fig.add_axes([0.16, 0.14, 0.43, 0.78])
    ax.set_ylim(-0.7, n - 0.3)
    tr = blended_transform_factory(ax.transAxes, ax.transData)
    values = []
    ylabels, yt = [], []
    for i, (title, r) in enumerate(layout):
        y = n - 1 - i
        if title:
            ax.text(-0.95, y, title, fontweight="bold", va="center")
            continue
        if r is None:
            continue
        st_, sep = num(r["stated_gap_digits"]), num(r["careless_gap_digits"])
        if sep is not None:
            ax.annotate("", xy=(sep + 0.06, y), xytext=(st_, y),
                        arrowprops=dict(arrowstyle="-|>", color="#888888", lw=1.2,
                                        shrinkA=5, shrinkB=0))
            ax.plot(sep, y, "^", color=ORANGE, ms=10, zorder=4)
        ax.plot(st_, y, "s", color=BLUE, ms=9, zorder=4)
        yt.append(y)
        ylabels.append(lab(r))
        a, b = word(r["cmp3_answer_home_first"]), word(r["cmp3_answer_chef_first"])
        oneword = a if a == b else f"{a}/{b}"
        d = probs[r["model"]]
        pdiff = sum(d) / len(d)
        cols = [(oneword, None), (f"{pdiff:+.2f}", None), (f"{st_:+.2f}", None)]
        # the share is read from the data, where it is withheld if the paired gap
        # does not clear the model's wording floor, as in Figures 2 and 7
        share = num(r["share"])
        if sep is None:
            cols += [("—", None), ("—", None)]
        elif share is None:
            cols += [(f"{sep:+.2f}", None), ("within\nfloor", None)]
        else:
            c = C_GREEN if share >= 2 / 3 else C_AMBER if share >= 1 / 3 else C_RED
            cols += [(f"{sep:+.2f}", c), (f"{share * 100:.0f}%", c)]
        for k, (txt, c) in enumerate(cols):
            ax.text(1.12 + 0.15 * k, y, txt, transform=tr, ha="center",
                    va="center", fontsize=9, clip_on=False,
                     bbox=None if c is None else dict(boxstyle="round,pad=0.25",
                                                      fc=c, ec="none"))
        values.append([lab(r), oneword, round(pdiff, 4), st_,
                       "" if sep is None else sep,
                       "" if share is None else round(share, 4)])
    for k, h in enumerate(["One-word\nanswer", "P(chef) −\nP(home)", "Paired\nscores",
                           "Separate\ncases", "Separate ÷\npaired"]):
        ax.text(1.12 + 0.15 * k, n - 0.3, h, transform=tr, ha="center",
                va="bottom", fontsize=9, fontweight="bold", clip_on=False)
    ax.axvline(0, color="#222222", lw=1)
    ax.set_xlim(-1.0, 3.0)
    ax.set_yticks(yt)
    ax.set_yticklabels(ylabels, fontsize=9)
    ax.set_xlabel("Careless chef − careless home cook, blame on the 0–9 scale")
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    fig.legend(handles=[
        Line2D([], [], marker="s", ls="", color=BLUE, ms=8,
               label="asked side by side (stated)"),
        Line2D([], [], marker="^", ls="", color=ORANGE, ms=9,
               label="judged as separate cases (applied)"),
        Patch(fc=C_GREEN, label="separate ≥ ⅔ of stated"),
        Patch(fc=C_AMBER, label="⅓–⅔ of stated"),
        Patch(fc=C_RED, label="< ⅓ of stated")],
        loc="lower left", bbox_to_anchor=(0.14, 0.0), ncol=3, frameon=False,
        fontsize=9)
    fig.savefig(os.path.join(out, "fig6_chef_home.png"), dpi=150)
    with open(os.path.join(out, "fig6_chef_home_values.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["model", "one_word", "p_chef_minus_p_home", "stated_gap",
                    "separate_gap", "separate_over_paired"])
        w.writerows(values)
    print(os.path.join(out, "fig6_chef_home.png"))


if __name__ == "__main__":
    main()
