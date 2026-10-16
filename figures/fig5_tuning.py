#!/usr/bin/env python3
"""Figure 5: the careful subject's position on each family's pretrained base, with the
study adapter and in the developer's release, on the worksheet (bicycle).

Reads data/B1_tuning_table.csv: base P0 position with its 95% interval (circle), the
study adapter trained on the English corpus (triangle), the developer's release
(square), the base model's uninvolved bystander (diamond), and for Yi the adapter trained
on the Chinese corpus (open triangle, the row flagged is_footnote_row). Markers within a
row are offset vertically for legibility.

Writes figures/out/fig5_tuning.png and figures/out/fig5_tuning_values.csv.
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
from paperlib import (read_csv, num, FAMILY_LABEL, BAND_GREEN, BAND_AMBER,  # noqa
                      BAND_RED)

RED, ORANGE, BLUE, GREY = "#c0392b", "#e08a00", "#2c5f9e", "#555555"
XMIN, XMAX = -0.15, 1.02


def main():
    out = os.path.join(ROOT, "figures", "out")
    os.makedirs(out, exist_ok=True)
    rows = read_csv("B1_tuning_table.csv")
    main_rows = sorted([r for r in rows if r["is_footnote_row"] == "0"],
                       key=lambda r: num(r["base_P0_pos"]))
    zh = {r["family"].split(" ")[0]: r for r in rows if r["is_footnote_row"] == "1"}
    fig, ax = plt.subplots(figsize=(10, 7.6))
    ax.axvspan(XMIN, 0.10, color=BAND_GREEN, zorder=0)
    ax.axvspan(0.10, 0.30, color=BAND_AMBER, zorder=0)
    ax.axvspan(0.30, XMAX, color=BAND_RED, zorder=0)
    values = []
    for y, r in enumerate(main_rows):
        b, lo, hi = num(r["base_P0_pos"]), num(r["base_P0_ci_low"]), num(r["base_P0_ci_high"])
        ad, ins, by = num(r["adapter_P0_pos"]), num(r["instruct_P0_pos"]), num(r["base_BYST_pos"])
        pts = [b, ad, ins, by]
        fam = r["family"]
        if fam in zh:
            pts.append(num(zh[fam]["adapter_P0_pos"]))
        ax.plot([min(pts) - 0.02, max(pts) + 0.02], [y, y], color="#b0b0b0", lw=0.9,
                zorder=1)
        ax.plot([lo, hi], [y + 0.08, y + 0.08], color=RED, lw=2.6, zorder=2)
        ax.plot(b, y + 0.08, "o", color=RED, mec="white", ms=10, zorder=4)
        ax.plot(ad, y + 0.0, "^", color=ORANGE, mec="white", ms=9, zorder=4)
        ax.plot(ins, y - 0.08, "s", color=BLUE, mec="white", ms=8, zorder=4)
        ax.plot(by, y, "D", mfc="white", mec=GREY, mew=1.4, ms=9, zorder=3)
        values += [[FAMILY_LABEL[fam], "base", b, lo, hi],
                   [FAMILY_LABEL[fam], "adapter (English corpus)", ad, "", ""],
                   [FAMILY_LABEL[fam], "developer release", ins, "", ""],
                   [FAMILY_LABEL[fam], "bystander (base)", by, "", ""]]
        if fam in zh:
            z = num(zh[fam]["adapter_P0_pos"])
            ax.plot(z, y, "^", mfc="white", mec=ORANGE, mew=1.8, ms=10, zorder=4)
            values.append([FAMILY_LABEL[fam], "adapter (Chinese corpus)", z, "", ""])
    ax.set_yticks(range(len(main_rows)))
    ax.set_yticklabels([FAMILY_LABEL[r["family"]] for r in main_rows], fontsize=11)
    ax.set_xlim(XMIN, XMAX)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1])
    ax.set_xticklabels(["0\nblameless", "0.25", "0.5", "0.75", "1\ncareless"])
    ax.set_xlabel("Careful subject's position on the model's own scale "
                  "(worksheet, bicycle)")
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.legend(handles=[
        Line2D([], [], marker="o", ls="", color=RED, ms=9,
               label="pretrained base (95% interval)"),
        Line2D([], [], marker="^", ls="", color=ORANGE, ms=9,
               label="+ study adapter (English corpus)"),
        Line2D([], [], marker="^", ls="", mfc="white", mec=ORANGE, ms=9,
               label="+ study adapter (Chinese corpus; Yi only)"),
        Line2D([], [], marker="s", ls="", color=BLUE, ms=8,
               label="developer's instruction-tuned release"),
        Line2D([], [], marker="D", ls="", mfc="white", mec=GREY, ms=8,
               label="uninvolved bystander (base)")],
        loc="upper center", bbox_to_anchor=(0.45, -0.13), ncol=2, frameon=False)
    fig.subplots_adjust(left=0.17, bottom=0.25)
    fig.savefig(os.path.join(out, "fig5_tuning.png"), dpi=150)
    with open(os.path.join(out, "fig5_tuning_values.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["family", "series", "position", "ci_low", "ci_high"])
        w.writerows(values)
    print(os.path.join(out, "fig5_tuning.png"))


if __name__ == "__main__":
    main()
