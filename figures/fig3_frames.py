#!/usr/bin/env python3
"""Figure 3: the same instruction-tuned weights on the worksheet and in their own chat
template, per scenario.

Reads data/frame_by_scenario.csv: per family and scenario, the careful subject's position
on the worksheet (ws_P0_pos) and through the chat template (chat_P0_pos) from the same
load, the chat gate, and whether the chat careless case falls to or below the target case
(chat_C_below_P0, marked '†': positions there are not interpretable). A chat reading that
fails the gate is drawn faded. Values beyond the axis are drawn at the edge and labelled.

Writes figures/out/fig3_frames.png and figures/out/fig3_frames_values.csv.
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
from paperlib import (read_csv, num, FAMILY_LABEL, SCENARIOS,  # noqa: E402
                      BAND_GREEN, BAND_AMBER, BAND_RED)

ORDER = ["mistral", "gemma27", "llama31", "falcon3", "olmo2", "qwen3", "gemma9", "yi34b"]
TITLE = {"bicycle": "Bicycle", "ladder": "Ladder", "prawns_home": "Prawns, home",
         "prawns_restaurant": "Prawns, restaurant", "scaffolding": "Scaffolding",
         "cheque": "Cheque"}
BLUE, RED, FADED = "#2c5f9e", "#c0392b", "#e8b4b4"
XMIN, XMAX = -0.15, 1.15


def main():
    out = os.path.join(ROOT, "figures", "out")
    os.makedirs(out, exist_ok=True)
    cell = {(r["family"], r["scenario"]): r for r in read_csv("frame_by_scenario.csv")}
    fig, axes = plt.subplots(2, 3, figsize=(13, 8.6), sharey=True)
    values = []
    for ax, s in zip(axes.flat, SCENARIOS):
        ax.axvspan(XMIN, 0.10, color=BAND_GREEN, zorder=0)
        ax.axvspan(0.10, 0.30, color=BAND_AMBER, zorder=0)
        ax.axvspan(0.30, XMAX, color=BAND_RED, zorder=0)
        dagger = False
        for i, fam in enumerate(ORDER):
            y = len(ORDER) - 1 - i
            r = cell.get((fam, s))
            if r is None:
                continue
            ws, ch = num(r["ws_P0_pos"]), num(r["chat_P0_pos"])
            passed = r["chat_gate"] == "PASSED"
            inverted = r["chat_C_below_P0"] == "true"
            chx = min(max(ch, XMIN + 0.01), XMAX - 0.01)
            ax.plot([ws, chx], [y, y], color="#444444" if passed else FADED, lw=1.2,
                    zorder=1)
            ax.plot(ws, y, "o", color=BLUE, mec="white", ms=7, zorder=3)
            ax.plot(chx, y, "o", mfc="white", mec=RED if passed else FADED, mew=1.8,
                    ms=8, zorder=3)
            if chx != ch:
                ax.text(chx, y + 0.3, f"{ch:.2f}", color=RED, alpha=0.7, fontsize=7,
                        ha="center")
            if inverted:
                dagger = True
                ax.text(XMAX + 0.04, y, "†", color=RED, alpha=1 if passed else 0.4,
                        va="center", clip_on=False)
            values.append([s, FAMILY_LABEL[fam], round(ws, 4), round(ch, 4),
                           r["chat_gate"], r["chat_C_below_P0"]])
        ax.set_xlim(XMIN, XMAX)
        ax.set_xticks([0, 0.5, 1])
        ax.set_title(TITLE[s] + ("  († chat careless ≤ target)" if dagger
                                 and s == "ladder" else ""),
                     loc="left", fontweight="bold", fontsize=10)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
    for ax in axes[:, 0]:
        ax.set_yticks(range(len(ORDER)))
        ax.set_yticklabels([FAMILY_LABEL[f] for f in ORDER][::-1])
    fig.supxlabel("Careful subject's position on the model's own scale "
                  "(0 blameless, 1 careless)", fontsize=10, y=0.07)
    fig.legend(handles=[
        Line2D([], [], marker="o", ls="", color=BLUE, ms=7, label="worksheet"),
        Line2D([], [], marker="o", ls="", mfc="white", mec=RED, mew=1.8, ms=8,
               label="chat (same weights, same load)"),
        Line2D([], [], marker="o", ls="", mfc="white", mec=FADED, mew=1.8, ms=8,
               label="chat reading that fails the gate")],
        loc="lower center", ncol=3, frameon=False)
    fig.subplots_adjust(bottom=0.14, hspace=0.25, wspace=0.12)
    fig.savefig(os.path.join(out, "fig3_frames.png"), dpi=150)
    with open(os.path.join(out, "fig3_frames_values.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["scenario", "family", "worksheet_P0_pos", "chat_P0_pos",
                    "chat_gate", "chat_careless_at_or_below_target"])
        w.writerows(values)
    print(os.path.join(out, "fig3_frames.png"))


if __name__ == "__main__":
    main()
