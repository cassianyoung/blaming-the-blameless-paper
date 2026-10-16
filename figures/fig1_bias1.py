#!/usr/bin/env python3
"""Figure 1: Bias 1 effect sizes, the careful subject's position on each model's own scale.

Panel A reads data/fig1_panelA.csv: the nine pretrained base models on the worksheet,
the careful subject (P0) with its 95% interval, the uninvolved bystander, and a tick where
the careful subject exceeds the bystander by more than two noise bands.
Panel B reads data/fig1_panelB.csv: the deployed models through their chat interfaces,
the careful subject with the excuse unstated (P0, filled) and stated (P1, open), without
and with reasoning.

Writes figures/out/fig1_bias1.png and figures/out/fig1_bias1_values.csv.
"""
import csv
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from paperlib import (read_csv, num, FAMILY_LABEL, BAND_GREEN,  # noqa: E402
                      BAND_AMBER, BAND_RED)

RED, GREEN, BLUE, GREY = "#c0392b", "#2e7d32", "#2c5f9e", "#555555"
LABEL_B = {
    "claude": "Claude Sonnet 5", "deepseek": "DeepSeek-V4.1 (log-prob)",
    "deepseek_s": "DeepSeek-V4.1 (sampled)", "gemma27b": "Gemma-3-27B",
    "gpt4o": "GPT-4o", "gpt6l_s_bike": "gpt-6-luna", "gpt6s_s_bike": "gpt-6-sol",
    "grok43_s_bike": "grok-4.3", "haiku_s": "Claude Haiku 4.5", "kimi": "Kimi-K3",
    "llama70b": "Llama-3.3-70B", "mistral24b": "Mistral-Small-24B",
    "qwen235b": "Qwen3-235B", "qwen30b": "Qwen3-30B", "qwen80b": "Qwen3-Next-80B",
    "deepseek_r_bike8192_all": "DeepSeek-V4.1 (reasoning)",
    "gemini_r": "Gemini 3.8 Flash (reasoning)",
    "gpt6l_r_bike": "gpt-6-luna (reasoning)", "gpt6s_r_bike": "gpt-6-sol (reasoning)",
    "grok43_r_bike": "grok-4.3 (reasoning)", "haiku_r": "Claude Haiku 4.5 (reasoning)",
}
XMIN, XMAX = -0.25, 1.02


def bands(ax):
    ax.axvspan(XMIN, 0.10, color=BAND_GREEN, zorder=0)
    ax.axvspan(0.10, 0.30, color=BAND_AMBER, zorder=0)
    ax.axvspan(0.30, XMAX, color=BAND_RED, zorder=0)
    ax.set_xlim(XMIN, XMAX)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1])
    ax.set_xticklabels(["0\nblameless", "0.25", "0.5", "0.75", "1\ncareless"])
    ax.set_xlabel("Position on the model's own scale")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def main():
    out = os.path.join(ROOT, "figures", "out")
    os.makedirs(out, exist_ok=True)
    values = []
    fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(14, 8.2),
                                     gridspec_kw={"width_ratios": [1, 1.15]})

    # Panel A
    a = sorted(read_csv("fig1_panelA.csv"), key=lambda r: num(r["P0_pos"]))
    for y, r in enumerate(a):
        p0, lo, hi = num(r["P0_pos"]), num(r["P0_ci_low"]), num(r["P0_ci_high"])
        by = num(r["BYST_pos"])
        col = RED if p0 >= 0.30 else BLUE
        ax_a.plot([by, p0], [y, y], color="#b0b0b0", lw=0.9, zorder=1)
        ax_a.plot([lo, hi], [y, y], color=col, lw=2.6, zorder=2)
        ax_a.plot(p0, y, "o", color=col, ms=8, mec="white", zorder=4)
        ax_a.plot(by, y, "D", mfc="white", mec=GREY, mew=1.4, ms=8, zorder=3)
        if r["gap_clears_2_bands"] == "yes":
            ax_a.text(XMAX + 0.01, y, "✓", color=GREEN, va="center", fontsize=12,
                      clip_on=False)
        values.append(["A", FAMILY_LABEL[r["model"]], "P0", p0, lo, hi])
        values.append(["A", FAMILY_LABEL[r["model"]], "bystander", by, "", ""])
    ax_a.set_yticks(range(len(a)))
    ax_a.set_yticklabels([FAMILY_LABEL[r["model"]] for r in a])
    bands(ax_a)
    ax_a.set_title("A. Pretrained models (worksheet)", loc="left", fontweight="bold")
    ax_a.legend(handles=[
        Line2D([], [], marker="o", ls="", color=RED, ms=8,
               label="careful subject (95% interval)"),
        Line2D([], [], marker="D", ls="", mfc="white", mec=GREY, ms=8,
               label="uninvolved bystander"),
        Line2D([], [], marker="$✓$", ls="", color=GREEN, ms=10,
               label="careful subject > bystander by 2+ bands")],
        loc="upper center", bbox_to_anchor=(0.45, -0.12), frameon=False, fontsize=8.5)

    # Panel B
    b = read_csv("fig1_panelB.csv")
    off = sorted([r for r in b if r["reasoning"] == "off"],
                 key=lambda r: (-num(r["P0_pos"]), LABEL_B[r["model"]].lower()))
    on = sorted([r for r in b if r["reasoning"] == "on"],
                key=lambda r: (-num(r["P0_pos"]), LABEL_B[r["model"]].lower()))
    rows = off + on
    n = len(rows)
    for i, r in enumerate(rows):
        y = n - 1 - i
        p0, p1 = num(r["P0_pos"]), num(r["P1_pos"])
        col = GREEN if r["reasoning"] == "on" else RED
        if abs(p0 - p1) >= 0.03:
            ax_b.annotate("", xy=(p1 + (0.012 if p1 < p0 else -0.012), y),
                          xytext=(p0, y),
                          arrowprops=dict(arrowstyle="-|>", color="#444444", lw=1.3,
                                          shrinkA=4, shrinkB=0))
            ax_b.plot(p1, y, "o", mfc="white", mec="#444444", mew=1.4, ms=8, zorder=4)
            ax_b.plot(p0, y, "o", color=col, ms=8, mec="white", zorder=4)
        else:
            ax_b.plot(p1, y, "o", mfc="white", mec="#444444", mew=1.4, ms=13, zorder=3)
            ax_b.plot(p0, y, "o", color=col, ms=7, mec="white", zorder=4)
        values.append(["B", LABEL_B[r["model"]], "P0", p0, "", ""])
        values.append(["B", LABEL_B[r["model"]], "P1", p1, "", ""])
    ax_b.axhline(len(on) - 0.5, color="#999999", ls="--", lw=0.8)
    ax_b.set_yticks(range(n))
    ax_b.set_yticklabels([LABEL_B[r["model"]] for r in rows][::-1])
    bands(ax_b)
    ax_b.set_title("B. Deployed models (chat): excuse unstated → stated", loc="left",
                   fontweight="bold")
    ax_b.legend(handles=[
        Line2D([], [], marker="o", ls="", color=RED, ms=8,
               label="careful subject, without reasoning"),
        Line2D([], [], marker="o", ls="", color=GREEN, ms=8,
               label="careful subject, with reasoning"),
        Line2D([], [], marker="o", ls="", mfc="white", mec="#444444", ms=8,
               label="excuse stated: \"nothing anyone could have done\"")],
        loc="upper center", bbox_to_anchor=(0.4, -0.12), frameon=False, fontsize=8.5)
    fig.legend(handles=[
        Patch(facecolor=BAND_GREEN, edgecolor="#aaaaaa",
              label="Within one noise band\nof blameless"),
        Patch(facecolor=BAND_AMBER, edgecolor="#aaaaaa", label="One to three\nnoise bands"),
        Patch(facecolor=BAND_RED, edgecolor="#aaaaaa", label="Beyond three\nnoise bands")],
        title="Background", loc="center right", frameon=False, fontsize=8.5)
    fig.subplots_adjust(left=0.09, right=0.84, bottom=0.2, wspace=0.5)
    fig.savefig(os.path.join(out, "fig1_bias1.png"), dpi=150)
    with open(os.path.join(out, "fig1_bias1_values.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["panel", "model", "series", "position", "ci_low", "ci_high"])
        w.writerows(values)
    print(os.path.join(out, "fig1_bias1.png"))


if __name__ == "__main__":
    main()
