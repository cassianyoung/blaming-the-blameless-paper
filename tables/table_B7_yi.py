#!/usr/bin/env python3
"""Table B.7: the Yi family.

Panel A reads data/B7_yi_long.csv on the bicycle for Yi-1.5-34B: the base, the study
adapters trained on each corpus, and the developer release, all on the worksheet, with
the change against the base, the change in pooled bands and the rise test verdict.
Panel B reads the same file for the careful subject's position on the three Yi base
models, six scenarios.

The rise test: a rise of more than two pooled bands, more than 0.5 digits and more than
0.10 in position. All three clauses: rises; none: no rise; otherwise partial.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from paperlib import (read_csv, write_table, num, f2, signed,  # noqa: E402
                      SCENARIOS, SCENARIO_LABEL)

PANEL_A = [
    ("base", "Pretrained base", "—"),
    ("adapter_en_s1", "Study adapter", "Shared English corpus"),
    ("adapter_en_s2", "Study adapter", "Shared English corpus"),
    ("adapter_en_s3", "Study adapter", "Shared English corpus"),
    ("adapter_zh", "Study adapter", "Chinese corpus"),
    ("adapter_zh_translated_512", "Study adapter",
     "Chinese corpus translated into English (512 tokens)"),
    ("adapter_zh_translated_2048", "Study adapter",
     "Chinese corpus translated into English (2,048 tokens)"),
    ("adapter_en_no_prose", "Study adapter",
     "English corpus, prose-judgement items replaced"),
    ("release_worksheet", "Developer's release (Yi-1.5-34B-Chat)", "—"),
]
VERDICT = {"RISES": "rises", "NO RISE": "no rise", "__PARTIAL": "partial"}
PANEL_B = [("base_6b", "Yi-1.5-6B"), ("base_9b", "Yi-1.5-9B"), ("base", "Yi-1.5-34B")]


def main():
    rows = read_csv("B7_yi_long.csv")
    cell = {(r["version"], r["scenario"]): r for r in rows}
    ha = ["Version", "Training corpus", "Seed", "Careful subject (P0)", "95% interval",
          "Change vs base", "Δ in bands", "Rise test"]
    out = []
    for v, label, corpus in PANEL_A:
        r = cell[(v, "bicycle")]
        lo, hi = num(r["P0_ci_low"]), num(r["P0_ci_high"])
        ci = "—" if lo is None else f"{f2(lo)}–{f2(hi)}"
        if v == "base":
            out.append([label, corpus, "—", f2(num(r["P0_pos"])), ci, "—", "—", "—"])
            continue
        out.append([label, corpus, r["seed"] or "—", f2(num(r["P0_pos"])), ci,
                    signed(num(r["delta_pos_vs_base"])),
                    f2(num(r["delta_bands_vs_base"]), 1),
                    VERDICT.get(r["rise_verdict"], r["rise_verdict"])])
    print(write_table("table_B7A_yi_34b", ha, out))
    hb = ["Base model"] + [SCENARIO_LABEL[s] for s in SCENARIOS]
    outb = [[label] + [f2(num(cell[(v, s)]["P0_pos"])) for s in SCENARIOS]
            for v, label in PANEL_B]
    print(write_table("table_B7B_yi_sizes", hb, outb))


if __name__ == "__main__":
    main()
