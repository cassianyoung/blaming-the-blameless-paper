#!/usr/bin/env python3
"""Table B.3: the same instruct weights, worksheet against chat, bicycle, eight families.

Reads data/frame_table_bicycle.csv (one row per family) and data/frame_table_summary.csv
(the two summary rows). A family whose chat reading fails the chat gate is marked '*'.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from paperlib import (read_csv, write_table, num, f2, signed,  # noqa: E402
                      FAMILY_LABEL)

HEADER = ["Family", "Worksheet N", "Chat N", "Floor shift", "Worksheet P0 pos.",
          "Chat P0 pos.", "Δ pos.", "ρ, worksheet vs chat", "Chat gate (N mass 0–3)"]


def main():
    out = []
    for r in read_csv("frame_table_bicycle.csv"):
        failed = r["chat_gate"] != "PASSED"
        out.append([FAMILY_LABEL[r["family"]] + (" *" if failed else ""),
                    f2(num(r["ws_N"])), f2(num(r["chat_N"])),
                    signed(num(r["floor_shift_digits"])), f2(num(r["ws_P0_pos"])),
                    f2(num(r["chat_P0_pos"])), signed(num(r["delta_pos"])),
                    f2(num(r["spearman_rho_ws_vs_chat"])),
                    f"{'fail' if failed else 'pass'} ({f2(num(r['chat_N_mass_0_3']))})"])
    summ = {}
    for r in read_csv("frame_table_summary.csv"):
        summ[(r["scope"], r["statistic"])] = r["value"]
    for scope, label in (("all rows", "Summary, all"),
                         ("chat gate PASSED", "Summary, gate passed")):
        g = lambda k: summ[(scope, k)]  # noqa: E731
        up = int(g("floor moves beyond +0.30 digits (up)"))
        dn = int(g("floor moves beyond -0.30 digits (down)"))
        lo, hi = g("rho range").split(" to ")
        out.append([f"{label} ({g('n rows')})", "", "",
                    f"moves on {up + dn}: {up} up, {dn} down", "", "",
                    f"{f2(num(g('mean unsigned delta_pos')))} mean unsigned",
                    f"median {f2(num(g('rho median')))} ({f2(num(lo))}–{f2(num(hi))})",
                    ""])
    notes = ["* Fails the chat gate (blameless mass on 0–3 below 0.8); shown, enters "
             "no result. StableLM 2's chat release could not be scored."]
    print(write_table("table_B3_frames", HEADER, out, notes))


if __name__ == "__main__":
    main()
