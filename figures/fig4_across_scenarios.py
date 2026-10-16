#!/usr/bin/env python3
"""Figure 4: deployed models across six scenarios.

Reads data/B5_across_scenarios_wide.csv: per model and scenario, the careful subject with
nothing stated (P0, filled; red without reasoning, green with) and with "nothing anyone
could have done" added (P1, open), as positions on the model's own scale, and the gate
verdict. A scenario that fails the model's gate is drawn faded. Where P0 and P1
coincide, P1 is drawn as a ring around P0.

Writes figures/out/fig4_across_scenarios.png and the plotted values as a CSV.
"""
import csv
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from paperlib import (read_csv, num, API_LABEL, SCENARIOS, SCENARIO_LABEL,  # noqa
                      BAND_GREEN, BAND_AMBER, BAND_RED)

OFF = ["gpt4o", "gpt6s_s", "gpt6l_s", "claude", "haiku_s", "qwen235b", "qwen80b",
       "qwen30b", "deepseek", "deepseek_s", "gemma27b", "llama70b", "mistral24b",
       "grok43_s", "kimi"]
ON = ["gpt6s_r", "gpt6l_r", "haiku_r", "deepseek_r_mt8192", "gemini_r", "grok43_r"]
RED, GREEN, FADED = "#c0392b", "#2e7d32", "#e8b4b4"
XMIN, XMAX = -0.3, 1.0


def main():
    out = os.path.join(ROOT, "figures", "out")
    os.makedirs(out, exist_ok=True)
    by = {r["model"]: r for r in read_csv("B5_across_scenarios_wide.csv")}
    arms = OFF + ON
    labels = [API_LABEL[a] + (" (R)" if a in ON else "") for a in arms]
    n = len(arms)
    fig, axes = plt.subplots(2, 3, figsize=(13, 13), sharey=True)
    values = []
    for ax, s in zip(axes.flat, SCENARIOS):
        ax.axvspan(XMIN, 0.10, color=BAND_GREEN, zorder=0)
        ax.axvspan(0.10, 0.30, color=BAND_AMBER, zorder=0)
        ax.axvspan(0.30, XMAX, color=BAND_RED, zorder=0)
        for i, arm in enumerate(arms):
            y = n - 1 - i
            r = by[arm]
            p0, p1 = num(r[f"{s}_P0"]), num(r[f"{s}_P1"])
            if p0 is None:
                ax.text(0.02, y, "no reading", fontsize=7, color="#888888",
                        va="center")
                continue
            ok = r[f"{s}_gate"] == "PASSED"
            col = (GREEN if arm in ON else RED) if ok else FADED
            ring = "#444444" if ok else FADED
            if p1 is not None and abs(p0 - p1) >= 0.03:
                ax.plot([p0, p1], [y, y], color="#666666" if ok else FADED, lw=1,
                        zorder=1)
                ax.plot(p1, y, "o", mfc="white", mec=ring, mew=1.3, ms=7, zorder=3)
                ax.plot(p0, y, "o", color=col, mec="white", ms=6, zorder=4)
            else:
                if p1 is not None:
                    ax.plot(p1, y, "o", mfc="white", mec=ring, mew=1.3, ms=11, zorder=3)
                ax.plot(p0, y, "o", color=col, mec="white", ms=6, zorder=4)
            values.append([s, API_LABEL[arm], "on" if arm in ON else "off",
                           round(p0, 4), "" if p1 is None else round(p1, 4),
                           r[f"{s}_gate"]])
        ax.axhline(len(ON) - 0.5, color="#999999", ls="--", lw=0.7)
        ax.set_xlim(XMIN, XMAX)
        ax.set_xticks([0, 0.5, 1])
        ax.set_title(SCENARIO_LABEL[s], loc="left", fontweight="bold", fontsize=10)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
    for ax in axes[:, 0]:
        ax.set_yticks(range(n))
        ax.set_yticklabels(labels[::-1], fontsize=8)
    fig.supxlabel("Careful subject's position on the model's own scale "
                  "(0 blameless, 1 careless)", fontsize=10, y=0.05)
    fig.legend(handles=[
        Line2D([], [], marker="o", ls="", color=RED, ms=6,
               label="careful subject, without reasoning"),
        Line2D([], [], marker="o", ls="", color=GREEN, ms=6,
               label="careful subject, with reasoning (R)"),
        Line2D([], [], marker="o", ls="", mfc="white", mec="#444444", ms=7,
               label="excuse stated: \"nothing anyone could have done\""),
        Line2D([], [], marker="o", ls="", color=FADED, ms=6,
               label="fails the gate on that scenario")],
        loc="lower center", ncol=4, frameon=False, fontsize=8)
    fig.subplots_adjust(left=0.14, bottom=0.1, hspace=0.12, wspace=0.08)
    fig.savefig(os.path.join(out, "fig4_across_scenarios.png"), dpi=150)
    with open(os.path.join(out, "fig4_across_scenarios_values.csv"), "w",
              newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["scenario", "model", "reasoning", "P0_pos", "P1_pos", "gate"])
        w.writerows(values)
    print(os.path.join(out, "fig4_across_scenarios.png"))


if __name__ == "__main__":
    main()
