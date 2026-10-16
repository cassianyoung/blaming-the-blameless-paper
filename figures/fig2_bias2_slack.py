#!/usr/bin/env python3
"""Figure 2 (Bias 2): the share of its own stated slack each deployed model withholds.

Reads data/fig7_duty.csv, one row per model and professional-against-private pair. For
each pair the model states a gap when the two cases are scored side by side
(stated_gap) and gives a gap when each case is judged alone (separate_gap); `share` is
the separate gap over the stated gap, carried on the pairs where the model states a
convention. Per model, over those pairs:

  withheld, judged alone (filled)       1 - median(share)
  withheld, convention stated (open)    1 - median(stated_condition_gap / stated_gap)

0: the model applies all the slack it states; 1: it gives none; below 0: told the
convention, it gives more than it states. A model with no separate-case reading has no
share and is not drawn.

Writes figures/out/fig2_bias2_slack.png and figures/out/fig2_bias2_slack_values.csv.
"""
import csv
import os
import statistics as st
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from paperlib import (read_csv, num, API_LABEL, BAND_GREEN, BAND_AMBER,  # noqa: E402
                      BAND_RED)

PURPLE, GREEN = "#6a3d9a", "#2e7d32"
XMIN, XMAX = -1.3, 1.05


def per_model():
    rows = read_csv("fig7_duty.csv")
    out = {}
    for r in rows:
        if num(r["share"]) is None:
            continue
        d = out.setdefault(r["arm"], {"reasoning": r["reasoning"], "share": [],
                                      "sc": []})
        d["share"].append(num(r["share"]))
        sc, sg = num(r["stated_condition_gap"]), num(r["stated_gap"])
        if sc is not None and sg:
            d["sc"].append(sc / sg)
    res = []
    for arm, d in out.items():
        res.append({"arm": arm, "reasoning": d["reasoning"],
                    "alone": 1 - st.median(d["share"]),
                    "stated": 1 - st.median(d["sc"]) if d["sc"] else None,
                    "n_pairs": len(d["share"])})
    return res


def label(arm, reasoning):
    base = API_LABEL[arm]
    return base + (" (reasoning)" if reasoning == "on" else "")


def main():
    out = os.path.join(ROOT, "figures", "out")
    os.makedirs(out, exist_ok=True)
    res = per_model()
    off = sorted([r for r in res if r["reasoning"] == "off"], key=lambda r: -r["alone"])
    on = sorted([r for r in res if r["reasoning"] == "on"], key=lambda r: -r["alone"])
    rows = off + on
    n = len(rows)
    fig, ax = plt.subplots(figsize=(12, 9.6))
    ax.axvspan(XMIN, -0.30, facecolor=BAND_RED, hatch="///", edgecolor="#e8a0a0",
               lw=0, zorder=0)
    ax.axvspan(-0.30, -0.10, color=BAND_AMBER, zorder=0)
    ax.axvspan(-0.10, 0.10, color=BAND_GREEN, zorder=0)
    ax.axvspan(0.10, 0.30, color=BAND_AMBER, zorder=0)
    ax.axvspan(0.30, XMAX, color=BAND_RED, zorder=0)
    for i, r in enumerate(rows):
        y = n - 1 - i
        col = GREEN if r["reasoning"] == "on" else PURPLE
        if r["stated"] is not None:
            ax.annotate("", xy=(r["stated"] + 0.03, y), xytext=(r["alone"], y),
                        arrowprops=dict(arrowstyle="-|>", color="#444444", lw=1.4,
                                        shrinkA=4, shrinkB=0))
            ax.plot(r["stated"], y, "o", mfc="white", mec="#444444", mew=1.6, ms=9,
                    zorder=4)
        ax.plot(r["alone"], y, "o", color=col, mec="white", ms=9, zorder=4)
    ax.axhline(len(on) - 0.5, color="#999999", ls="--", lw=0.8)
    ax.set_yticks(range(n))
    ax.set_yticklabels([label(r["arm"], r["reasoning"]) for r in rows][::-1])
    ax.set_xlim(XMIN, XMAX)
    ax.set_xticks([-1, -0.5, 0, 0.25, 0.5, 0.75, 1])
    ax.set_xticklabels(["−1\ndouble", "−0.5", "0\napplies all", "0.25", "0.5", "0.75",
                        "1\nwithholds all"])
    ax.set_xlabel("Share of the model's own stated slack it withholds")
    ax.set_title("Deployed models (chat): convention unstated → stated",
                 fontweight="bold")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.legend(handles=[
        Line2D([], [], marker="o", ls="", color=PURPLE, ms=9,
               label="Private person judged alone,\nwithout reasoning"),
        Line2D([], [], marker="o", ls="", color=GREEN, ms=9,
               label="Private person judged alone,\nwith reasoning"),
        Line2D([], [], marker="o", ls="", mfc="white", mec="#444444", ms=9,
               label="Convention stated\nin the prompt")],
        title="Markers", loc="upper right", bbox_to_anchor=(0.99, 0.9), frameon=False)
    fig.legend(handles=[
        Patch(facecolor=BAND_GREEN, edgecolor="#aaaaaa",
              label="Applies its convention: within\na tenth of the slack it states"),
        Patch(facecolor=BAND_AMBER, edgecolor="#aaaaaa",
              label="A tenth to three tenths off,\ntoo little (right) or too much (left)"),
        Patch(facecolor=BAND_RED, edgecolor="#aaaaaa",
              label="Withholds more than\nthree tenths of it"),
        Patch(facecolor=BAND_RED, edgecolor="#e8a0a0", hatch="///",
              label="Overshoots: gives more than three\ntenths more than it states")],
        title="Background", loc="upper right", bbox_to_anchor=(0.99, 0.55),
        frameon=False)
    fig.subplots_adjust(left=0.2, right=0.68, bottom=0.1)
    fig.savefig(os.path.join(out, "fig2_bias2_slack.png"), dpi=150)
    with open(os.path.join(out, "fig2_bias2_slack_values.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["model", "reasoning", "withheld_alone", "withheld_stated",
                    "n_pairs"])
        for r in rows:
            w.writerow([label(r["arm"], r["reasoning"]), r["reasoning"],
                        round(r["alone"], 4),
                        "" if r["stated"] is None else round(r["stated"], 4),
                        r["n_pairs"]])
    print(os.path.join(out, "fig2_bias2_slack.png"))


if __name__ == "__main__":
    main()
